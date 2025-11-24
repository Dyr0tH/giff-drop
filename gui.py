from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox, QPushButton, QDialog, QLineEdit, QRadioButton, QButtonGroup, QHBoxLayout, QProgressBar, QComboBox, QFileDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import downloader
import os

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

    def __init__(self, url, is_youtube=False, audio_only=False, resolution=None, output_folder=None):
        super().__init__()
        self.url = url
        self.is_youtube = is_youtube
        self.audio_only = audio_only
        self.resolution = resolution
        self.output_folder = output_folder

    def run(self):
        try:
            if self.is_youtube:
                path = downloader.download_youtube(self.url, self.audio_only, self.resolution, self.output_folder)
            else:
                path = downloader.download_media(self.url, self.output_folder)
            self.finished.emit(path)
        except Exception as e:
            self.error.emit(str(e))

class YouTubeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download YouTube Video")
        self.setFixedWidth(350)
        
        layout = QVBoxLayout(self)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here...")
        layout.addWidget(self.url_input)
        
        self.fetch_btn = QPushButton("Fetch Resolutions")
        self.fetch_btn.clicked.connect(self.fetch_resolutions)
        layout.addWidget(self.fetch_btn)
        
        self.format_group = QButtonGroup(self)
        
        self.video_radio = QRadioButton("Video + Audio")
        self.video_radio.setChecked(True)
        self.video_radio.toggled.connect(self.toggle_resolution_combo)
        layout.addWidget(self.video_radio)
        self.format_group.addButton(self.video_radio)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.setEnabled(False)
        self.resolution_combo.addItem("Best Available")
        layout.addWidget(self.resolution_combo)
        
        self.audio_radio = QRadioButton("Audio Only")
        self.audio_radio.toggled.connect(self.toggle_resolution_combo)
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

    def toggle_resolution_combo(self):
        self.resolution_combo.setEnabled(self.video_radio.isChecked() and bool(self.resolutions))

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
            
        if self.video_radio.isChecked():
            self.resolution_combo.setEnabled(True)
            
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
        return url, audio_only, resolution

class DropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GIF Drop")
        self.setGeometry(100, 100, 400, 400)
        self.setAcceptDrops(True)
        
        self.download_folder = None # Default to None (let downloader handle default)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel("Drag & Drop a Tenor GIF or Image link here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; color: #555; border: 2px dashed #aaa; border-radius: 10px; padding: 20px;")
        self.layout.addWidget(self.label)
        
        self.yt_btn = QPushButton("Download YouTube Video")
        self.yt_btn.setStyleSheet("padding: 10px; font-size: 14px;")
        self.yt_btn.clicked.connect(self.open_youtube_dialog)
        self.layout.addWidget(self.yt_btn)
        
        self.folder_btn = QPushButton("Change Download Folder")
        self.folder_btn.setStyleSheet("padding: 8px; font-size: 12px; margin-top: 5px;")
        self.folder_btn.clicked.connect(self.select_download_folder)
        self.layout.addWidget(self.folder_btn)

        self.footer = QLabel("created by shahid | @shahidgrows")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setStyleSheet("font-size: 10px; color: #888; margin-top: 10px;")
        self.layout.addWidget(self.footer)

        self.support_label = QLabel("Supports Tenor GIFs, Images, and YouTube")
        self.support_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.support_label.setStyleSheet("font-size: 10px; color: #aaa; margin-top: 2px;")
        self.layout.addWidget(self.support_label)

    def select_download_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.download_folder = folder
            QMessageBox.information(self, "Folder Selected", f"Downloads will be saved to:\n{folder}")

    def open_youtube_dialog(self):
        dialog = YouTubeDialog(self)
        if dialog.exec():
            url, audio_only, resolution = dialog.get_data()
            if url:
                self.start_download(url, is_youtube=True, audio_only=audio_only, resolution=resolution)

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
            self.start_download(url)

    def start_download(self, url, is_youtube=False, audio_only=False, resolution=None):
        self.label.setText("Downloading...")
        self.label.setStyleSheet("font-size: 18px; color: #0078d7; border: 2px solid #0078d7; border-radius: 10px; padding: 20px;")
        
        self.worker = DownloadWorker(url, is_youtube, audio_only, resolution, self.download_folder)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_download_error)
        self.worker.start()

    def on_download_finished(self, path):
        self.label.setText(f"Saved to:\n{path}")
        self.label.setStyleSheet("font-size: 14px; color: green; border: 2px solid green; border-radius: 10px; padding: 20px;")

    def on_download_error(self, error_msg):
        self.label.setText(f"Error:\n{error_msg}")
        self.label.setStyleSheet("font-size: 14px; color: red; border: 2px solid red; border-radius: 10px; padding: 20px;")
