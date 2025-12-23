# GIF Drop

**GIF Drop** is a versatile media downloader application built with Python and PyQt6. It allows you to easily download GIFs, videos, and images from various platforms including Tenor, YouTube, Instagram, and Pinterest.

## Features

*   **Universal Drag & Drop:** simply drag and drop links from Tenor or direct image URLs to download them instantly.
*   **Tenor Search:** Dedicated tab to browse trending GIFs or search for specific ones. One-click download.
*   **YouTube Downloader:**
    *   Download Videos (H.264 MP4) or Audio Only (MP3).
    *   Select specific video resolutions.
*   **Instagram Downloader:**
    *   Download Reels and Videos.
    *   Option for Audio Only downloads.
*   **Pinterest Downloader:**
    *   Download Images and Videos from Pinterest posts.
*   **Custom Download Folder:** Choose where your files are saved.
*   **Modern GUI:** Clean and easy-to-use interface with dark mode styling.

## Installation

### Prerequisites

*   Python 3.8 or higher
*   [FFmpeg](https://ffmpeg.org/download.html) (Required for media merging and conversion)

### Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/gif-drop.git
    cd gif-drop
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the application:
    ```bash
    python main.py
    ```

2.  **Home Tab:**
    *   **Drag & Drop:** Drag a link from a browser and drop it onto the drop zone.
    *   **Buttons:** Use the dedicated buttons to open dialogs for YouTube, Instagram, or Pinterest downloads.
    *   **Change Folder:** Click "Change Download Folder" to set your preferred save location.

3.  **Tenor Search Tab:**
    *   Browse trending GIFs or use the search bar.
    *   Click "Download" on any GIF to save it.

## Building Executable

To create a standalone Windows executable:

1.  Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```

2.  Run the build command:
    ```bash
    pyinstaller --noconfirm --onefile --windowed --name "GIF Drop" --add-data "downloader.py;." --add-data "gui.py;." main.py
    ```

3.  The executable will be located in the `dist` folder.

## Technologies Used

*   **Python**
*   **PyQt6** (GUI Framework)
*   **yt-dlp** (Media downloading engine)
*   **BeautifulSoup4** (Web scraping)
*   **Requests** (HTTP requests)

## License

[MIT License](LICENSE)
