import downloader
import os

def test_downloader():
    # A known safe Tenor GIF URL (just a random one from search)
    # This might fail if the URL changes or is invalid, but it's a good smoke test.
    # Using a generic search page might be harder to parse if I logic-ed for specific gif pages.
    # Let's use a specific GIF page.
    test_url = "https://tenor.com/view/hello-bear-waving-hi-gif-26109328"

    print(f"Testing download from: {test_url}")
    try:
        path = downloader.download_gif(test_url)
        print(f"Successfully downloaded to: {path}")
        
        if os.path.exists(path):
            print("File exists.")
            # Clean up
            os.remove(path)
            print("Test file removed.")
        else:
            print("Error: File does not exist after download.")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_downloader()
