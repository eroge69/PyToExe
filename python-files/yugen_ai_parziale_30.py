
# yugen_ai.py - Versione parziale (30%)
# Sistema base di Yūgen AI: struttura iniziale, GUI PyQt6, animazione iniziale, layout principale

import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedLayout, QFileDialog, QScrollArea
)
from PyQt6.QtGui import QFont, QMovie
from PyQt6.QtCore import Qt

# Cartelle e configurazione iniziale
def setup_directories():
    folders = ["models", "characters", "scripts", "output", "cache"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    if not os.path.exists("settings.json"):
        with open("settings.json", "w") as f:
            json.dump({"first_run": True}, f)

# GUI principale
class YugenAIApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yūgen AI")
        self.setStyleSheet("background-color: #1e1e1e; color: #d0d0d0;")
        self.resize(1024, 768)
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Logo iniziale animato
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie("assets/logo_animation.gif")  # deve essere nella cartella 'assets'
        self.logo.setMovie(self.movie)
        self.movie.start()
        self.main_layout.addWidget(self.logo)

        # Area script + video preview
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Inserisci la sceneggiatura...")
        self.editor.setFont(QFont("Times", 12))

        self.generate_button = QPushButton("Genera Video")
        self.generate_button.clicked.connect(self.generate_video)

        self.preview_label = QLabel("Anteprima Video")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray;")

        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Script"))
        left_panel.addWidget(self.editor)
        left_panel.addWidget(self.generate_button)

        right_panel = QVBoxLayout()
        right_panel.addWidget(self.preview_label)

        mid_layout = QHBoxLayout()
        mid_layout.addLayout(left_panel, 2)
        mid_layout.addLayout(right_panel, 3)

        self.main_layout.addLayout(mid_layout)

    def generate_video(self):
        script = self.editor.toPlainText()
        if script:
            with open("scripts/last_script.txt", "w", encoding="utf-8") as f:
                f.write(script)
            self.preview_label.setText("Video simulato generato.")
        else:
            self.preview_label.setText("Inserisci prima uno script.")

if __name__ == "__main__":
    setup_directories()
    app = QApplication(sys.argv)
    window = YugenAIApp()
    window.show()
    sys.exit(app.exec())
