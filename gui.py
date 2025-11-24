import sys
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import downloader

class DownloadWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            path = downloader.download_gif(self.url)
            self.finished.emit(path)
        except Exception as e:
            self.error.emit(str(e))

class DropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GIF Drop")
        self.setGeometry(100, 100, 400, 300)
        self.setAcceptDrops(True)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel("Drag & Drop a Tenor GIF link here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; color: #555; border: 2px dashed #aaa; border-radius: 10px; padding: 20px;")
        self.layout.addWidget(self.label)

        self.footer = QLabel("created by shahid | @shahidgrows")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setStyleSheet("font-size: 10px; color: #888; margin-top: 10px;")
        self.layout.addWidget(self.footer)

        self.support_label = QLabel("Currently only tested / supports Tenor")
        self.support_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.support_label.setStyleSheet("font-size: 10px; color: #aaa; margin-top: 2px;")
        self.layout.addWidget(self.support_label)

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

    def start_download(self, url):
        self.label.setText("Downloading...")
        self.label.setStyleSheet("font-size: 18px; color: #0078d7; border: 2px solid #0078d7; border-radius: 10px; padding: 20px;")
        
        self.worker = DownloadWorker(url)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.error.connect(self.on_download_error)
        self.worker.start()

    def on_download_finished(self, path):
        self.label.setText(f"Saved to:\n{path}")
        self.label.setStyleSheet("font-size: 14px; color: green; border: 2px solid green; border-radius: 10px; padding: 20px;")
        # Reset after a few seconds? Or just leave it.

    def on_download_error(self, error_msg):
        self.label.setText(f"Error:\n{error_msg}")
        self.label.setStyleSheet("font-size: 14px; color: red; border: 2px solid red; border-radius: 10px; padding: 20px;")
