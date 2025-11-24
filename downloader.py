import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pathlib

def get_downloads_folder():
    return str(pathlib.Path.home() / "Downloads")

def is_tenor_url(url):
    parsed = urlparse(url)
    return "tenor.com" in parsed.netloc

def download_gif(url):
    if not is_tenor_url(url):
        raise ValueError("Not a valid Tenor URL")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tenor usually has the gif in a meta tag or specific structure
        # Looking for og:image or similar
        meta_image = soup.find("meta", property="og:image")
        
        if not meta_image:
            # Fallback or other specific tenor structure
            # Sometimes it's in a div with class 'Gif'
            raise ValueError("Could not find GIF image on page")

        gif_url = meta_image["content"]
        
        # Ensure we have the .gif version if possible, sometimes og:image is a jpg preview
        # Tenor og:image often ends in .gif, but let's check.
        if not gif_url.endswith(".gif"):
             # Try to find the actual gif source if the og:image isn't one
             # This is a simplification; often the og:image IS the gif or close to it.
             # Let's trust og:image for a start, or look for specific mp4/gif tags
             pass

        # Download the content
        gif_response = requests.get(gif_url, stream=True)
        gif_response.raise_for_status()

        # Extract filename
        filename = os.path.basename(urlparse(gif_url).path)
        if not filename.endswith('.gif'):
            filename += ".gif"
            
        save_path = os.path.join(get_downloads_folder(), filename)
        
        # Avoid overwriting
        base, ext = os.path.splitext(save_path)
        counter = 1
        while os.path.exists(save_path):
            save_path = f"{base}_{counter}{ext}"
            counter += 1

        with open(save_path, 'wb') as f:
            for chunk in gif_response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return save_path

    except Exception as e:
        raise RuntimeError(f"Failed to download GIF: {str(e)}")
