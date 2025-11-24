import downloader
import os

def test_downloader():
    # A known safe Tenor GIF URL
    tenor_url = "https://tenor.com/view/hello-bear-waving-hi-gif-26109328"
    
    # A generic image URL (Google logo)
    image_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"

    # A short YouTube video (e.g., a 1-second test video or similar)
    # Using a very short video to save time and bandwidth
    youtube_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw" # "Me at the zoo" - first YT video, 18s

    print("Testing Tenor Download...")
    try:
        path = downloader.download_media(tenor_url)
        print(f"Success: {path}")
        if os.path.exists(path): os.remove(path)
    except Exception as e:
        print(f"Tenor Failed: {e}")

    print("\nTesting Image Download...")
    try:
        path = downloader.download_media(image_url)
        print(f"Success: {path}")
        if os.path.exists(path): os.remove(path)
    except Exception as e:
        print(f"Image Failed: {e}")

    print("\nTesting YouTube Resolution Fetching...")
    try:
        resolutions = downloader.get_youtube_resolutions(youtube_url)
        print(f"Resolutions: {resolutions}")
    except Exception as e:
        print(f"Resolution Fetch Failed: {e}")

    print("\nTesting YouTube Download (Video+Audio) to Custom Folder...")
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdirname:
            print(f"Downloading to temporary folder: {tmpdirname}")
            path = downloader.download_youtube(youtube_url, audio_only=False, output_folder=tmpdirname)
            print(f"Success: {path}")
            if os.path.dirname(path) != tmpdirname:
                print(f"Error: File not saved to custom folder. Saved to: {path}")
    except Exception as e:
        print(f"YouTube Video Failed: {e}")

    print("\nTesting YouTube Download (Audio Only)...")
    try:
        path = downloader.download_youtube(youtube_url, audio_only=True)
        print(f"Success: {path}")
        if os.path.exists(path): os.remove(path)
    except Exception as e:
        print(f"YouTube Audio Failed: {e}")

if __name__ == "__main__":
    test_downloader()
