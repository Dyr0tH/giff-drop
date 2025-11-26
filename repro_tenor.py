import downloader
import sys

url = "https://tenor.com/view/cat-typing-laptop-work-gif-25346860"
print(f"Testing URL: {url}")

try:
    path = downloader.download_media(url)
    print(f"Success: {path}")
except Exception as e:
    print(f"Failed: {e}")
