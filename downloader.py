import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pathlib
import yt_dlp
import imageio_ffmpeg
import yt_dlp
import imageio_ffmpeg
import mimetypes
import json

TENOR_API_KEY = "AIzaSyDjT2-90qrVFPfLfvZO8YicG4HPqrzq-8E"
TENOR_CLIENT_KEY = "GIF_DROP_APP"

def get_tenor_trending(limit=20):
    url = f"https://tenor.googleapis.com/v2/featured?key={TENOR_API_KEY}&client_key={TENOR_CLIENT_KEY}&limit={limit}&media_filter=gif,tinygif"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = json.loads(response.content)
        return _parse_tenor_results(data)
    except Exception as e:
        print(f"Tenor Trending Error: {e}")
        return []

def search_tenor(query, limit=20):
    url = f"https://tenor.googleapis.com/v2/search?q={query}&key={TENOR_API_KEY}&client_key={TENOR_CLIENT_KEY}&limit={limit}&media_filter=gif,tinygif"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = json.loads(response.content)
        return _parse_tenor_results(data)
    except Exception as e:
        print(f"Tenor Search Error: {e}")
        return []

def _parse_tenor_results(data):
    results = []
    for result in data.get('results', []):
        media = result.get('media_formats', {})
        gif_url = media.get('gif', {}).get('url')
        tinygif_url = media.get('tinygif', {}).get('url') # For preview
        
        if gif_url:
            results.append({
                'id': result.get('id'),
                'title': result.get('content_description', 'GIF'),
                'full_url': gif_url,
                'preview_url': tinygif_url or gif_url
            })
    return results

def get_downloads_folder():
    return str(pathlib.Path.home() / "Downloads")

def is_tenor_url(url):
    parsed = urlparse(url)
    return "tenor.com" in parsed.netloc

def get_youtube_resolutions(url):
    try:
        ydl_opts = {'noplaylist': True, 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            resolutions = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    resolutions.add(f['height'])
            return sorted(list(resolutions), reverse=True)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch resolutions: {str(e)}")

def download_youtube(url, audio_only=False, resolution=None, output_folder=None, audio_codec='mp3', video_codec='default'):
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        target_folder = output_folder if output_folder else get_downloads_folder()

        ydl_opts = {
            'outtmpl': os.path.join(target_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'ffmpeg_location': ffmpeg_exe,
        }
        
        if audio_only:
            # Map friendly names to yt-dlp codecs
            acodec = 'mp3'
            if audio_codec == 'aac':
                acodec = 'm4a' # yt-dlp uses m4a for aac container usually
            
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': acodec,
                    'preferredquality': '192',
                }],
            })
        else:
            # Video + Audio
            # Base format string
            format_str = 'bestvideo'
            
            if video_codec == 'h264':
                # Prefer AVC1 (H.264)
                format_str += '[vcodec^=avc1]'
            
            if resolution:
                format_str += f'[height={resolution}]'
            
            # Add audio and fallback
            format_str += '+bestaudio/best'
            
            ydl_opts.update({
                'format': format_str,
                'merge_output_format': 'mp4',
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if audio_only:
                base, _ = os.path.splitext(filename)
                # Check for the actual extension we asked for
                ext = 'mp3' if audio_codec == 'mp3' else 'm4a'
                final_path = f"{base}.{ext}"
                if os.path.exists(final_path):
                    filename = final_path
                
            return filename

    except Exception as e:
        raise RuntimeError(f"Failed to download YouTube video: {str(e)}")

def download_instagram(url, audio_only=False, output_folder=None):
    # Reuse YouTube logic as yt-dlp handles Instagram well
    return download_youtube(url, audio_only=audio_only, output_folder=output_folder)

def download_pinterest(url, output_folder=None):
    try:
        # Try yt-dlp first (best for videos)
        print(f"Attempting Pinterest download with yt-dlp: {url}")
        return download_youtube(url, output_folder=output_folder)
    except Exception as e:
        print(f"yt-dlp failed for Pinterest ({e}), falling back to scraper...")
        # Fallback to universal scraper (best for images)
        return download_media(url, output_folder=output_folder)

def download_media(url, output_folder=None):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Check content type without downloading everything first
        print(f"Checking URL: {url}")
        try:
            head_response = requests.head(url, headers=headers, allow_redirects=True)
            print(f"HEAD Status: {head_response.status_code}")
            content_type = head_response.headers.get('content-type', '').lower()
        except Exception as e:
            print(f"HEAD failed: {e}")
            # If HEAD fails, try GET with stream
            head_response = requests.get(url, headers=headers, stream=True)
            print(f"GET Status: {head_response.status_code}")
            content_type = head_response.headers.get('content-type', '').lower()
            head_response.close()
        
        print(f"Content-Type: {content_type}")

        if 'text/html' in content_type:
            print(f"Detected HTML page, scraping: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Strategy 1: Open Graph / Twitter Tags
            og_video = soup.find("meta", attrs={"property": "og:video"})
            og_image = soup.find("meta", attrs={"property": "og:image"})
            twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
            
            target_url = None
            if og_video and og_video.get("content"):
                target_url = og_video["content"]
            elif og_image and og_image.get("content"):
                target_url = og_image["content"]
            elif twitter_image and twitter_image.get("content"):
                target_url = twitter_image["content"]
            
            if target_url:
                print(f"Found media via scraping: {target_url}")
                return download_media(target_url, output_folder)
            else:
                print("No OG tags found.")
                # Strategy 2: Try yt-dlp for generic video sites
                print("No metadata found, trying generic yt-dlp download...")
                return download_youtube(url, output_folder=output_folder)

        # If we are here, it should be a direct media file
        media_url = url
        media_response = requests.get(media_url, headers=headers, stream=True)
        media_response.raise_for_status()
        content_type = media_response.headers.get('content-type', '').lower()
        
        # Extract filename
        parsed_url = urlparse(media_url)
        filename = os.path.basename(parsed_url.path)
        
        # If filename is empty (e.g. root URL), use a default
        if not filename:
            filename = "download"

        # Check if we need to add an extension
        root, ext = os.path.splitext(filename)
        if not ext:
            # Try to guess from Content-Type
            mime_type = content_type.split(';')[0].strip()
            guessed_ext = mimetypes.guess_extension(mime_type)
            
            if guessed_ext:
                if guessed_ext == '.jpe': guessed_ext = '.jpg'
                filename += guessed_ext
            else:
                # Manual fallback
                if 'image/jpeg' in mime_type:
                    filename += '.jpg'
                elif 'image/png' in mime_type:
                    filename += '.png'
                elif 'image/gif' in mime_type:
                    filename += '.gif'
                elif 'image/webp' in mime_type:
                    filename += '.webp'
                else:
                    filename += '.download'

        target_folder = output_folder if output_folder else get_downloads_folder()
        save_path = os.path.join(target_folder, filename)
        
        base, ext = os.path.splitext(save_path)
        counter = 1
        while os.path.exists(save_path):
            save_path = f"{base}_{counter}{ext}"
            counter += 1

        with open(save_path, 'wb') as f:
            for chunk in media_response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return save_path

    except Exception as e:
        raise RuntimeError(f"Failed to download media: {str(e)}")
