import sys
import os
import threading
import requests
import webbrowser
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QFileDialog, QComboBox, QStackedWidget, QListWidget, QCheckBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
import json
from datetime import datetime

def sanitize_filename(filename):
    invalid_chars = r'\/:*?"<>|'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

logging.basicConfig(level=logging.ERROR)

# Global Variables
current_downloader = None
is_downloading = False
download_history = []

# History Functions
def load_history():
    global download_history
    try:
        if os.path.exists("download_history.json"):
            with open("download_history.json", "r") as file:
                download_history = json.load(file)
        for entry in download_history:
            if 'title' not in entry:
                entry['title'] = "Unknown"
    except Exception as e:
        logging.error(f"Failed to load history: {e}")
        download_history = []

def save_history():
    try:
        with open("download_history.json", "w") as file:
            json.dump(download_history, file)
    except Exception as e:
        logging.error(f"Failed to save history: {e}")

def add_to_history(url, type, quality, save_location, title):
    global download_history
    entry = {
        "url": url,
        "type": type,
        "quality": quality,
        "save_location": save_location,
        "title": title,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    download_history.append(entry)
    save_history()

class HomeGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Media Converter")
        self.setStyleSheet("""
            background-color: #1a1a1a;
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
        """)
        self.stacked_widget = QStackedWidget()
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        title = QLabel("  YouTube Media Converter  ")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        self.stacked_widget.addWidget(self.create_home_screen())
        
        self.audio_converter = AudioConverter(self)
        self.video_converter = VideoConverter(self)
        self.thumbnail_converter = ThumbnailConverter(self)
        self.post_converter = PostConverter(self)
        self.playlist_converter = PlaylistConverter(self)

        self.stacked_widget.addWidget(self.audio_converter)
        self.stacked_widget.addWidget(self.video_converter)
        self.stacked_widget.addWidget(self.thumbnail_converter)
        self.stacked_widget.addWidget(self.post_converter)
        self.stacked_widget.addWidget(self.playlist_converter)

        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def create_home_screen(self):
        home_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        converters = [
            ("Audio Converter", "🎵", self.open_audio_converter),
            ("Video Converter", "📹", self.open_video_converter),
            ("Thumbnail Downloader", "🖼️", self.open_thumbnail_converter),
            ("Post Downloader", "📝", self.open_post_converter),
            ("Playlist Downloader", "📂", self.open_playlist_converter)
        ]

        for name, icon, callback in converters:
            btn = QPushButton(f"{icon} {name}")
            btn.setFont(QFont("Segoe UI", 14))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    padding: 10px;
                    border-radius: 10px;
                    border: 2px solid #4CAF50;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                    border-color: #66BB6A;
                }
            """)
            btn.clicked.connect(callback)
            btn.enterEvent = lambda e, b=btn: self.animate_button(b, True)
            btn.leaveEvent = lambda e, b=btn: self.animate_button(b, False)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        history_label = QLabel("Recent Downloads")
        history_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        history_label.setStyleSheet("color: #aaaaaa; margin-top: 25px;")
        layout.addWidget(history_label)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #252525;
                border-radius: 10px;
                padding: 15px;
                color: #ffffff;
                font-size: 13px;
            }
            QListWidget::item:hover {
                background-color: #333333;
            }
        """)
        self.update_history_list()
        layout.addWidget(self.history_list)

        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(20)
        
        code_xceed = QPushButton("© 2025 codeXceed")
        code_xceed.setFont(QFont("Segoe UI", 11))
        code_xceed.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #666666;
                border: none;
            }
            QPushButton:hover {
                color: #4CAF50;
            }
        """)
        code_xceed.clicked.connect(lambda: webbrowser.open("https://www.youtube.com/channel/UCv4lewSF-uek7YQ8FG8THqw"))
        footer_layout.addWidget(code_xceed)

        coffee_btn = QPushButton("☕ Buy Me a Coffee")
        coffee_btn.setFont(QFont("Segoe UI", 11))
        coffee_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: #ffffff;
                padding: 8px 15px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        coffee_btn.clicked.connect(lambda: webbrowser.open("https://www.buymeacoffee.com/codexceed"))
        footer_layout.addWidget(coffee_btn)

        layout.addLayout(footer_layout)
        layout.addStretch()
        home_widget.setLayout(layout)
        return home_widget

    def animate_button(self, button, enter):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(150)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        rect = button.geometry()
        if enter:
            animation.setEndValue(rect.adjusted(-3, -3, 3, 3))
        else:
            animation.setEndValue(rect.adjusted(3, 3, -3, -3))
        animation.start()

    def open_audio_converter(self): self.stacked_widget.setCurrentIndex(1)
    def open_video_converter(self): self.stacked_widget.setCurrentIndex(2)
    def open_thumbnail_converter(self): self.stacked_widget.setCurrentIndex(3)
    def open_post_converter(self): self.stacked_widget.setCurrentIndex(4)
    def open_playlist_converter(self): self.stacked_widget.setCurrentIndex(5)
    def go_back(self): self.stacked_widget.setCurrentIndex(0)

    def update_history_list(self):
        self.history_list.clear()
        for entry in download_history[-5:]:
            title = entry.get('title', 'Unknown')
            self.history_list.addItem(f"{entry['type']} - {title} ({entry['quality']}) - {entry['timestamp']}")

class ConverterBase(QWidget):
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(str)
    download_finished = pyqtSignal(bool, str)

    def __init__(self, parent, title, icon):
        super().__init__()
        self.parent = parent
        self.title = title
        self.icon = icon
        self.save_path = None
        self.input_layout = None
        self.init_ui()
        self.status_update.connect(self.update_status)
        self.progress_update.connect(self.update_progress)
        self.download_finished.connect(self.finish_download)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 16px;
                padding: 8px;
            }
            QPushButton:hover {
                color: #4CAF50;
            }
        """)
        back_btn.clicked.connect(self.parent.go_back)
        header_label = QLabel(f"{self.icon} {self.title}")
        header_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(back_btn)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.input_layout = QVBoxLayout()
        self.input_layout.setSpacing(15)
        
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Enter URL here...")
        self.url_entry.setStyleSheet("""
            QLineEdit {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 12px;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        self.url_entry.textChanged.connect(self.check_ready_to_download)
        self.input_layout.addWidget(self.url_entry)

        self.quality_combobox = QComboBox()
        self.quality_combobox.setStyleSheet("""
            QComboBox {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 12px;
                color: #ffffff;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.input_layout.addWidget(self.quality_combobox)

        self.format_combobox = QComboBox()
        self.format_combobox.setStyleSheet("""
            QComboBox {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 12px;
                color: #ffffff;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.input_layout.addWidget(self.format_combobox)

        layout.addLayout(self.input_layout)

        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet("color: #aaaaaa; font-size: 13px;")
        folder_layout.addWidget(self.folder_label)
        folder_layout.addStretch()
        self.choose_folder_button = QPushButton("Select Folder")
        self.choose_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)
        self.choose_folder_button.clicked.connect(self.choose_folder)
        folder_layout.addWidget(self.choose_folder_button)

        layout.addLayout(folder_layout)

        self.download_button = QPushButton("Download")
        self.download_button.setEnabled(False)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: #ffffff;
                padding: 15px;
                border-radius: 10px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        layout.addWidget(self.download_button)

        self.progress_label = QLabel("0%")
        self.progress_label.setStyleSheet("color: #4CAF50; font-size: 14px;")
        self.progress_label.hide()
        layout.addWidget(self.progress_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Ready to download")
        self.status_label.setStyleSheet("color: #aaaaaa; font-size: 13px;")
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: #ffffff;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        self.cancel_button.hide()
        self.cancel_button.clicked.connect(self.cancel_download)
        layout.addWidget(self.cancel_button)

        self.instructions_label = QLabel(self.get_instructions())
        self.instructions_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        self.instructions_label.setWordWrap(True)
        layout.addWidget(self.instructions_label)

        layout.addStretch()
        self.setLayout(layout)

    def get_instructions(self):
        return "Usage instructions will be provided for each converter."

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if folder:
            self.save_path = folder
            self.folder_label.setText(f"Selected: {os.path.basename(self.save_path)}")
            self.status_label.setText("Folder selected")
            self.check_ready_to_download()

    def check_ready_to_download(self):
        url = self.url_entry.text().strip()
        self.download_button.setEnabled(bool(url and self.save_path))

    def reset_ui(self):
        global current_downloader, is_downloading
        is_downloading = False
        current_downloader = None
        self.download_button.setEnabled(bool(self.url_entry.text().strip() and self.save_path))
        self.cancel_button.hide()
        self.quality_combobox.setEnabled(True)
        self.format_combobox.setEnabled(True)
        self.progress_label.hide()
        self.progress_label.setText("0%")
        self.url_entry.setEnabled(True)
        self.status_label.setText("Ready to download")

    def cancel_download(self):
        global is_downloading
        if is_downloading:
            is_downloading = False
            self.status_label.setText("Cancelling download...")
            if current_downloader:
                current_downloader.params['abort'] = True

    def update_status(self, status):
        self.status_label.setText(status)

    def update_progress(self, progress):
        self.progress_label.setText(progress)

    def finish_download(self, success, message):
        self.status_label.setText(message)
        if success:
            QTimer.singleShot(1500, self.reset_ui)
        else:
            QTimer.singleShot(1000, self.reset_ui)

class AudioConverter(ConverterBase):
    def __init__(self, parent):
        super().__init__(parent, "Audio Converter", "🎵")
        self.quality_combobox.addItems(["64kbps", "128kbps", "192kbps", "256kbps", "320kbps"])
        self.format_combobox.addItems(["mp3", "wav", "aac"])
        self.download_button.clicked.connect(self.download_audio)

    def get_instructions(self):
        return (
            " ✅ To download audio:\n"
            "1. Enter the URL of the video.\n"
            "2. Select the desired audio quality (e.g., 128kbps).\n"
            "3. Choose a format (e.g., mp3).\n"
            "4. Choose a save location by clicking 'Select Folder'.\n"
            "5. Click 'Download' to start the process."
        )

    def download_audio(self):
        global current_downloader, is_downloading
        url = self.url_entry.text().strip()
        quality_text = self.quality_combobox.currentText()
        quality = quality_text.replace("kbps", "")
        format = self.format_combobox.currentText()

        if not url:
            self.status_label.setText("Please enter a valid URL")
            return
        if not self.save_path:
            self.status_label.setText("Please select a save location")
            return

        self.download_button.setEnabled(False)
        self.cancel_button.show()
        self.quality_combobox.setEnabled(False)
        self.format_combobox.setEnabled(False)
        self.progress_label.show()
        self.url_entry.setEnabled(False)
        self.status_label.setText("Starting download...")

        is_downloading = True
        threading.Thread(target=self.start_download, args=(url, self.save_path, quality, quality_text, format), daemon=True).start()

    def start_download(self, url, save_path, quality, quality_text, format):
        global current_downloader, is_downloading
        try:
            self.status_update.emit("Downloading audio...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(save_path, f'%(title)s_{quality_text}.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format,
                    'preferredquality': quality
                }],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                current_downloader = ydl
                info = ydl.extract_info(url, download=is_downloading)
                if is_downloading:
                    add_to_history(url, "Audio", quality_text, save_path, info.get('title', 'Unknown'))
                    self.parent.update_history_list()
                    self.download_finished.emit(True, "Download completed successfully")
                else:
                    self.download_finished.emit(False, "Download cancelled")
        except Exception as e:
            self.download_finished.emit(False, f"Error: {str(e)[:50]}...")

    def progress_hook(self, d):
        global is_downloading
        if not is_downloading:
            raise Exception("Download cancelled")
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                percent = int((d['downloaded_bytes'] / d['total_bytes']) * 100)
                self.progress_update.emit(f"{percent}%")
            elif d.get('total_bytes_estimate'):
                percent = int((d['downloaded_bytes'] / d['total_bytes_estimate']) * 100)
                self.progress_update.emit(f"{percent}%")
            else:
                # If no size info available, at least show some progress
                self.progress_update.emit(f"Downloading... {d.get('downloaded_bytes', 0) // 1024 // 1024}MB")

class VideoConverter(ConverterBase):
    def __init__(self, parent):
        super().__init__(parent, "Video Converter", "📹")
        self.quality_combobox.addItems(["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"])
        self.format_combobox.addItems(["mp4", "avi", "mkv"])

        # Remove format_combobox from input_layout to reposition it
        self.input_layout.removeWidget(self.format_combobox)

        # Create subtitle checkbox with a toggle-switch-like stylesheet
        self.subtitle_checkbox = QCheckBox("Download Subtitles")
        self.subtitle_checkbox.setStyleSheet("""
            QCheckBox {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 12px;
                color: #ffffff;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
                border-radius: 10px;
                background-color: #333333;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
            QCheckBox:hover {
                border-color: #4CAF50;
            }
        """)

        # Create a horizontal layout for format_combobox and subtitle_checkbox
        format_and_subtitle_layout = QHBoxLayout()
        format_and_subtitle_layout.addWidget(self.format_combobox)
        format_and_subtitle_layout.addWidget(self.subtitle_checkbox)
        format_and_subtitle_layout.addStretch()  # Push widgets to the left, optional

        # Add the horizontal layout back to input_layout
        self.input_layout.addLayout(format_and_subtitle_layout)

        self.download_button.clicked.connect(self.download_video)

    def get_instructions(self):
        return (
            '⚠ If you don\'t hear sound in Windows Media Player or Photos app, '
            'try using <a href="https://www.videolan.org/vlc/" style="color: #4CAF50;">VLC Media Player</a>.<br><br>'
            " ✅ To download a video:<br>"
            "1. Enter the URL of the video.<br>"
            "2. Select the desired video quality (e.g., 720p).<br>"
            "3. Choose a format (e.g., mp4).<br>"
            "4. Optionally, check 'Download Subtitles'.<br>"
            "5. Choose a save location by clicking 'Select Folder'.<br>"
            "6. Click 'Download' to start the process."
        )

    def download_video(self):
        global current_downloader, is_downloading
        url = self.url_entry.text().strip()
        quality_text = self.quality_combobox.currentText()
        quality = quality_text.replace("p", "")
        format = self.format_combobox.currentText()
        download_subtitles = self.subtitle_checkbox.isChecked()

        if not url:
            self.status_label.setText("Please enter a valid URL")
            return
        if not self.save_path:
            self.status_label.setText("Please select a save location")
            return

        self.download_button.setEnabled(False)
        self.cancel_button.show()
        self.quality_combobox.setEnabled(False)
        self.format_combobox.setEnabled(False)
        self.subtitle_checkbox.setEnabled(False)
        self.progress_label.show()
        self.url_entry.setEnabled(False)
        self.status_label.setText("Starting download...")

        is_downloading = True
        threading.Thread(target=self.start_download, args=(url, self.save_path, quality, quality_text, format, download_subtitles), daemon=True).start()

    def start_download(self, url, save_path, quality, quality_text, format, download_subtitles):
        global current_downloader, is_downloading
        try:
            self.status_update.emit("Downloading video...")
            ydl_opts = {
                'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
                'merge_output_format': format,
                'outtmpl': os.path.join(save_path, f'%(title)s_{quality_text}.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': format}],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }
            if download_subtitles:
                ydl_opts['writesubtitles'] = True
                ydl_opts['subtitleslangs'] = ['en']
            with YoutubeDL(ydl_opts) as ydl:
                current_downloader = ydl
                info = ydl.extract_info(url, download=is_downloading)
                if is_downloading:
                    add_to_history(url, "Video", quality_text, save_path, info.get('title', 'Unknown'))
                    self.parent.update_history_list()
                    self.download_finished.emit(True, "Download completed successfully")
                else:
                    self.download_finished.emit(False, "Download cancelled")
        except Exception as e:
            self.download_finished.emit(False, f"Error: {str(e)[:50]}...")

    def progress_hook(self, d):
        global is_downloading
        if not is_downloading:
            raise Exception("Download cancelled")
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                percent = int((d['downloaded_bytes'] / d['total_bytes']) * 100)
                self.progress_update.emit(f"{percent}%")
            elif d.get('total_bytes_estimate'):
                percent = int((d['downloaded_bytes'] / d['total_bytes_estimate']) * 100)
                self.progress_update.emit(f"{percent}%")
            else:
                # If no size info available, at least show some progress
                self.progress_update.emit(f"Downloading... {d.get('downloaded_bytes', 0) // 1024 // 1024}MB")
                
            if 'info_dict' in d and 'title' in d['info_dict'] and (d.get('downloaded_bytes', 0) == 0):
                self.current_video += 1
                self.status_update.emit(f"Downloading video {self.current_video} of {self.total_videos}: {d['info_dict']['title'][:30]}...")
        elif d['status'] == 'finished':
            self.progress_update.emit("100%")
            self.status_update.emit(f"Finished video {self.current_video} of {self.total_videos}")

    def reset_ui(self):
        super().reset_ui()
        self.subtitle_checkbox.setEnabled(True)

class ThumbnailConverter(ConverterBase):
    def __init__(self, parent):
        super().__init__(parent, "Thumbnail Downloader", "🖼️")
        self.quality_combobox.addItems(["Default", "Medium", "High", "SD", "HD"])
        self.format_combobox.addItems(["jpg", "png"])
        self.download_button.clicked.connect(self.download_thumbnail)

    def get_instructions(self):
        return (
            " ✅ To download a thumbnail:\n"
            "1. Enter the URL of the video.\n"
            "2. Select the desired thumbnail quality (e.g., HD).\n"
            "3. Choose a format (e.g., jpg).\n"
            "4. Choose a save location by clicking 'Select Folder'.\n"
            "5. Click 'Download' to start the process."
        )

    def download_thumbnail(self):
        global is_downloading
        url = self.url_entry.text().strip()
        quality = self.quality_combobox.currentText()
        format = self.format_combobox.currentText()

        if not url:
            self.status_label.setText("Please enter a valid URL")
            return
        if not self.save_path:
            self.status_label.setText("Please select a save location")
            return

        self.download_button.setEnabled(False)
        self.cancel_button.show()
        self.url_entry.setEnabled(False)
        self.progress_label.show()
        self.status_label.setText("Starting download...")

        is_downloading = True
        threading.Thread(target=self.start_download, args=(url, self.save_path, quality, format), daemon=True).start()

    def start_download(self, url, save_path, quality, format):
        global is_downloading
        try:
            self.status_update.emit("Getting video info...")
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = sanitize_filename(info.get('title', 'thumbnail'))
                video_id = info.get('id', 'unknown')

            self.status_update.emit("Downloading thumbnail...")
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/{self.get_thumbnail_quality(quality)}"
            save_location = os.path.join(save_path, f"{title}_thumbnail_{quality}.{format}")
            response = requests.get(thumbnail_url, stream=True)
            response.raise_for_status()

            with open(save_location, 'wb') as file:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                for chunk in response.iter_content(1024):
                    if not is_downloading:
                        raise Exception("Download cancelled")
                    downloaded += len(chunk)
                    file.write(chunk)
                    if total_size:
                        percent = int((downloaded / total_size) * 100)
                        self.progress_update.emit(f"{percent}%")

            if is_downloading:
                add_to_history(url, "Thumbnail", quality, save_path, title)
                self.parent.update_history_list()
                self.download_finished.emit(True, "Download completed successfully")
            else:
                self.download_finished.emit(False, "Download cancelled")
        except Exception as e:
            self.download_finished.emit(False, f"Error: {str(e)[:50]}...")

    def get_thumbnail_quality(self, quality):
        return {
            "Default": "default.jpg",
            "Medium": "mqdefault.jpg",
            "High": "hqdefault.jpg",
            "SD": "sddefault.jpg",
            "HD": "maxresdefault.jpg"
        }.get(quality, "default.jpg")

class PostConverter(ConverterBase):
    def __init__(self, parent):
        super().__init__(parent, "Post Downloader", "📝")
        self.quality_combobox.addItems(["Original"])
        self.format_combobox.addItems(["jpg", "png"])
        self.download_button.clicked.connect(self.download_post)

    def get_instructions(self):
        return (
            " ✅ To download a post:\n"
            "1. Enter the URL of the post.\n"
            "2. Choose a format (e.g., jpg).\n"
            "3. Choose a save location by clicking 'Select Folder'.\n"
            "4. Click 'Download' to start the process."
        )

    def download_post(self):
        global is_downloading
        url = self.url_entry.text().strip()
        format = self.format_combobox.currentText()

        if not url:
            self.status_label.setText("Please enter a valid URL")
            return
        if not self.save_path:
            self.status_label.setText("Please select a save location")
            return

        self.download_button.setEnabled(False)
        self.cancel_button.show()
        self.url_entry.setEnabled(False)
        self.progress_label.show()
        self.status_label.setText("Starting download...")

        is_downloading = True
        threading.Thread(target=self.start_download, args=(url, self.save_path, format), daemon=True).start()

    def start_download(self, url, save_path, format):
        global is_downloading
        try:
            self.status_update.emit("Downloading post...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            title = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            file_name = os.path.join(save_path, f"{title}.{format}")
            with open(file_name, "wb") as file:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                for chunk in response.iter_content(1024):
                    if not is_downloading:
                        raise Exception("Download cancelled")
                    downloaded += len(chunk)
                    file.write(chunk)
                    if total_size:
                        percent = int((downloaded / total_size) * 100)
                        self.progress_update.emit(f"{percent}%")

            if is_downloading:
                add_to_history(url, "Post", "Original", save_path, title)
                self.parent.update_history_list()
                self.download_finished.emit(True, "Download completed successfully")
            else:
                self.download_finished.emit(False, "Download cancelled")
        except Exception as e:
            self.download_finished.emit(False, f"Error: {str(e)[:50]}...")

class PlaylistConverter(ConverterBase):
    def __init__(self, parent):
        super().__init__(parent, "Playlist Downloader", "📂")
        self.quality_combobox.addItems(["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"])
        self.format_combobox.addItems(["mp4", "avi", "mkv"])
        self.download_button.clicked.connect(self.download_playlist)
        self.current_video = 0
        self.total_videos = 0
        self.video_titles = []
        self.current_title = ""

    def get_instructions(self):
        return (
            '⚠ If you don\'t hear sound in Windows Media Player or Photos app, '
            'try using <a href="https://www.videolan.org/vlc/" style="color: #4CAF50;">VLC Media Player</a>.<br><br>'
            " ✅ To download a playlist:<br>"
            "1. Enter the URL of the playlist.<br>"
            "2. Select the desired video quality (e.g., 1080p).<br>"
            "3. Choose a format (e.g., mp4).\n"
            "4. Choose a save location by clicking 'Select Folder'.\n"
            "5. Click 'Download' to start downloading the entire playlist."
        )

    def download_playlist(self):
        global current_downloader, is_downloading
        url = self.url_entry.text().strip()
        quality_text = self.quality_combobox.currentText()
        quality = quality_text.replace("p", "")
        format = self.format_combobox.currentText()

        if not url:
            self.status_label.setText("Please enter a valid URL")
            return
        if not self.save_path:
            self.status_label.setText("Please select a save location")
            return

        self.download_button.setEnabled(False)
        self.cancel_button.show()
        self.quality_combobox.setEnabled(False)
        self.format_combobox.setEnabled(False)
        self.progress_label.show()
        self.url_entry.setEnabled(False)
        self.status_label.setText("Analyzing playlist...")

        is_downloading = True
        threading.Thread(target=self.start_download, args=(url, self.save_path, quality, quality_text, format), daemon=True).start()

    def start_download(self, url, save_path, quality, quality_text, format):
        global current_downloader, is_downloading
        try:
            # First pass to get playlist info
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'skip_download': True,
                'playlistend': 999999,  # Ensure we get all videos in the playlist
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Check if it's actually a playlist
                if 'entries' not in info:
                    self.status_update.emit("This doesn't appear to be a playlist")
                    self.download_finished.emit(False, "Not a valid playlist URL")
                    return
                
                self.total_videos = len(info['entries'])
                title = info.get('title', 'playlist')
                
                if self.total_videos == 0:
                    self.status_update.emit("No videos found in playlist")
                    self.download_finished.emit(False, "Playlist appears to be empty")
                    return
                
                # Pre-fetch video titles if possible
                self.video_titles = []
                for entry in info['entries']:
                    if 'title' in entry:
                        self.video_titles.append(entry['title'])
                    else:
                        self.video_titles.append(f"Video {len(self.video_titles) + 1}")
                
                self.status_update.emit(f"Found {self.total_videos} videos in playlist: {title}")

            if not is_downloading:
                self.download_finished.emit(False, "Download cancelled")
                return

            # Second pass to actually download
            ydl_opts = {
                'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
                'merge_output_format': format,
                'outtmpl': os.path.join(save_path, f'%(playlist_index)s - %(title)s_{quality_text}.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': format}],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': False,  # Ensure playlist is processed
                'playlistend': 999999,  # Ensure all videos are downloaded
            }
            
            self.current_video = 0
            with YoutubeDL(ydl_opts) as ydl:
                current_downloader = ydl
                self.status_update.emit(f"Starting download of {self.total_videos} videos")
                ydl.download([url])

            if is_downloading:
                add_to_history(url, "Playlist", quality_text, save_path, title)
                self.parent.update_history_list()
                self.download_finished.emit(True, "Playlist download completed successfully")
            else:
                self.download_finished.emit(False, "Download cancelled")
        except Exception as e:
            self.download_finished.emit(False, f"Error: {str(e)[:50]}...")

    def progress_hook(self, d):
        global is_downloading
        if not is_downloading:
            raise Exception("Download cancelled")
        
        if d['status'] == 'downloading':
            # Update title if it's a new video
            if 'info_dict' in d and 'title' in d['info_dict']:
                new_title = d['info_dict']['title']
                if new_title != self.current_title:
                    self.current_title = new_title
                    # Try to find the playlist index
                    if 'playlist_index' in d['info_dict']:
                        self.current_video = int(d['info_dict']['playlist_index'])
                    else:
                        self.current_video += 1
                    # Update status with current video info
                    self.status_update.emit(f"Downloading ({self.current_video}/{self.total_videos}): {self.current_title[:40]}...")
            
            # Update progress percentage
            if d.get('total_bytes'):
                percent = int((d['downloaded_bytes'] / d['total_bytes']) * 100)
                self.progress_update.emit(f"{percent}%")
            elif d.get('total_bytes_estimate'):
                percent = int((d['downloaded_bytes'] / d['total_bytes_estimate']) * 100)
                self.progress_update.emit(f"{percent}%")
            else:
                # If no size info available, at least show some progress
                self.progress_update.emit(f"Downloading... {d.get('downloaded_bytes', 0) // 1024 // 1024}MB")
        
        elif d['status'] == 'finished':
            self.progress_update.emit("100%")
            # Add an explicit message to indicate which video is being processed
            if 'info_dict' in d and 'title' in d['info_dict']:
                filename = d['filename']
                self.status_update.emit(f"Processing video {self.current_video} of {self.total_videos}: {os.path.basename(filename)}")

    def reset_ui(self):
        super().reset_ui()
        self.current_video = 0
        self.total_videos = 0
        self.video_titles = []
        self.current_title = ""

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    load_history()
    app = QApplication(sys.argv)
    window = HomeGUI()
    window.show()
    sys.exit(app.exec())