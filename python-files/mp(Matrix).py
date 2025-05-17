import os
import sys
import random
from PyQt5.QtCore import Qt, QTimer, QUrl, QSize, QEvent
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QPixmap, QPainterPath
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QSlider, QLabel, QFileDialog, QFrame, QSizePolicy)
import vlc

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(30)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.title_label = QLabel("Cyberpunk Media Player")
        self.title_label.setStyleSheet("color: #00ff00; font-weight: bold; font-family: 'Courier New';")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.minimize_btn = QPushButton("_")
        self.minimize_btn.setFixedSize(30, 30)
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(30, 30)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.parent.close)
        
        layout.addSpacing(5)
        layout.addWidget(self.title_label)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #222222;
                color: #00ff00;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton#close_btn:hover {
                background-color: #aa0000;
            }
        """)
        
        self.start_pos = None
        
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            delta = event.pos() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            
    def mouseReleaseEvent(self, event):
        self.start_pos = None
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(20, 20, 20))
        
        # Draw bottom border with glow
        pen = QPen(QColor(0, 255, 0, 180))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        
        # Draw glow effect
        for i in range(3):
            alpha = 100 - (i * 30)
            pen = QPen(QColor(0, 255, 0, alpha))
            pen.setWidth(1)
            painter.setPen(pen)
            y_pos = self.height() - 1 + i
            if y_pos < self.height() + 3:
                painter.drawLine(0, y_pos, self.width(), y_pos)

class AlbumArt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.album_art = None
        self.default_art = QPixmap(200, 200)
        self.default_art.fill(Qt.black)
        
    def set_album_art(self, path):
        if path and os.path.exists(path):
            self.album_art = QPixmap(path).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            self.album_art = self.default_art
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(10, 10, 10))
        
        # Draw album art
        if self.album_art:
            x = (self.width() - self.album_art.width()) // 2
            y = (self.height() - self.album_art.height()) // 2
            painter.drawPixmap(x, y, self.album_art)
        
        # Draw border with glow
        pen = QPen(QColor(0, 255, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(2, 2, self.width() - 4, self.height() - 4)
        
        # Draw glow effect
        for i in range(3):
            alpha = 100 - (i * 30)
            pen = QPen(QColor(0, 255, 0, alpha))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(2 + i, 2 + i, self.width() - 4 - (i * 2), self.height() - 4 - (i * 2))

class AudioVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.bars = [random.randint(5, 50) for _ in range(20)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_bars)
        self.timer.start(100)
        
    def update_bars(self):
        for i in range(len(self.bars)):
            # Simulate audio activity
            change = random.randint(-10, 10)
            self.bars[i] += change
            self.bars[i] = max(5, min(50, self.bars[i]))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(10, 10, 10))
        
        # Draw visualizer bars
        bar_width = self.width() / (len(self.bars) * 2)
        for i, height in enumerate(self.bars):
            x = i * bar_width * 2 + bar_width / 2
            y = self.height() - height
            
            # Create gradient for bars
            gradient = QLinearGradient(x, y, x, self.height())
            gradient.setColorAt(0, QColor(0, 255, 0))
            gradient.setColorAt(1, QColor(0, 100, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, bar_width, height, 2, 2)
        
        # Draw border with glow
        pen = QPen(QColor(0, 255, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(2, 2, self.width() - 4, self.height() - 4)

class HUDOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        
        self.scanline_pos = 0
        self.glitch_timer = 0
        self.glitch_rects = []
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw scan line
        self.scanline_pos = (self.scanline_pos + 5) % self.height()
        painter.setPen(QPen(QColor(0, 255, 0, 30), 2))
        painter.drawLine(0, self.scanline_pos, self.width(), self.scanline_pos)
        
        # Draw HUD elements
        painter.setPen(QPen(QColor(0, 255, 0, 150)))
        painter.setFont(QFont("Courier New", 8))
        
        # Top-left corner
        painter.drawText(10, 20, "SYS//MEDIA_PLAYER_v2.5")
        painter.drawText(10, 35, f"RESOLUTION: {self.width()}x{self.height()}")
        
        # Top-right corner
        text = "CYBERPUNK//INTERFACE"
        text_width = painter.fontMetrics().horizontalAdvance(text)
        painter.drawText(self.width() - text_width - 10, 20, text)
        
        # Bottom-left corner
        painter.drawText(10, self.height() - 20, "STATUS: ONLINE")
        
        # Draw corner brackets
        pen = QPen(QColor(0, 255, 0, 200), 2)
        painter.setPen(pen)
        
        # Top-left bracket
        painter.drawLine(5, 5, 25, 5)
        painter.drawLine(5, 5, 5, 25)
        
        # Top-right bracket
        painter.drawLine(self.width() - 25, 5, self.width() - 5, 5)
        painter.drawLine(self.width() - 5, 5, self.width() - 5, 25)
        
        # Bottom-left bracket
        painter.drawLine(5, self.height() - 5, 25, self.height() - 5)
        painter.drawLine(5, self.height() - 25, 5, self.height() - 5)
        
        # Bottom-right bracket
        painter.drawLine(self.width() - 25, self.height() - 5, self.width() - 5, self.height() - 5)
        painter.drawLine(self.width() - 5, self.height() - 25, self.width() - 5, self.height() - 5)
        
        # Random glitches
        self.glitch_timer += 1
        if self.glitch_timer >= 10:
            self.glitch_timer = 0
            self.glitch_rects = []
            if random.random() < 0.3:  # 30% chance of glitch
                for _ in range(random.randint(1, 3)):
                    x = random.randint(0, self.width() - 50)
                    y = random.randint(0, self.height() - 10)
                    w = random.randint(20, 100)
                    h = random.randint(5, 10)
                    self.glitch_rects.append((x, y, w, h))
        
        for x, y, w, h in self.glitch_rects:
            painter.fillRect(x, y, w, h, QColor(0, 255, 0, 50))

class CyberpunkMediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize VLC instance and media player
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        
        self.is_video_loaded = False
        self.is_fullscreen = False
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Cyberpunk Media Player")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(800, 600)
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Title bar
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # Video frame
        self.videoframe = QFrame()
        self.videoframe.setStyleSheet("background-color: black;")
        self.videoframe.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # HUD overlay for video
        self.hud = HUDOverlay(self.videoframe)
        hud_layout = QVBoxLayout(self.videoframe)
        hud_layout.setContentsMargins(0, 0, 0, 0)
        hud_layout.addWidget(self.hud)
        
        self.main_layout.addWidget(self.videoframe)
        
        # Audio widget (initially hidden)
        self.audio_widget = QWidget()
        self.audio_layout = QVBoxLayout(self.audio_widget)
        
        self.audio_label = QLabel("No audio file loaded")
        self.audio_label.setAlignment(Qt.AlignCenter)
        self.audio_label.setStyleSheet("color: #00ff00; font-weight: bold; font-family: 'Courier New';")
        
        self.album_art = AlbumArt()
        self.visualizer = AudioVisualizer()
        
        self.audio_layout.addWidget(self.audio_label)
        self.audio_layout.addWidget(self.album_art)
        self.audio_layout.addWidget(self.visualizer)
        
        self.main_layout.addWidget(self.audio_widget)
        self.audio_widget.hide()
        
        # Seek slider
        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderMoved.connect(self.set_position)
        self.seek_slider.sliderPressed.connect(self.set_position)
        self.main_layout.addWidget(self.seek_slider)
        
        # Controls
        self.controls = QWidget()
        controls_layout = QHBoxLayout(self.controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_pause)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_file)
        
        self.fullscreen_button = QPushButton("Fullscreen")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.open_button)
        controls_layout.addWidget(self.fullscreen_button)
        controls_layout.addWidget(QLabel("Volume:"))
        controls_layout.addWidget(self.volume_slider)
        
        self.main_layout.addWidget(self.controls)
        
        # Set up the timer to update the seek bar
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)
        
        # Set up audio controls for minimized mode
        self.audio_controls = QWidget()
        audio_controls_layout = QHBoxLayout(self.audio_controls)
        audio_controls_layout.setContentsMargins(0, 0, 0, 0)
        
        self.audio_play_button = QPushButton("Play")
        self.audio_play_button.clicked.connect(self.play_pause)
        
        self.audio_stop_button = QPushButton("Stop")
        self.audio_stop_button.clicked.connect(self.stop)
        
        self.audio_slider = QSlider(Qt.Horizontal)
        self.audio_slider.setRange(0, 1000)
        self.audio_slider.sliderMoved.connect(self.set_position)
        self.audio_slider.sliderPressed.connect(self.set_position)
        
        audio_controls_layout.addWidget(self.audio_play_button)
        audio_controls_layout.addWidget(self.audio_stop_button)
        audio_controls_layout.addWidget(self.audio_slider)
        
        self.audio_layout.addWidget(self.audio_controls)
        
        # Apply cyberpunk styling
        self.apply_cyberpunk_style()
        
    def apply_cyberpunk_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
                border: 2px solid #00ff00;
            }
            QWidget {
                background-color: #121212;
                color: #00ff00;
            }
            QPushButton {
                background-color: #222222;
                color: #00ff00;
                border: 1px solid #00ff00;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Courier New';
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                border: 1px solid #00ffaa;
            }
            QPushButton:pressed {
                background-color: #00aa00;
            }
            QSlider::groove:horizontal {
                border: 1px solid #00ff00;
                height: 8px;
                background: #222222;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00ff00;
                border: 1px solid #00ff00;
                width: 18px;
                margin: -2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal:hover {
                background: #00ffaa;
            }
            QLabel {
                color: #00ff00;
                font-family: 'Courier New';
            }
        """)
        
    def open_file(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Media files (*.mp3 *.mp4 *.avi *.mkv *.flac *.wav)")
        
        if dialog.exec_():
            file_path = dialog.selectedFiles()[0]
            self.load_media(file_path)
            
    def load_media(self, file_path):
        # Stop any currently playing media
        if self.mediaplayer.is_playing():
            self.mediaplayer.stop()
            
        # Create a new media object
        self.media = self.instance.media_new(file_path)
        self.mediaplayer.set_media(self.media)
        
        # Get file name from path
        filename = os.path.basename(file_path)
        
        # Check if it's a video or audio file
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
        audio_extensions = ['.mp3', '.flac', '.wav', '.aac', '.ogg']
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in video_extensions:
            self.is_video_loaded = True
            self.switch_to_video_mode()
        elif file_ext in audio_extensions:
            self.is_video_loaded = False
            self.switch_to_audio_mode(file_path, filename)
        
        # Set up video output if needed
        if self.is_video_loaded:
            self.set_video_output()
        
        # Start playback
        self.mediaplayer.play()
        self.play_button.setText("Pause")
        self.audio_play_button.setText("Pause")
        
        # Start the UI update timer
        self.timer.start()
        
    def switch_to_video_mode(self):
        self.audio_widget.hide()
        self.videoframe.show()
        self.hud.show()
        self.seek_slider.show()
        self.controls.show()
        
    def switch_to_audio_mode(self, file_path, filename):
        self.videoframe.hide()
        self.hud.hide()
        self.seek_slider.hide()
        self.controls.hide()
        self.audio_widget.show()
        
        # Try to find album art
        folder = os.path.dirname(file_path)
        for artname in ["cover.jpg", "folder.jpg", "album.jpg", "cover.png", "folder.png"]:
            artpath = os.path.join(folder, artname)
            if os.path.exists(artpath):
                self.album_art.set_album_art(artpath)
                break
        else:
            self.album_art.set_album_art(None)
        
        self.audio_label.setText(f"Now Playing: {filename}")
        
        # Check window state and adjust UI accordingly
        if self.isMinimized():
            self.switch_to_minimized_audio_mode()
        else:
            self.switch_to_normal_audio_mode()
            
    def switch_to_minimized_audio_mode(self):
        # Hide album art and visualizer
        self.album_art.hide()
        self.visualizer.hide()
        
        # Show only essential controls in a compact layout
        self.audio_controls.show()
        self.audio_slider.show()
        
        # Set to a very compact size
        self.setFixedSize(320, 120)
        
    def switch_to_normal_audio_mode(self):
        # Show all audio components
        self.album_art.show()
        self.visualizer.show()
        self.audio_controls.show()
        
        # Set to standard audio mode size
        self.setFixedSize(420, 540)
        
    def set_video_output(self):
        # Set the video output to the videoframe widget
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))
            
    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.play_button.setText("Play")
            self.audio_play_button.setText("Play")
        else:
            if self.mediaplayer.get_media():
                self.mediaplayer.play()
                self.play_button.setText("Pause")
                self.audio_play_button.setText("Pause")
                
    def stop(self):
        self.mediaplayer.stop()
        self.play_button.setText("Play")
        self.audio_play_button.setText("Play")
        
    def set_volume(self, volume):
        self.mediaplayer.audio_set_volume(volume)
        
    def set_position(self):
        # Set the media position to where the slider was moved
        if self.mediaplayer.is_playing():
            pos = self.seek_slider.value()
            self.mediaplayer.set_position(pos / 1000.0)
            
    def update_ui(self):
        # Update the slider position based on the media position
        if self.mediaplayer.is_playing():
            position = self.mediaplayer.get_position() * 1000
            self.seek_slider.setValue(int(position))
            self.audio_slider.setValue(int(position))
            
    def toggle_fullscreen(self):
        current_position = 0
        was_playing = False
        if self.mediaplayer and self.mediaplayer.get_media():
            current_position = self.mediaplayer.get_time()
            was_playing = self.mediaplayer.is_playing()
            self.mediaplayer.stop()
        
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True
        
        # Handle audio mode layout if needed
        if self.audio_widget.isVisible():
            self.switch_to_normal_audio_mode()
        
        if self.mediaplayer and self.mediaplayer.get_media():
            if self.is_video_loaded:
                self.set_video_output()
            self.mediaplayer.set_time(current_position)
            if was_playing:
                self.mediaplayer.play()
                self.play_button.setText("Pause")
                self.audio_play_button.setText("Pause")
                
    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized() and self.audio_widget.isVisible():
                self.switch_to_minimized_audio_mode()
            elif not self.isMinimized() and self.audio_widget.isVisible():
                self.switch_to_normal_audio_mode()
                
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw border with glow effect
        pen = QPen(QColor(0, 255, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
        
        # Glow effect
        for i in range(3):
            alpha = 100 - (i * 30)
            pen = QPen(QColor(0, 255, 0, alpha))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(i, i, self.width() - (i * 2), self.height() - (i * 2))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = CyberpunkMediaPlayer()
    player.show()
    sys.exit(app.exec_())
