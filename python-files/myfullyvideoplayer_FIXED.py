# potplayer_clone.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QStatusBar, QFileDialog, QToolBar, QAction,
    QLabel, QMessageBox, QListWidget, QPushButton, QSizePolicy, QSlider
)
from PyQt6.QtGui import QIcon, QKeySequence
from PyQt6.QtCore import Qt, QSize

class VideoDisplay(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel("🎬 Video Display Area")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background-color: black; color: white; font-size: 24px;")
        layout.addWidget(self.label)

    def play(self, file_path):
        self.label.setText(f"▶️ Playing: {file_path}")

class PlaybackControls(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.play_btn = QPushButton("▶️ Play")
        self.pause_btn = QPushButton("⏸ Pause")
        self.stop_btn = QPushButton("⏹ Stop")
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)

        self.play_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.pause_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.stop_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.seek_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout.addWidget(self.play_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(QLabel("Seek:"))
        layout.addWidget(self.seek_slider)
        layout.addWidget(QLabel("Volume:"))
        layout.addWidget(self.volume_slider)

class PlaylistWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel("📂 Playlist")
        self.list_widget = QListWidget()

        layout.addWidget(self.label)
        layout.addWidget(self.list_widget)
        self.add_mock_items()

    def add_mock_items(self):
        for i in range(3):
            self.list_widget.addItem(f"Sample Track {i+1}")

    def add_item(self, file_path):
        self.list_widget.addItem(file_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎞 PotPlayer Clone")
        self.setGeometry(100, 100, 1280, 720)
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        self._create_main_layout()

    def _create_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # File Menu
        file_menu = menubar.addMenu("&File")
        open_action = QAction("📂 Open File", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        exit_action = QAction("❌ Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menubar.addMenu("&View")
        toggle_playlist_action = QAction("📃 Toggle Playlist", self)
        toggle_playlist_action.setCheckable(True)
        toggle_playlist_action.setChecked(True)
        toggle_playlist_action.triggered.connect(self.toggle_playlist)
        view_menu.addAction(toggle_playlist_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        open_btn = QAction(QIcon(), "Open", self)
        open_btn.triggered.connect(self.open_file)
        toolbar.addAction(open_btn)

        play_btn = QAction(QIcon(), "Play", self)
        toolbar.addAction(play_btn)

        pause_btn = QAction(QIcon(), "Pause", self)
        toolbar.addAction(pause_btn)

    def _create_statusbar(self):
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        statusbar.showMessage("Ready")

    def _create_main_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Video Area
        self.video_display = VideoDisplay()
        main_layout.addWidget(self.video_display, 5)

        # Playback Controls
        self.controls = PlaybackControls()
        main_layout.addWidget(self.controls)

        # Playlist
        self.playlist = PlaylistWidget()
        self.playlist.setMaximumHeight(180)
        main_layout.addWidget(self.playlist)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Media File")
        if file_path:
            self.statusBar().showMessage(f"Loaded: {file_path}")
            self.video_display.play(file_path)
            self.playlist.add_item(file_path)

    def toggle_playlist(self, state):
        self.playlist.setVisible(state)

    def show_about(self):
        QMessageBox.about(self, "About PotPlayer Clone",
                          "PotPlayer Clone\nBuilt with Python + PyQt6\n© 2025")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PotPlayer Clone")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# === LINE 501 ===

import vlc

class MediaPlayer:
    def __init__(self, video_widget):
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.video_widget = video_widget

        if sys.platform.startswith("linux"):  # X11
            self.mediaplayer.set_xwindow(self.video_widget.winId())
        elif sys.platform == "win32":
            self.mediaplayer.set_hwnd(int(self.video_widget.winId()))
        elif sys.platform == "darwin":
            self.mediaplayer.set_nsobject(int(self.video_widget.winId()))

    def set_media(self, file_path):
        media = self.instance.media_new(file_path)
        self.mediaplayer.set_media(media)
        self.mediaplayer.play()

    def play(self):
        if self.mediaplayer.get_state() == vlc.State.Paused:
            self.mediaplayer.play()

    def pause(self):
        self.mediaplayer.pause()

    def stop(self):
        self.mediaplayer.stop()

    def is_playing(self):
        return self.mediaplayer.is_playing()

    def get_position(self):
        return self.mediaplayer.get_position()

    def set_position(self, pos):
        self.mediaplayer.set_position(pos)

    def set_volume(self, volume):
        self.mediaplayer.audio_set_volume(volume)

    def get_volume(self):
        return self.mediaplayer.audio_get_volume()

    def get_duration(self):
        return self.mediaplayer.get_length()

    def get_time(self):
        return self.mediaplayer.get_time()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎞 PotPlayer Clone")
        self.setGeometry(100, 100, 1280, 720)
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        self._create_main_layout()
        self.media_player = MediaPlayer(self.video_display)
        self._connect_controls()

    def _connect_controls(self):
        self.controls.play_btn.clicked.connect(self.play_media)
        self.controls.pause_btn.clicked.connect(self.pause_media)
        self.controls.stop_btn.clicked.connect(self.stop_media)
        self.controls.volume_slider.valueChanged.connect(self.change_volume)
        self.controls.seek_slider.sliderReleased.connect(self.seek_position)

    def play_media(self):
        self.media_player.play()
        self.statusBar().showMessage("Playing...")

    def pause_media(self):
        self.media_player.pause()
        self.statusBar().showMessage("Paused")

    def stop_media(self):
        self.media_player.stop()
        self.statusBar().showMessage("Stopped")

    def change_volume(self, value):
        self.media_player.set_volume(value)
        self.statusBar().showMessage(f"Volume: {value}%")

    def seek_position(self):
        position = self.controls.seek_slider.value() / 100.0
        self.media_player.set_position(position)
        self.statusBar().showMessage(f"Seek: {int(position * 100)}%")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Media File")
        if file_path:
            self.statusBar().showMessage(f"Loaded: {file_path}")
            self.video_display.play(file_path)
            self.playlist.add_item(file_path)
            self.media_player.set_media(file_path)

# Auto-reconnect platform-specific video rendering
def update_video_widget_bindings(media_player, widget):
    if sys.platform.startswith("linux"):  # X11
        media_player.set_xwindow(widget.winId())
    elif sys.platform == "win32":
        media_player.set_hwnd(int(widget.winId()))
    elif sys.platform == "darwin":
        media_player.set_nsobject(int(widget.winId()))

# Reimplement the VideoDisplay to support actual rendering surface (optional fullscreen later)
class VideoDisplay(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel("🎬 Video Display Area")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background-color: black; color: white; font-size: 24px;")
        layout.addWidget(self.label)

    def mouseDoubleClickEvent(self, event):
        self.toggle_fullscreen()

    def toggle_fullscreen(self):
        parent = self.window()
        if parent.isFullScreen():
            parent.showNormal()
        else:
            parent.showFullScreen()

    def play(self, file_path):
        self.label.setText(f"▶️ Playing: {file_path}")

# Timer to update seek bar and track progress
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎞 PotPlayer Clone")
        self.setGeometry(100, 100, 1280, 720)
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        self._create_main_layout()
        self.media_player = MediaPlayer(self.video_display)
        self._connect_controls()
        self._init_timer()

    def _init_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()

    def update_ui(self):
        if self.media_player.is_playing():
            position = self.media_player.get_position()
            self.controls.seek_slider.blockSignals(True)
            self.controls.seek_slider.setValue(int(position * 100))
            self.controls.seek_slider.blockSignals(False)
            current_time = self.media_player.get_time() / 1000
            duration = self.media_player.get_duration() / 1000
            self.statusBar().showMessage(f"{current_time:.1f}s / {duration:.1f}s")

    def _connect_controls(self):
        self.controls.play_btn.clicked.connect(self.play_media)
        self.controls.pause_btn.clicked.connect(self.pause_media)
        self.controls.stop_btn.clicked.connect(self.stop_media)
        self.controls.volume_slider.valueChanged.connect(self.change_volume)
        self.controls.seek_slider.sliderReleased.connect(self.seek_position)

    def play_media(self):
        self.media_player.play()
        self.statusBar().showMessage("Playing...")

    def pause_media(self):
        self.media_player.pause()
        self.statusBar().showMessage("Paused")

    def stop_media(self):
        self.media_player.stop()
        self.statusBar().showMessage("Stopped")

    def change_volume(self, value):
        self.media_player.set_volume(value)
        self.statusBar().showMessage(f"Volume: {value}%")

    def seek_position(self):
        position = self.controls.seek_slider.value() / 100.0
        self.media_player.set_position(position)
        self.statusBar().showMessage(f"Seek: {int(position * 100)}%")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Media File")
        if file_path:
            self.statusBar().showMessage(f"Loaded: {file_path}")
            self.video_display.play(file_path)
            self.playlist.add_item(file_path)
            self.media_player.set_media(file_path)
            self.media_player.play()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            if self.media_player.is_playing():
                self.media_player.pause()
            else:
                self.media_player.play()
        elif event.key() == Qt.Key.Key_Escape:
            self.showNormal()

# === LINE 1001 ===

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.load_and_play(file_path)

    def load_and_play(self, file_path):
        if file_path:
            self.statusBar().showMessage(f"Loaded: {file_path}")
            self.playlist.add_item(file_path)
            self.video_display.play(file_path)
            self.media_player.set_media(file_path)
            self.media_player.play()

    def add_subtitle(self, subtitle_path):
        if self.media_player.mediaplayer:
            self.media_player.mediaplayer.video_set_subtitle_file(subtitle_path)
            self.statusBar().showMessage(f"Subtitle loaded: {subtitle_path}")

    def open_subtitle_file(self):
        subtitle_path, _ = QFileDialog.getOpenFileName(self, "Open Subtitle File", filter="Subtitle Files (*.srt *.sub *.ass)")
        if subtitle_path:
            self.add_subtitle(subtitle_path)

    def _create_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        file_menu = menubar.addMenu("&File")
        open_action = QAction("📂 Open File", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        subtitle_action = QAction("📝 Load Subtitle", self)
        subtitle_action.setShortcut("Ctrl+T")
        subtitle_action.triggered.connect(self.open_subtitle_file)
        file_menu.addAction(subtitle_action)

        exit_action = QAction("❌ Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("&View")
        toggle_playlist_action = QAction("📃 Toggle Playlist", self)
        toggle_playlist_action.setCheckable(True)
        toggle_playlist_action.setChecked(True)
        toggle_playlist_action.triggered.connect(self.toggle_playlist)
        view_menu.addAction(toggle_playlist_action)

        tools_menu = menubar.addMenu("&Tools")
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        tools_menu.addAction(settings_action)

        help_menu = menubar.addMenu("&Help")
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()

class SettingsDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Settings")
        self.setFixedSize(400, 300)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Settings panel placeholder.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

class PlaylistWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel("📂 Playlist")
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.item_double_clicked)

        layout.addWidget(self.label)
        layout.addWidget(self.list_widget)

    def add_item(self, file_path):
        if not self.contains(file_path):
            self.list_widget.addItem(file_path)

    def contains(self, path):
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).text() == path:
                return True
        return False

    def item_double_clicked(self, item):
        file_path = item.text()
        main_window = self.window()
        if isinstance(main_window, MainWindow):
            main_window.load_and_play(file_path)

class PlaybackControls(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.play_btn = QPushButton("▶️")
        self.pause_btn = QPushButton("⏸")
        self.stop_btn = QPushButton("⏹")
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)

        self.play_btn.setToolTip("Play")
        self.pause_btn.setToolTip("Pause")
        self.stop_btn.setToolTip("Stop")
        self.seek_slider.setToolTip("Seek")
        self.volume_slider.setToolTip("Volume")

        self.play_btn.setFixedWidth(40)
        self.pause_btn.setFixedWidth(40)
        self.stop_btn.setFixedWidth(40)

        layout.addWidget(self.play_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(QLabel("Seek:"))
        layout.addWidget(self.seek_slider)
        layout.addWidget(QLabel("Volume:"))
        layout.addWidget(self.volume_slider)

class VideoDisplay(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background-color: black;")
        layout.addWidget(self.label)

    def mouseDoubleClickEvent(self, event):
        self.toggle_fullscreen()

    def toggle_fullscreen(self):
        parent = self.window()
        if parent.isFullScreen():
            parent.showNormal()
        else:
            parent.showFullScreen()

    def play(self, file_path):
        self.label.setText(f"<span style='color:white;'>▶️ {file_path}</span>")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PotPlayer Clone")
    app.setStyle("Fusion")

    window = MainWindow()
    window.setAcceptDrops(True)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# === LINE 1501 ===

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        open_btn = QAction("Open", self)
        open_btn.triggered.connect(self.open_file)
        toolbar.addAction(open_btn)

        subtitle_btn = QAction("Subtitle", self)
        subtitle_btn.triggered.connect(self.open_subtitle_file)
        toolbar.addAction(subtitle_btn)

        screenshot_btn = QAction("📸 Screenshot", self)
        screenshot_btn.triggered.connect(self.take_screenshot)
        toolbar.addAction(screenshot_btn)

        loop_btn = QAction("🔁 Loop", self)
        loop_btn.setCheckable(True)
        loop_btn.setChecked(False)
        loop_btn.triggered.connect(self.toggle_loop)
        toolbar.addAction(loop_btn)

        shuffle_btn = QAction("🔀 Shuffle", self)
        shuffle_btn.setCheckable(True)
        shuffle_btn.setChecked(False)
        shuffle_btn.triggered.connect(self.toggle_shuffle)
        toolbar.addAction(shuffle_btn)

        save_playlist_btn = QAction("💾 Save Playlist", self)
        save_playlist_btn.triggered.connect(self.save_playlist)
        toolbar.addAction(save_playlist_btn)

        load_playlist_btn = QAction("📂 Load Playlist", self)
        load_playlist_btn.triggered.connect(self.load_playlist)
        toolbar.addAction(load_playlist_btn)

    def toggle_loop(self, checked):
        self.loop_enabled = checked
        self.statusBar().showMessage(f"Loop {'enabled' if checked else 'disabled'}")

    def toggle_shuffle(self, checked):
        self.shuffle_enabled = checked
        self.statusBar().showMessage(f"Shuffle {'enabled' if checked else 'disabled'}")

    def take_screenshot(self):
        import time
        screenshot_time = time.strftime("%Y%m%d-%H%M%S")
        file_path = f"screenshot_{screenshot_time}.png"
        if self.video_display:
            pixmap = self.video_display.grab()
            pixmap.save(file_path)
            self.statusBar().showMessage(f"Screenshot saved: {file_path}")

    def save_playlist(self):
        import json
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Playlist", filter="JSON (*.json)")
        if file_path:
            items = []
            for i in range(self.playlist.list_widget.count()):
                items.append(self.playlist.list_widget.item(i).text())
            with open(file_path, 'w') as f:
                json.dump(items, f)
            self.statusBar().showMessage(f"Playlist saved: {file_path}")

    def load_playlist(self):
        import json
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Playlist", filter="JSON (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    items = json.load(f)
                self.playlist.list_widget.clear()
                for item in items:
                    self.playlist.add_item(item)
                self.statusBar().showMessage(f"Playlist loaded: {file_path}")
            except Exception as e:
                self.statusBar().showMessage(f"Failed to load playlist: {e}")

    def media_finished(self):
        if self.loop_enabled:
            self.media_player.set_position(0)
            self.media_player.play()
        elif self.shuffle_enabled:
            import random
            count = self.playlist.list_widget.count()
            if count > 0:
                index = random.randint(0, count - 1)
                item = self.playlist.list_widget.item(index)
                self.load_and_play(item.text())
        else:
            current = self.get_current_playlist_index()
            if current is not None and current + 1 < self.playlist.list_widget.count():
                next_item = self.playlist.list_widget.item(current + 1)
                self.load_and_play(next_item.text())

    def get_current_playlist_index(self):
        current_file = self.video_display.label.text()
        for i in range(self.playlist.list_widget.count()):
            if self.playlist.list_widget.item(i).text() in current_file:
                return i
        return None

    def _init_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()

        self.end_check_timer = QTimer(self)
        self.end_check_timer.setInterval(1000)
        self.end_check_timer.timeout.connect(self.check_end)
        self.end_check_timer.start()

    def check_end(self):
        if self.media_player:
            state = self.media_player.mediaplayer.get_state()
            if state == vlc.State.Ended:
                self.media_finished()

# SettingsDialog: extend with theme toggle
class SettingsDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Settings")
        self.setFixedSize(400, 300)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.theme_label = QLabel("Choose Theme:")
        layout.addWidget(self.theme_label)

        self.dark_btn = QPushButton("🌙 Dark")
        self.light_btn = QPushButton("☀️ Light")
        layout.addWidget(self.dark_btn)
        layout.addWidget(self.light_btn)

        self.dark_btn.clicked.connect(self.set_dark)
        self.light_btn.clicked.connect(self.set_light)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def set_dark(self):
        self.parent().apply_theme("dark")

    def set_light(self):
        self.parent().apply_theme("light")

# Add theme method to main window
class MainWindow(QMainWindow):
    def apply_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #2d2d2d; color: white; }
                QLabel, QPushButton, QListWidget, QSlider { color: white; }
            """)
            self.statusBar().showMessage("Theme: Dark")
        elif theme_name == "light":
            self.setStyleSheet("")
            self.statusBar().showMessage("Theme: Light")

# Drag file support setup
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PotPlayer Clone")
    app.setStyle("Fusion")

    window = MainWindow()
    window.setAcceptDrops(True)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
# === LINE 2001 ===

import json
from pathlib import Path

CONFIG_FILE = Path("config.json")

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle("🎞 PotPlayer Clone")
        self.setGeometry(100, 100, 1280, 720)

        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        self._create_main_layout()

        self.media_player = MediaPlayer(self.video_display)
        self._connect_controls()
        self._init_timer()

        self.loop_enabled = False
        self.shuffle_enabled = False
        self.playback_rate = 1.0
        self.subtitle_delay = 0

        self.load_user_settings()
        self.installEventFilter(self)

    def load_user_settings(self):
        theme = self.config.get("theme", "light")
        self.apply_theme(theme)

    def save_user_settings(self):
        self.config["theme"] = "dark" if "background-color: #2d2d2d" in self.styleSheet() else "light"
        save_config(self.config)

    def closeEvent(self, event):
        self.save_user_settings()
        super().closeEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Plus:
                self.change_speed(0.1)
            elif key == Qt.Key.Key_Minus:
                self.change_speed(-0.1)
            elif key == Qt.Key.Key_BracketLeft:
                self.adjust_subtitle_delay(-500)
            elif key == Qt.Key.Key_BracketRight:
                self.adjust_subtitle_delay(500)
        return super().eventFilter(obj, event)

    def change_speed(self, delta):
        self.playback_rate += delta
        self.media_player.mediaplayer.set_rate(self.playback_rate)
        self.statusBar().showMessage(f"Speed: {self.playback_rate:.1f}x")

    def adjust_subtitle_delay(self, ms):
        self.subtitle_delay += ms
        if self.media_player.mediaplayer:
            self.media_player.mediaplayer.set_spu_delay(self.subtitle_delay * 1000)
        self.statusBar().showMessage(f"Subtitle delay: {self.subtitle_delay} ms")

class HotkeyManager:
    def __init__(self):
        self.bindings = {
            "play_pause": Qt.Key.Key_Space,
            "stop": Qt.Key.Key_S,
            "screenshot": Qt.Key.Key_F12,
            "speed_up": Qt.Key.Key_Plus,
            "speed_down": Qt.Key.Key_Minus,
        }

    def get_key(self, action):
        return self.bindings.get(action, None)

    def set_key(self, action, qt_key):
        self.bindings[action] = qt_key

    def save(self):
        with open("hotkeys.json", "w") as f:
            json.dump({k: int(v) for k, v in self.bindings.items()}, f)

    def load(self):
        try:
            with open("hotkeys.json", "r") as f:
                raw = json.load(f)
                self.bindings = {k: Qt.Key(key) for k, key in raw.items()}
        except Exception:
            pass

class NowPlayingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.label = QLabel("", self)
        self.label.setStyleSheet("color: white; background-color: rgba(0,0,0,160); font-size: 16px; padding: 8px;")
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.hide()

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def show_message(self, text, duration=3000):
        self.label.setText(text)
        self.adjustSize()
        self.move(
            self.parent().geometry().center() - self.rect().center()
        )
        self.show()
        self.timer.start(duration)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle("🎞 PotPlayer Clone")
        self.setGeometry(100, 100, 1280, 720)

        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        self._create_main_layout()

        self.media_player = MediaPlayer(self.video_display)
        self.overlay = NowPlayingOverlay(self)
        self.hotkeys = HotkeyManager()
        self.hotkeys.load()

        self._connect_controls()
        self._init_timer()

        self.loop_enabled = False
        self.shuffle_enabled = False
        self.playback_rate = 1.0
        self.subtitle_delay = 0

        self.load_user_settings()
        self.installEventFilter(self)

    def load_and_play(self, file_path):
        if file_path:
            self.statusBar().showMessage(f"Loaded: {file_path}")
            self.playlist.add_item(file_path)
            self.video_display.play(file_path)
            self.media_player.set_media(file_path)
            self.media_player.play()
            self.overlay.show_message(f"🎵 Now Playing:\n{Path(file_path).name}")

    def keyPressEvent(self, event):
        key = event.key()
        if key == self.hotkeys.get_key("play_pause"):
            if self.media_player.is_playing():
                self.media_player.pause()
            else:
                self.media_player.play()
        elif key == self.hotkeys.get_key("stop"):
            self.media_player.stop()
        elif key == self.hotkeys.get_key("screenshot"):
            self.take_screenshot()
        elif key == self.hotkeys.get_key("speed_up"):
            self.change_speed(0.1)
        elif key == self.hotkeys.get_key("speed_down"):
            self.change_speed(-0.1)

    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_BracketLeft:
                self.adjust_subtitle_delay(-500)
            elif event.key() == Qt.Key.Key_BracketRight:
                self.adjust_subtitle_delay(500)
        return super().eventFilter(obj, event)

# === LINE 2501 ===

class HotkeySettingsDialog(QWidget):
    def __init__(self, hotkey_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⌨️ Hotkey Settings")
        self.setFixedSize(400, 400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.hotkey_manager = hotkey_manager
        self.layout = QVBoxLayout(self)

        self.instructions = QLabel("Click a button, then press a key to rebind.")
        self.layout.addWidget(self.instructions)

        self.buttons = {}
        for action in hotkey_manager.bindings:
            btn = QPushButton(f"{action}: {QKeySequence(hotkey_manager.bindings[action]).toString()}")
            btn.clicked.connect(lambda _, a=action, b=btn: self.rebind_key(a, b))
            self.layout.addWidget(btn)
            self.buttons[action] = btn

        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save)
        self.layout.addWidget(save_btn)

        self.rebinding = None

    def rebind_key(self, action, button):
        self.rebinding = (action, button)
        button.setText(f"{action}: [Press Key]")

    def keyPressEvent(self, event):
        if self.rebinding:
            action, button = self.rebinding
            key = event.key()
            self.hotkey_manager.set_key(action, key)
            button.setText(f"{action}: {QKeySequence(key).toString()}")
            self.rebinding = None

    def save(self):
        self.hotkey_manager.save()
        self.close()

# Add to settings dialog
class SettingsDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Settings")
        self.setFixedSize(400, 400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.theme_label = QLabel("Choose Theme:")
        layout.addWidget(self.theme_label)

        self.dark_btn = QPushButton("🌙 Dark")
        self.light_btn = QPushButton("☀️ Light")
        layout.addWidget(self.dark_btn)
        layout.addWidget(self.light_btn)

        self.color_picker_btn = QPushButton("🎨 Custom Theme Color")
        layout.addWidget(self.color_picker_btn)

        self.hotkey_btn = QPushButton("⌨️ Hotkey Settings")
        layout.addWidget(self.hotkey_btn)

        self.dark_btn.clicked.connect(self.set_dark)
        self.light_btn.clicked.connect(self.set_light)
        self.color_picker_btn.clicked.connect(self.custom_color)
        self.hotkey_btn.clicked.connect(self.open_hotkey_dialog)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def set_dark(self):
        self.parent().apply_theme("dark")

    def set_light(self):
        self.parent().apply_theme("light")

    def custom_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.parent().apply_custom_theme(color.name())

    def open_hotkey_dialog(self):
        dialog = HotkeySettingsDialog(self.parent().hotkeys, self)
        dialog.show()

class MainWindow(QMainWindow):
    def apply_custom_theme(self, color_hex):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {color_hex}; color: white; }}
            QLabel, QPushButton, QListWidget, QSlider {{ color: white; }}
        """)
        self.config["theme"] = "custom"
        self.config["theme_color"] = color_hex

    def apply_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #2d2d2d; color: white; }
                QLabel, QPushButton, QListWidget, QSlider { color: white; }
            """)
        elif theme_name == "light":
            self.setStyleSheet("")
        elif theme_name == "custom":
            color = self.config.get("theme_color", "#333333")
            self.apply_custom_theme(color)

# A–B Loop logic
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.a_point = None
        self.b_point = None
        self.history = []
        # ... (rest already initialized)

    def set_a_point(self):
        if self.media_player:
            self.a_point = self.media_player.get_time()
            self.statusBar().showMessage(f"A point set at {self.a_point // 1000:.2f}s")

    def set_b_point(self):
        if self.media_player:
            self.b_point = self.media_player.get_time()
            self.statusBar().showMessage(f"B point set at {self.b_point // 1000:.2f}s")

    def check_ab_loop(self):
        if self.a_point is not None and self.b_point is not None:
            current_time = self.media_player.get_time()
            if current_time >= self.b_point:
                self.media_player.set_position(self.a_point / self.media_player.get_duration())

    def _init_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()

        self.ab_timer = QTimer(self)
        self.ab_timer.setInterval(300)
        self.ab_timer.timeout.connect(self.check_ab_loop)
        self.ab_timer.start()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_A:
            self.set_a_point()
        elif event.key() == Qt.Key.Key_B:
            self.set_b_point()

# Playback history
class HistoryManager:
    def __init__(self, file="history.json"):
        self.file = Path(file)
        self.history = self.load()

    def add_entry(self, path):
        from datetime import datetime
        entry = {"file": path, "time": datetime.now().isoformat()}
        self.history.insert(0, entry)
        self.history = self.history[:50]
        self.save()

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.history, f, indent=2)

    def load(self):
        if self.file.exists():
            with open(self.file, "r") as f:
                return json.load(f)
        return []

    def get_entries(self):
        return self.history

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.history_manager = HistoryManager()
        # ... continue from init

    def load_and_play(self, file_path):
        if file_path:
            self.statusBar().showMessage(f"Loaded: {file_path}")
            self.playlist.add_item(file_path)
            self.video_display.play(file_path)
            self.media_player.set_media(file_path)
            self.media_player.play()
            self.overlay.show_message(f"🎵 Now Playing:\n{Path(file_path).name}")
            self.history_manager.add_entry(file_path)

# Foundation for plugin system
class Plugin:
    def __init__(self, name):
        self.name = name

    def load(self, main_window):
        pass

class PluginManager:
    def __init__(self):
        self.plugins = []

    def register(self, plugin: Plugin):
        self.plugins.append(plugin)

    def load_all(self, main_window):
        for plugin in self.plugins:
            plugin.load(main_window)

# Example Plugin
class ExampleGreetingPlugin(Plugin):
    def load(self, main_window):
        main_window.statusBar().showMessage("👋 Hello from plugin!")

# Plugin loading
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.plugin_manager = PluginManager()
        self.plugin_manager.register(ExampleGreetingPlugin("Greeting"))
        self.plugin_manager.load_all(self)
# === LINE 3001 ===

class HistoryViewer(QWidget):
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📜 Playback History")
        self.setFixedSize(400, 500)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.history_manager = history_manager

        self.load_history()

        self.list_widget.itemDoubleClicked.connect(self.play_selected)

        layout.addWidget(self.list_widget)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def load_history(self):
        self.list_widget.clear()
        for item in self.history_manager.get_entries():
            text = f"{Path(item['file']).name} - {item['time']}"
            self.list_widget.addItem(text)

    def play_selected(self, item):
        index = self.list_widget.row(item)
        entry = self.history_manager.get_entries()[index]
        self.parent().load_and_play(entry["file"])
        self.close()

class SettingsDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... existing widgets ...
        self.history_btn = QPushButton("📜 View Playback History")
        self.layout().addWidget(self.history_btn)
        self.history_btn.clicked.connect(self.show_history)

    def show_history(self):
        dialog = HistoryViewer(self.parent().history_manager, self)
        dialog.show()

# Plugin auto-discovery
class PluginManager:
    def __init__(self, folder="plugins"):
        self.plugins = []
        self.folder = Path(folder)
        self.folder.mkdir(exist_ok=True)

    def discover_plugins(self):
        for file in self.folder.glob("*.py"):
            try:
                name = file.stem
                spec = importlib.util.spec_from_file_location(name, str(file))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, type) and issubclass(obj, Plugin) and obj is not Plugin:
                        instance = obj(name)
                        self.register(instance)
            except Exception as e:
                print(f"Failed to load plugin {file}: {e}")

    def load_all(self, main_window):
        self.discover_plugins()
        for plugin in self.plugins:
            plugin.load(main_window)

    def unload_all(self):
        self.plugins.clear()

# Auto-resume last played file
class ResumeManager:
    def __init__(self, file="resume.json"):
        self.file = Path(file)

    def save(self, path, position):
        with open(self.file, "w") as f:
            json.dump({"path": path, "position": position}, f)

    def load(self):
        if self.file.exists():
            with open(self.file, "r") as f:
                return json.load(f)
        return {}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resume_manager = ResumeManager()
        # ... other init code ...
        self.resume_last_play()

    def resume_last_play(self):
        resume_data = self.resume_manager.load()
        path = resume_data.get("path")
        pos = resume_data.get("position", 0)
        if path and Path(path).exists():
            self.load_and_play(path)
            QTimer.singleShot(1000, lambda: self.media_player.set_position(pos / self.media_player.get_duration()))

    def closeEvent(self, event):
        if self.media_player and self.media_player.get_duration() > 0:
            position = self.media_player.get_position()
            self.resume_manager.save(self.media_player.current_file, position * self.media_player.get_duration())
        self.save_user_settings()
        super().closeEvent(event)

# Bookmarking system
class BookmarkManager:
    def __init__(self, file="bookmarks.json"):
        self.file = Path(file)
        self.bookmarks = self.load()

    def add_bookmark(self, path, label, position):
        self.bookmarks.append({"file": path, "label": label, "position": position})
        self.save()

    def get_bookmarks(self):
        return self.bookmarks

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.bookmarks, f, indent=2)

    def load(self):
        if self.file.exists():
            with open(self.file, "r") as f:
                return json.load(f)
        return []

class BookmarkViewer(QWidget):
    def __init__(self, bookmarks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔖 Bookmarks")
        self.setFixedSize(400, 400)
        self.bookmarks = bookmarks
        self.parent_window = parent
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        layout.addWidget(self.list)
        for bm in self.bookmarks.get_bookmarks():
            self.list.addItem(f"{bm['label']} - {Path(bm['file']).name}")
        self.list.itemDoubleClicked.connect(self.goto_bookmark)

    def goto_bookmark(self, item):
        index = self.list.row(item)
        bm = self.bookmarks.get_bookmarks()[index]
        self.parent_window.load_and_play(bm["file"])
        QTimer.singleShot(1500, lambda: self.parent_window.media_player.set_position(bm["position"]))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bookmark_manager = BookmarkManager()
        # ... rest ...

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_M:
            self.create_bookmark()

    def create_bookmark(self):
        if self.media_player and self.media_player.current_file:
            position = self.media_player.get_position()
            label, ok = QInputDialog.getText(self, "Bookmark", "Label this bookmark:")
            if ok and label:
                self.bookmark_manager.add_bookmark(self.media_player.current_file, label, position)
                self.statusBar().showMessage(f"Bookmark '{label}' saved")

    def open_bookmarks(self):
        viewer = BookmarkViewer(self.bookmark_manager, self)
        viewer.show()

# Add bookmark button to settings
class SettingsDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ...
        self.bookmark_btn = QPushButton("🔖 View Bookmarks")
        self.layout().addWidget(self.bookmark_btn)
        self.bookmark_btn.clicked.connect(self.parent().open_bookmarks)

# Final plugin discovery integration
import importlib.util

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.plugin_manager = PluginManager()
        self.plugin_manager.discover_plugins()
        self.plugin_manager.load_all(self)
# === LINE 3501 ===

class EqualizerDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎚️ Audio Equalizer")
        self.setFixedSize(400, 300)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout(self)
        self.sliders = []

        self.labels = ["60Hz", "170Hz", "310Hz", "600Hz", "1kHz", "3kHz", "6kHz", "12kHz", "14kHz", "16kHz"]

        grid = QGridLayout()
        for i, label in enumerate(self.labels):
            lbl = QLabel(label)
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setRange(-10, 10)
            slider.setValue(0)
            self.sliders.append(slider)

            grid.addWidget(lbl, 0, i)
            grid.addWidget(slider, 1, i)

        layout.addLayout(grid)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_equalizer)
        layout.addWidget(apply_btn)

    def apply_equalizer(self):
        # Placeholder: Integrate with VLC or other engine later
        gains = [s.value() for s in self.sliders]
        print("Equalizer settings:", gains)
        self.close()

class MediaInfoDialog(QWidget):
    def __init__(self, media_player, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📊 Media Info")
        self.setFixedSize(400, 300)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        info = self.get_info(media_player)
        self.text_edit.setPlainText(info)

    def get_info(self, mp):
        try:
            media = mp.mediaplayer.get_media()
            media.parse()
            return (
                f"Title: {media.get_meta(0)}\n"
                f"Duration: {media.get_duration() // 1000}s\n"
                f"Tracks: {media.get_tracks_info()}\n"
                f"State: {mp.mediaplayer.get_state()}"
            )
        except Exception as e:
            return f"Error getting media info: {e}"

class MainWindow(QMainWindow):
    def open_equalizer(self):
        eq = EqualizerDialog(self)
        eq.show()

    def show_media_info(self):
        info = MediaInfoDialog(self.media_player, self)
        info.show()

# Add to menu or settings
class SettingsDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... previous widgets ...
        self.eq_btn = QPushButton("🎚️ Equalizer")
        self.info_btn = QPushButton("📊 Media Info")
        self.layout().addWidget(self.eq_btn)
        self.layout().addWidget(self.info_btn)
        self.eq_btn.clicked.connect(self.parent().open_equalizer)
        self.info_btn.clicked.connect(self.parent().show_media_info)

# Playlist filtering
class PlaylistWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)

    def filter(self, text):
        for i in range(self.count()):
            item = self.item(i)
            item.setHidden(text.lower() not in item.text().lower())

class PlaylistSearch(QWidget):
    def __init__(self, playlist_widget, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.label = QLabel("🔍 Search:")
        self.input = QLineEdit()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        self.playlist = playlist_widget
        self.input.textChanged.connect(self.playlist.filter)

# Integrate playlist search into main layout
class MainWindow(QMainWindow):
    def _create_main_layout(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.video_display = VideoDisplay()
        layout.addWidget(self.video_display, 8)

        self.playlist = PlaylistWidget()
        self.playlist_search = PlaylistSearch(self.playlist)
        layout.addWidget(self.playlist_search)
        layout.addWidget(self.playlist, 2)

# Streaming URL support
class MainWindow(QMainWindow):
    def open_stream_dialog(self):
        url, ok = QInputDialog.getText(self, "🌍 Open Stream", "Enter streaming URL:")
        if ok and url:
            self.stream_url(url)

    def stream_url(self, url):
        self.media_player.set_media(url)
        self.media_player.play()
        self.overlay.show_message(f"📡 Streaming: {url}")
        self.statusBar().showMessage("Streaming started")

# Add to toolbar/menu
class MainWindow(QMainWindow):
    def _create_toolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        stream_btn = QAction("🌐 Stream", self)
        stream_btn.triggered.connect(self.open_stream_dialog)
        toolbar.addAction(stream_btn)

# Mini player
class MiniPlayer(QMainWindow):
    def __init__(self, media_player):
        super().__init__()
        self.setWindowTitle("🪟 Mini Player")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setGeometry(100, 100, 300, 200)

        self.video_display = VideoDisplay()
        self.media_player = media_player
        self.media_player.set_video_widget(self.video_display)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.video_display)

        btn = QPushButton("🔙 Return to Full Player")
        btn.clicked.connect(self.return_to_main)
        layout.addWidget(btn)

        self.setCentralWidget(central)

    def return_to_main(self):
        self.hide()
        self.media_player.set_video_widget(self.parent().video_display)
        self.parent().show()

class MainWindow(QMainWindow):
    def toggle_mini_player(self):
        self.mini_player = MiniPlayer(self.media_player)
        self.mini_player.setParent(self)
        self.mini_player.show()
        self.hide()

# Add button or key to activate mini player
class MainWindow(QMainWindow):
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_N:
            self.toggle_mini_player()

# Optional: button in toolbar/menu
class MainWindow(QMainWindow):
    def _create_toolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        mini_btn = QAction("🪟 Mini Player", self)
        mini_btn.triggered.connect(self.toggle_mini_player)
        toolbar.addAction(mini_btn)

        stream_btn = QAction("🌐 Stream", self)
        stream_btn.triggered.connect(self.open_stream_dialog)
        toolbar.addAction(stream_btn)

# Tooltips for accessibility
class MainWindow(QMainWindow):
    def _create_toolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        for action in toolbar.actions():
            action.setToolTip(action.text())
# === LINE 4001 ===

# Drag and drop support for files and folders
class PlaylistWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if Path(path).is_dir():
                self.add_directory(path)
            elif Path(path).is_file():
                self.add_file(path)

    def add_directory(self, directory):
        for file in Path(directory).glob("*"):
            if file.suffix in [".mp4", ".avi", ".mkv", ".mov"]:
                self.addItem(str(file))

    def add_file(self, file):
        if Path(file).suffix in [".mp4", ".avi", ".mkv", ".mov"]:
            self.addItem(file)

# Stop playback when a video ends
class MediaPlayer(QMediaPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stateChanged.connect(self.handle_state_change)

    def handle_state_change(self, state):
        if state == QMediaPlayer.State.StoppedState:
            if not self.media():
                self.player_reached_end()

    def player_reached_end(self):
        # Pause, reset, or trigger any end-of-media functionality
        self.setPosition(0)
        self.pause()
        self.parent().statusBar().showMessage("Video playback finished")

# Advanced subtitle settings dialog
class SubtitleSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎭 Subtitle Settings")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_size_slider.setRange(10, 50)
        self.font_size_slider.setValue(20)

        self.color_btn = QPushButton("Choose Subtitle Color")
        self.color_btn.clicked.connect(self.choose_color)

        layout.addWidget(QLabel("Subtitle Font Size:"))
        layout.addWidget(self.font_size_slider)
        layout.addWidget(self.color_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(apply_btn)

        self.subtitle_color = QColor(255, 255, 255)  # Default white

    def choose_color(self):
        color = QColorDialog.getColor(self.subtitle_color, self)
        if color.isValid():
            self.subtitle_color = color

    def apply_settings(self):
        size = self.font_size_slider.value()
        self.parent().media_player.set_subtitle_settings(size, self.subtitle_color)
        self.close()

# Media player with subtitle customization
class MediaPlayer(QMediaPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.subtitle_size = 20  # Default subtitle size
        self.subtitle_color = QColor(255, 255, 255)  # Default subtitle color

    def set_subtitle_settings(self, size, color):
        self.subtitle_size = size
        self.subtitle_color = color
        # Apply settings to the media player’s subtitle rendering system

# PiP (Picture-in-Picture) Overlay Mode
class PiPWindow(QMainWindow):
    def __init__(self, media_player):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setGeometry(100, 100, 300, 200)

        self.media_player = media_player
        self.video_display = VideoDisplay()

        self.media_player.set_video_widget(self.video_display)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.video_display)

        self.setCentralWidget(central)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

class MainWindow(QMainWindow):
    def open_pip_window(self):
        pip_window = PiPWindow(self.media_player)
        pip_window.show()

# Capture current frame and save as GIF
class FrameCapture(QThread):
    def __init__(self, media_player, parent=None):
        super().__init__(parent)
        self.media_player = media_player

    def run(self):
        frame = self.media_player.capture_frame()
        gif_path = str(Path.home() / "captured_frame.gif")
        frame.save(gif_path, format="GIF")
        self.parent().statusBar().showMessage(f"Frame captured and saved to {gif_path}")

# Integrating frame capture into the main UI
class MainWindow(QMainWindow):
    def capture_frame(self):
        capture_thread = FrameCapture(self.media_player, self)
        capture_thread.start()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_F:
            self.capture_frame()

# Tooltips for additional media controls
class MainWindow(QMainWindow):
    def _create_toolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        # PiP button
        pip_btn = QAction("🪞 PiP Mode", self)
        pip_btn.triggered.connect(self.open_pip_window)
        toolbar.addAction(pip_btn)

        # Subtitle Settings button
        subtitle_btn = QAction("🎭 Subtitles", self)
        subtitle_btn.triggered.connect(self.open_subtitle_settings)
        toolbar.addAction(subtitle_btn)

        # Capture frame button
        capture_btn = QAction("📸 Capture Frame", self)
        capture_btn.triggered.connect(self.capture_frame)
        toolbar.addAction(capture_btn)

    def open_subtitle_settings(self):
        settings = SubtitleSettingsDialog(self)
        settings.show()
# === LINE 4501 ===

# Advanced plugin system
class Plugin:
    def initialize(self):
        pass

    def on_media_play(self, media_player):
        pass

    def on_media_stop(self, media_player):
        pass

class PluginManager:
    def __init__(self):
        self.plugins = []

    def load_plugin(self, plugin_class):
        plugin = plugin_class()
        plugin.initialize()
        self.plugins.append(plugin)
        return plugin

    def on_media_play(self, media_player):
        for plugin in self.plugins:
            plugin.on_media_play(media_player)

    def on_media_stop(self, media_player):
        for plugin in self.plugins:
            plugin.on_media_stop(media_player)

# Example plugin
class CustomPlugin(Plugin):
    def initialize(self):
        print("Custom plugin initialized")

    def on_media_play(self, media_player):
        print("Custom plugin activated during play")

# Plugin integration into Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.plugin_manager = PluginManager()

        # Load a custom plugin
        self.plugin_manager.load_plugin(CustomPlugin)

    def media_play(self):
        # Simulate play functionality
        self.plugin_manager.on_media_play(self.media_player)

# Custom skinning and themes
class ThemeManager:
    def __init__(self):
        self.current_theme = "light"

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        if theme_name == "dark":
            QApplication.setStyle(QStyleFactory.create("Fusion"))
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.white)
            QApplication.setPalette(palette)
        else:
            QApplication.setStyle(QStyleFactory.create("Fusion"))
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.black)
            QApplication.setPalette(palette)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()

        # Apply the light theme by default
        self.theme_manager.apply_theme("light")

    def toggle_theme(self):
        new_theme = "dark" if self.theme_manager.current_theme == "light" else "light"
        self.theme_manager.apply_theme(new_theme)

# Keyboard shortcuts for media control
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Player")
        self.setGeometry(100, 100, 800, 600)

        self.media_player = QMediaPlayer()
        self.setCentralWidget(QTextEdit("Media controls here"))
        self._create_keyboard_shortcuts()

    def _create_keyboard_shortcuts(self):
        # Play/Pause: Space key
        play_pause_shortcut = QShortcut(QKeySequence("Space"), self)
        play_pause_shortcut.activated.connect(self.toggle_play_pause)

        # Stop: S key
        stop_shortcut = QShortcut(QKeySequence("S"), self)
        stop_shortcut.activated.connect(self.stop_media)

        # Next: N key
        next_shortcut = QShortcut(QKeySequence("N"), self)
        next_shortcut.activated.connect(self.play_next_media)

        # Previous: P key
        previous_shortcut = QShortcut(QKeySequence("P"), self)
        previous_shortcut.activated.connect(self.play_previous_media)

    def toggle_play_pause(self):
        if self.media_player.state() == QMediaPlayer.State.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def stop_media(self):
        self.media_player.stop()

    def play_next_media(self):
        print("Next media")

    def play_previous_media(self):
        print("Previous media")

# Voice control integration (experimental)
import speech_recognition as sr

class VoiceControl:
    def __init__(self, media_player):
        self.media_player = media_player
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen_for_command(self):
        with self.microphone as source:
            print("Listening for voice command...")
            audio = self.recognizer.listen(source)
            try:
                command = self.recognizer.recognize_google(audio)
                self.process_command(command)
            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
            except sr.RequestError:
                print("Sorry, the voice service is down.")

    def process_command(self, command):
        if "play" in command.lower():
            self.media_player.play()
        elif "pause" in command.lower():
            self.media_player.pause()
        elif "stop" in command.lower():
            self.media_player.stop()
        elif "next" in command.lower():
            print("Playing next media...")
        elif "previous" in command.lower():
            print("Playing previous media...")

# Start voice control in background
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer()

        self.voice_control = VoiceControl(self.media_player)
        self.voice_control.listen_for_command()

# Hotkeys for PiP and mini-player
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Player with Hotkeys")
        self.setGeometry(100, 100, 800, 600)

        self.media_player = QMediaPlayer()
        self.mini_player = MiniPlayer(self.media_player)

        self._create_hotkeys()

    def _create_hotkeys(self):
        # PiP mode: Ctrl+P
        pip_hotkey = QShortcut(QKeySequence("Ctrl+P"), self)
        pip_hotkey.activated.connect(self.open_pip_window)

        # Mini Player mode: Ctrl+M
        mini_hotkey = QShortcut(QKeySequence("Ctrl+M"), self)
        mini_hotkey.activated.connect(self.open_mini_player)

    def open_pip_window(self):
        pip_window = PiPWindow(self.media_player)
        pip_window.show()

    def open_mini_player(self):
        self.mini_player.show()

# Optional: Add a button to toggle the theme
class MainWindow(QMainWindow):
    def _create_toolbar(self):
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        theme_toggle_btn = QAction("🌙 Toggle Theme", self)
        theme_toggle_btn.triggered.connect(self.toggle_theme)
        toolbar.addAction(theme_toggle_btn)
# === LINE 5001 ===

# Gesture control integration (using webcam or touchpad)
import cv2
import numpy as np

class GestureControl:
    def __init__(self, media_player):
        self.media_player = media_player
        self.cap = cv2.VideoCapture(0)  # Open the webcam
        self.is_playing = False

    def start_gesture_recognition(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Here, you would integrate more logic for hand gestures
            # For example, swipe gestures for play/pause, forward/backward control
            
            cv2.imshow("Gesture Control", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit gesture recognition
                break

        self.cap.release()
        cv2.destroyAllWindows()

# Advanced settings panel for audio, video, and performance settings
class SettingsPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Advanced Settings")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)
        
        # Audio settings
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.update_volume)

        # Video settings
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.valueChanged.connect(self.update_brightness)

        # Performance settings (for CPU, GPU usage)
        self.performance_slider = QSlider(Qt.Orientation.Horizontal)
        self.performance_slider.setRange(0, 100)
        self.performance_slider.setValue(50)
        self.performance_slider.valueChanged.connect(self.update_performance)

        layout.addWidget(QLabel("Volume"))
        layout.addWidget(self.volume_slider)
        layout.addWidget(QLabel("Brightness"))
        layout.addWidget(self.brightness_slider)
        layout.addWidget(QLabel("Performance"))
        layout.addWidget(self.performance_slider)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(apply_btn)

    def update_volume(self, value):
        self.parent().media_player.set_volume(value)

    def update_brightness(self, value):
        self.parent().media_player.set_brightness(value)

    def update_performance(self, value):
        self.parent().media_player.set_performance(value)

    def apply_settings(self):
        self.close()

# Customizable media controls (speed, volume, etc.)
class MediaControlPanel(QWidget):
    def __init__(self, media_player):
        super().__init__()
        self.media_player = media_player
        layout = QVBoxLayout(self)

        # Speed control
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)  # 100% normal speed
        self.speed_slider.valueChanged.connect(self.update_speed)

        # Volume control
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.update_volume)

        layout.addWidget(QLabel("Playback Speed"))
        layout.addWidget(self.speed_slider)
        layout.addWidget(QLabel("Volume"))
        layout.addWidget(self.volume_slider)

    def update_speed(self, value):
        speed = value / 100.0
        self.media_player.setPlaybackRate(speed)

    def update_volume(self, value):
        self.media_player.setVolume(value)

# File explorer for browsing and managing media libraries
class FileExplorer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📂 File Explorer")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout(self)

        self.file_list = QListView(self)
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())

        self.file_list.setModel(self.file_model)
        self.file_list.setRootIndex(self.file_model.index(QDir.rootPath()))

        layout.addWidget(self.file_list)

        select_btn = QPushButton("Select Media")
        select_btn.clicked.connect(self.select_media)
        layout.addWidget(select_btn)

    def select_media(self):
        selected_index = self.file_list.selectedIndexes()[0]
        selected_file = self.file_model.filePath(selected_index)
        print(f"Selected file: {selected_file}")
        self.parent().load_media(selected_file)

# Video or screen recording functionality
class ScreenRecorder:
    def __init__(self):
        self.fps = 20.0
        self.screen_size = (1920, 1080)  # Full screen resolution
        self.output_file = "output_video.mp4"
        self.codec = cv2.VideoWriter_fourcc(*'mp4v')

    def start_recording(self):
        out = cv2.VideoWriter(self.output_file, self.codec, self.fps, self.screen_size)
        while True:
            img = np.array(pyautogui.screenshot())
            frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            out.write(frame)

            cv2.imshow('Recording Screen', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to stop recording
                break

        out.release()
        cv2.destroyAllWindows()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.setWindowTitle("Advanced Media Player")
        self.setGeometry(100, 100, 800, 600)

        self.recording = False
        self.screen_recorder = ScreenRecorder()

        # Initialize gesture control
        self.gesture_control = GestureControl(self.media_player)

        # Start gesture recognition in the background (or in a separate thread)
        self.gesture_control.start_gesture_recognition()

    def start_screen_recording(self):
        if not self.recording:
            self.recording = True
            self.screen_recorder.start_recording()
        else:
            print("Already recording screen!")

# Integrate new media control panel into the main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.setWindowTitle("Media Player with Advanced Features")
        self.setGeometry(100, 100, 800, 600)

        # Custom media control panel
        self.media_control_panel = MediaControlPanel(self.media_player)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.media_control_panel)

        # File explorer button
        file_explorer_btn = QPushButton("Open File Explorer", self)
        file_explorer_btn.clicked.connect(self.open_file_explorer)
        self.layout.addWidget(file_explorer_btn)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def open_file_explorer(self):
        explorer = FileExplorer(self)
        explorer.show()

