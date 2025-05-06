import sys
import os
import json
import subprocess
import psutil
import time
import math
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMenu, QAction, QStackedWidget, QCheckBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor
from ping3 import ping
from pypresence import Presence

# === Discord Rich Presence ===
client_id = "1369255330776875039"
rpc = Presence(client_id)
rpc.connect()
rpc.update(state="Launcher geöffnet", details="Bereit für FiveM", large_image="fivem", start=time.time())

# === Funktionen ===
def find_fivem_path():
    possible_paths = [
        os.path.expandvars(r"%localappdata%\FiveM\FiveM.exe"),
        os.path.expandvars(r"%appdata%\CitizenFX\FiveM\FiveM.exe")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# === Overlay Fenster ===
class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(200, 120)
        self.move(50, 50)

        self.cpu = 0
        self.ram = 0
        self.ping_val = 0
        self.fps = 0

        self.frame_count = 0
        self.last_time = time.time()

        # Timer zum Aktualisieren der Systemdaten
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.update_data)
        self.data_timer.start(1000)

        # Timer zum Neuzeichnen (für FPS)
        self.repaint_timer = QTimer()
        self.repaint_timer.timeout.connect(self.update_fps)
        self.repaint_timer.start(16)  # ~60 FPS

    def update_data(self):
        self.cpu = psutil.cpu_percent()
        self.ram = psutil.virtual_memory().percent
        self.ping_val = int(ping("google.com", unit='ms') or 0)

    def update_fps(self):
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_time
        if elapsed >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_time = current_time
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 160))
        painter.drawRoundedRect(self.rect(), 10, 10)

        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Consolas", 10))
        painter.drawText(10, 40, f"CPU: {self.cpu}%")
        painter.drawText(10, 60, f"RAM: {self.ram}%")
        painter.drawText(10, 80, f"Ping: {self.ping_val}ms")
        painter.drawText(10, 20, f"FPS: {self.fps}")


# === Hauptlauncher ===
class Launcher(QWidget):
    def __init__(self):
        super().__init__()

        self.overlay_window = None

        self.setWindowTitle("FiveM Launcher")
        self.setFixedSize(500, 500)
        self.setStyleSheet("background-color: #222; color: white;")

        self.main_layout = QHBoxLayout(self)

        # Seitenleiste
        sidebar = QVBoxLayout()
        self.news_btn = QPushButton("📰 News")
        self.settings_btn = QPushButton("⚙️ Einstellungen")
        for btn in [self.news_btn, self.settings_btn]:
            btn.setStyleSheet("background: #333; color: white; padding: 10px;")
            sidebar.addWidget(btn)
        sidebar.addStretch()
        self.main_layout.addLayout(sidebar)

        # Inhalt
        self.pages = QStackedWidget()
        self.page_news = QLabel("📰 Willkommen im Newsbereich")
        self.page_news.setAlignment(Qt.AlignCenter)
        self.page_settings = QWidget()
        settings_layout = QVBoxLayout(self.page_settings)

        self.overlay_checkbox = QCheckBox("Overlay (FPS, CPU, RAM) anzeigen")
        self.overlay_checkbox.setChecked(True)
        settings_layout.addWidget(self.overlay_checkbox)

        settings_layout.addStretch()
        self.pages.addWidget(self.page_news)
        self.pages.addWidget(self.page_settings)

        self.main_layout.addWidget(self.pages)

        self.status_label = QLabel("Bereit zum Spielen")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; font-size: 16px;")

        self.play_button = QPushButton("🎮 Spielen")
        self.play_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 15px;")
        self.play_button.clicked.connect(self.start_game)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.status_label)
        right_layout.addWidget(self.play_button)
        right_layout.addStretch()
        self.main_layout.addLayout(right_layout)

        # Verbindungen
        self.news_btn.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.settings_btn.clicked.connect(lambda: self.pages.setCurrentIndex(1))

    def start_game(self):
        if self.overlay_checkbox.isChecked():
            if not self.overlay_window:
                self.overlay_window = OverlayWindow()
            self.overlay_window.show()

        fivem_path = find_fivem_path()
        if fivem_path:
            subprocess.Popen(f'"{fivem_path}"')
            self.status_label.setText("Spiel wird gestartet...")
        else:
            self.status_label.setText("❌ FiveM nicht gefunden!")


def main():
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
