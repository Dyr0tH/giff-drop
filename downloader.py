import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pathlib
import yt_dlp
import imageio_ffmpeg

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

def download_youtube(url, audio_only=False, resolution=None, output_folder=None):
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        target_folder = output_folder if output_folder else get_downloads_folder()

        ydl_opts = {
            'outtmpl': os.path.join(target_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'ffmpeg_location': ffmpeg_exe,
        }
        
        if audio_only:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            if resolution:
                ydl_opts.update({
                    'format': f'bestvideo[height={resolution}]+bestaudio/best[height={resolution}]/best',
                })
            else:
                ydl_opts.update({
                    'format': 'bestvideo+bestaudio/best',
                })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if audio_only:
                base, _ = os.path.splitext(filename)
                mp3_path = f"{base}.mp3"
                if os.path.exists(mp3_path):
                    filename = mp3_path
                
            return filename

    except Exception as e:
        raise RuntimeError(f"Failed to download YouTube video: {str(e)}")

def download_media(url, output_folder=None):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        if is_tenor_url(url):
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_image = soup.find("meta", property="og:image")
            if not meta_image:
                raise ValueError("Could not find GIF image on Tenor page")
            media_url = meta_image["content"]
        else:
            media_url = url

        media_response = requests.get(media_url, headers=headers, stream=True)
        media_response.raise_for_status()
        
        content_type = media_response.headers.get('content-type', '')
        
        if 'image' not in content_type and 'video' not in content_type and not is_tenor_url(url):
             pass

        parsed_url = urlparse(media_url)
        filename = os.path.basename(parsed_url.path)
        
        if not os.path.splitext(filename)[1]:
            if 'image/jpeg' in content_type:
                filename += '.jpg'
            elif 'image/png' in content_type:
                filename += '.png'
            elif 'image/gif' in content_type:
                filename += '.gif'
            elif 'image/webp' in content_type:
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
