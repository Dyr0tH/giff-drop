from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox, 
                             QPushButton, QDialog, QLineEdit, QRadioButton, QButtonGroup, 
                             QHBoxLayout, QProgressBar, QComboBox, QFileDialog, QTabWidget,
                             QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
import downloader
import os
import requests

class ResolutionFetcher(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            resolutions = downloader.get_youtube_resolutions(self.url)
            self.finished.emit(resolutions)
        except Exception as e:
            self.error.emit(str(e))

class DownloadWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, is_youtube=False, is_instagram=False, is_pinterest=False, audio_only=False, resolution=None, output_folder=None, audio_codec='mp3', video_codec='default'):
        super().__init__()
        self.url = url
        self.is_youtube = is_youtube
        self.is_instagram = is_instagram
        self.is_pinterest = is_pinterest
        self.audio_only = audio_only
        self.resolution = resolution
        self.output_folder = output_folder
        self.audio_codec = audio_codec
        self.video_codec = video_codec

    def run(self):
        try:
            if self.is_youtube:
                path = downloader.download_youtube(self.url, self.audio_only, self.resolution, self.output_folder, self.audio_codec, self.video_codec)
            elif self.is_instagram:
                path = downloader.download_instagram(self.url, self.audio_only, self.output_folder)
            elif self.is_pinterest:
                path = downloader.download_pinterest(self.url, self.output_folder)
            else:
                path = downloader.download_media(self.url, self.output_folder)
            self.finished.emit(path)
        except Exception as e:
            self.error.emit(str(e))

class TenorFetcher(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, query=None):
        super().__init__()
        self.query = query

    def run(self):
        try:
            if self.query:
                results = downloader.search_tenor(self.query)
            else:
                results = downloader.get_tenor_trending()
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class ImageLoader(QThread):
    finished = pyqtSignal(bytes, str) # data, url

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.finished.emit(response.content, self.url)
        except:
            pass

class YouTubeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download YouTube Video")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here...")
        layout.addWidget(self.url_input)
        
        self.fetch_btn = QPushButton("Fetch Resolutions")
        self.fetch_btn.clicked.connect(self.fetch_resolutions)
        layout.addWidget(self.fetch_btn)
        
        # Format Selection
        self.format_group = QButtonGroup(self)
        
        self.video_radio = QRadioButton("Video + Audio")
        self.video_radio.setChecked(True)
        self.video_radio.toggled.connect(self.update_ui_state)
        layout.addWidget(self.video_radio)
        self.format_group.addButton(self.video_radio)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.setEnabled(False)
        self.resolution_combo.addItem("Best Available")
        layout.addWidget(self.resolution_combo)
        
        self.audio_radio = QRadioButton("Audio Only")
        self.audio_radio.toggled.connect(self.update_ui_state)
        layout.addWidget(self.audio_radio)
        self.format_group.addButton(self.audio_radio)
        
        btn_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.accept)
        self.download_btn.setEnabled(True)
        btn_layout.addWidget(self.download_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.resolutions = []
        self.update_ui_state()

    def update_ui_state(self):
        is_video = self.video_radio.isChecked()
        has_resolutions = bool(self.resolutions)
        
        self.resolution_combo.setEnabled(is_video and has_resolutions)

    def fetch_resolutions(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL first.")
            return
            
        self.fetch_btn.setText("Fetching...")
        self.fetch_btn.setEnabled(False)
        
        self.fetcher = ResolutionFetcher(url)
        self.fetcher.finished.connect(self.on_resolutions_fetched)
        self.fetcher.error.connect(self.on_fetch_error)
        self.fetcher.start()

    def on_resolutions_fetched(self, resolutions):
        self.fetch_btn.setText("Fetch Resolutions")
        self.fetch_btn.setEnabled(True)
        self.resolutions = resolutions
        
        self.resolution_combo.clear()
        self.resolution_combo.addItem("Best Available")
        for res in resolutions:
            self.resolution_combo.addItem(f"{res}p", res)
            
        self.update_ui_state()
            
        QMessageBox.information(self, "Success", f"Found {len(resolutions)} resolutions.")

    def on_fetch_error(self, error):
        self.fetch_btn.setText("Fetch Resolutions")
        self.fetch_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Failed to fetch resolutions: {error}")

    def get_data(self):
        url = self.url_input.text()
        audio_only = self.audio_radio.isChecked()
        resolution = None
        if not audio_only and self.resolution_combo.currentIndex() > 0:
            resolution = self.resolution_combo.currentData()
            
        # Hardcoded defaults as per user request
        audio_codec = 'mp3' 
        video_codec = 'h264'
        
        return url, audio_only, resolution, audio_codec, video_codec

class InstagramDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Instagram Video")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Instagram URL here...")
        layout.addWidget(self.url_input)
        
        self.format_group = QButtonGroup(self)
        
        self.video_radio = QRadioButton("Video + Audio")
        self.video_radio.setChecked(True)
        layout.addWidget(self.video_radio)
        self.format_group.addButton(self.video_radio)
        
        self.audio_radio = QRadioButton("Audio Only")
        layout.addWidget(self.audio_radio)
        self.format_group.addButton(self.audio_radio)
        
        btn_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.download_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)

    def get_data(self):
        url = self.url_input.text()
        audio_only = self.audio_radio.isChecked()
        return url, audio_only

class PinterestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Pinterest Media")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Pinterest URL here...")
        layout.addWidget(self.url_input)
        
        btn_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.download_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)

    def get_data(self):
        return self.url_input.text()

class HomeTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Drag & Drop a Tenor GIF or Image link here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; color: #555; border: 2px dashed #aaa; border-radius: 10px; padding: 20px;")
        self.layout.addWidget(self.label)
        
        self.yt_btn = QPushButton("Download YouTube Video")
        self.yt_btn.setStyleSheet("padding: 10px; font-size: 14px;")
        self.yt_btn.clicked.connect(self.open_youtube_dialog)
        self.layout.addWidget(self.yt_btn)
        
        self.insta_btn = QPushButton("Download Instagram Video")
        self.insta_btn.setStyleSheet("padding: 10px; font-size: 14px; margin-top: 5px;")
        self.insta_btn.clicked.connect(self.open_instagram_dialog)
        self.layout.addWidget(self.insta_btn)

        self.pin_btn = QPushButton("Download Pinterest Media")
        self.pin_btn.setStyleSheet("padding: 10px; font-size: 14px; margin-top: 5px;")
        self.pin_btn.clicked.connect(self.open_pinterest_dialog)
        self.layout.addWidget(self.pin_btn)
        
        self.folder_btn = QPushButton("Change Download Folder")
        self.folder_btn.setStyleSheet("padding: 8px; font-size: 12px; margin-top: 5px;")
        self.folder_btn.clicked.connect(self.select_download_folder)
        self.layout.addWidget(self.folder_btn)

        self.footer = QLabel("created by Shahid | @shahidgrows")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setStyleSheet("font-size: 20px; color: #888; margin-top: 10px;")
        self.layout.addWidget(self.footer)

        self.support_label = QLabel("Supports Tenor GIFs, Images, YouTube, Instagram, and Pinterest")
        self.support_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.support_label.setStyleSheet("font-size: 15px; color: #aaa; margin-top: 2px;")
        self.layout.addWidget(self.support_label)

    def select_download_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.main_window.download_folder = folder
            QMessageBox.information(self, "Folder Selected", f"Downloads will be saved to:\n{folder}")

    def open_youtube_dialog(self):
        dialog = YouTubeDialog(self)
        if dialog.exec():
            url, audio_only, resolution, audio_codec, video_codec = dialog.get_data()
            if url:
                self.main_window.start_download(url, is_youtube=True, audio_only=audio_only, resolution=resolution, audio_codec=audio_codec, video_codec=video_codec)

    def open_instagram_dialog(self):
        dialog = InstagramDialog(self)
        if dialog.exec():
            url, audio_only = dialog.get_data()
            if url:
                self.main_window.start_download(url, is_instagram=True, audio_only=audio_only)

    def open_pinterest_dialog(self):
        dialog = PinterestDialog(self)
        if dialog.exec():
            url = dialog.get_data()
            if url:
                self.main_window.start_download(url, is_pinterest=True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        url = ""
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toString()
        elif event.mimeData().hasText():
            url = event.mimeData().text()
        
        if url:
            self.main_window.start_download(url)
            
    def update_status(self, message, is_error=False):
        self.label.setText(message)
        color = "red" if is_error else "green"
        if message == "Downloading...": color = "#0078d7"
        self.label.setStyleSheet(f"font-size: 14px; color: {color}; border: 2px solid {color}; border-radius: 10px; padding: 20px;")

class GifWidget(QWidget):
    def __init__(self, gif_data, main_window):
        super().__init__()
        self.gif_data = gif_data
        self.main_window = main_window
        self.setFixedSize(160, 180)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.image_label = QLabel("Loading...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #eee; border-radius: 5px;")
        self.image_label.setFixedSize(150, 130)
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)
        
        self.download_btn = QPushButton("Download")
        self.download_btn.setStyleSheet("font-size: 10px; padding: 4px;")
        self.download_btn.clicked.connect(self.download_gif)
        layout.addWidget(self.download_btn)
        
        # Load image
        self.loader = ImageLoader(gif_data['preview_url'])
        self.loader.finished.connect(self.on_image_loaded)
        self.loader.start()
        
    def on_image_loaded(self, data, url):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.image_label.setPixmap(pixmap)
        self.image_label.setText("")
        
    def download_gif(self):
        self.main_window.start_download(self.gif_data['full_url'])
        QMessageBox.information(self.main_window, "Download Started", "Download started in background.")

class TenorTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        
        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Tenor GIFs...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)
        
        # Scroll Area for Results
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)
        
        # Load Trending initially
        self.load_trending()
        
    def load_trending(self):
        self.fetcher = TenorFetcher()
        self.fetcher.finished.connect(self.display_results)
        self.fetcher.start()
        
    def perform_search(self):
        query = self.search_input.text()
        if not query: return
        
        # Clear grid
        self.clear_grid()
        
        self.fetcher = TenorFetcher(query)
        self.fetcher.finished.connect(self.display_results)
        self.fetcher.start()
        
    def clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
    def display_results(self, results):
        self.clear_grid()
        row = 0
        col = 0
        max_cols = 3 # 3 columns grid
        
        for gif in results:
            widget = GifWidget(gif, self.main_window)
            self.grid_layout.addWidget(widget, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

class DropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GIF Drop")
        self.setGeometry(100, 100, 550, 600) # Increased size for Tabs
        
        self.download_folder = None 

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.home_tab = HomeTab(self)
        self.tabs.addTab(self.home_tab, "Home")
        
        self.tenor_tab = TenorTab(self)
        self.tabs.addTab(self.tenor_tab, "Tenor Search")

    def start_download(self, url, is_youtube=False, is_instagram=False, is_pinterest=False, audio_only=False, resolution=None, audio_codec='mp3', video_codec='default'):
        # Switch to home tab to show status
        # self.tabs.setCurrentWidget(self.home_tab) 
        # Actually, maybe just show a toast or status bar? 
        # For now, let's update the home tab label as that's where the status logic is.
        
        self.home_tab.update_status("Downloading...")
        
        self.worker = DownloadWorker(url, is_youtube, is_instagram, is_pinterest, audio_only, resolution, self.download_folder, audio_codec, video_codec)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_download_error)
        self.worker.start()

    def on_download_finished(self, path):
        self.home_tab.update_status(f"Saved to:\n{path}")

    def on_download_error(self, error_msg):
        self.home_tab.update_status(f"Error:\n{error_msg}", is_error=True)
