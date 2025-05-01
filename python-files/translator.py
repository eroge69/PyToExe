# Yassin Voice Translator - Advanced AI-Powered Multilingual Speech Translator

import sys
import os
import json
import threading
import speech_recognition as sr
from gtts import gTTS
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QComboBox, QTextEdit, QMessageBox, QHBoxLayout, QCheckBox, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from deep_translator import GoogleTranslator
import subprocess

# Language mapping dictionary
LANG_CODES = {
    "arabic": "ar",
    "english": "en",
    "french": "fr",
    "spanish": "es",
    "portuguese (brazilian)": "pt"
}

HISTORY_FILE = "translation_history.json"
FIRST_RUN_FILE = "first_run_complete.txt"
REQUIRED_MODULES = ["speechrecognition", "gtts", "pyqt6", "deep_translator"]

class YassinTranslator(QWidget):
    def __init__(self):
        super().__init__()
        self.first_run_check()
        self.setWindowTitle("🌍 Yassin AI Voice Translator - Smart, Secure & Fast")
        self.setWindowIcon(QIcon("translator_icon.png"))
        self.setGeometry(100, 100, 800, 720)
        self.is_dark_mode = False
        self.save_audio = True
        self.history = []
        self.load_history()
        self.setup_ui()
        self.apply_light_mode()

    def first_run_check(self):
        if not os.path.exists(FIRST_RUN_FILE):
            missing_modules = [m for m in REQUIRED_MODULES if not self.module_exists(m)]
            if missing_modules:
                try:
                    for module in missing_modules:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                except Exception as e:
                    print(f"❌ Failed to install required module: {e}")
            with open(FIRST_RUN_FILE, 'w') as f:
                f.write("setup done")

    def module_exists(self, module_name):
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def setup_ui(self):
        self.layout = QVBoxLayout()

        self.title = QLabel("🎧 Yassin Translator - Speak | Type | Translate | Listen", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.layout.addWidget(self.title)

        # Instagram button
        self.instagram_button = QPushButton("📷 Instagram: @y1ssine_ttx", self)
        self.instagram_button.clicked.connect(lambda: os.system("start https://www.instagram.com/y1ssine_ttx/" if os.name == "nt" else "xdg-open https://www.instagram.com/y1ssine_ttx/"))
        self.layout.addWidget(self.instagram_button)

        lang_layout = QHBoxLayout()

        self.source_label = QLabel("From:")
        self.source_lang = QComboBox(self)
        self.source_lang.addItems(LANG_CODES.keys())

        self.target_label = QLabel("To:")
        self.target_lang = QComboBox(self)
        self.target_lang.addItems(LANG_CODES.keys())

        lang_layout.addWidget(self.source_label)
        lang_layout.addWidget(self.source_lang)
        lang_layout.addWidget(self.target_label)
        lang_layout.addWidget(self.target_lang)

        self.layout.addLayout(lang_layout)

        self.transcript_area = QTextEdit(self)
        self.transcript_area.setPlaceholderText("🎤 Voice/Text input and translations will appear here...")
        self.layout.addWidget(self.transcript_area)

        input_layout = QHBoxLayout()
        self.input_area = QTextEdit(self)
        self.input_area.setPlaceholderText("⌨️ Type text to translate or use the mic button...")
        self.input_area.textChanged.connect(self.live_translate_typing)
        input_layout.addWidget(self.input_area)

        self.mic_btn = QPushButton("🎤", self)
        self.mic_btn.setFixedWidth(40)
        self.mic_btn.clicked.connect(self.handle_voice_translation)
        input_layout.addWidget(self.mic_btn)

        self.layout.addLayout(input_layout)

        btn_layout = QHBoxLayout()

        self.voice_translate_btn = QPushButton("🎙️ Voice Translate", self)
        self.voice_translate_btn.clicked.connect(self.handle_voice_translation)
        btn_layout.addWidget(self.voice_translate_btn)

        self.text_translate_btn = QPushButton("💬 Translate Text Only", self)
        self.text_translate_btn.clicked.connect(self.handle_text_translation)
        btn_layout.addWidget(self.text_translate_btn)

        self.no_audio_checkbox = QCheckBox("🔇 Text Only Mode")
        self.no_audio_checkbox.stateChanged.connect(self.toggle_audio_mode)
        btn_layout.addWidget(self.no_audio_checkbox)

        self.layout.addLayout(btn_layout)

        self.history_btn = QPushButton("📜 View History", self)
        self.history_btn.clicked.connect(self.show_history)
        self.layout.addWidget(self.history_btn)

        self.mode_toggle = QCheckBox("🌗 Dark Mode")
        self.mode_toggle.stateChanged.connect(self.toggle_mode)
        self.layout.addWidget(self.mode_toggle)

        self.setLayout(self.layout)

    def toggle_audio_mode(self):
        self.save_audio = not self.no_audio_checkbox.isChecked()

    def apply_dark_mode(self):
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #ffffff; }
            QTextEdit { background-color: #1e1e1e; color: white; font-size: 14px; padding: 10px; border-radius: 8px; }
            QPushButton { background-color: #0078D7; color: white; font-size: 16px; padding: 10px; border-radius: 10px; }
            QComboBox, QLabel { color: white; }
        """)
        self.is_dark_mode = True

    def apply_light_mode(self):
        self.setStyleSheet("""
            QWidget { background-color: #f0f2f5; color: #000000; }
            QTextEdit { background-color: #ffffff; color: black; font-size: 14px; padding: 10px; border-radius: 8px; }
            QPushButton { background-color: #0078D7; color: white; font-size: 16px; padding: 10px; border-radius: 10px; }
            QComboBox, QLabel { color: black; }
        """)
        self.is_dark_mode = False

    def toggle_mode(self):
        if self.mode_toggle.isChecked():
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def handle_voice_translation(self):
        thread = threading.Thread(target=self.translate_voice)
        thread.start()

    def translate_voice(self):
        recognizer = sr.Recognizer()
        source_lang_key = self.source_lang.currentText()
        target_lang_key = self.target_lang.currentText()
        source_lang = LANG_CODES[source_lang_key]
        target_lang = LANG_CODES[target_lang_key]

        try:
            self.transcript_area.append("🔴 Listening... Speak now!")
            QApplication.processEvents()

            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            spoken_text = recognizer.recognize_google(audio, language=source_lang)
            self.transcript_area.append(f"🗣️ [{source_lang_key}] You said: {spoken_text}")

            translated = GoogleTranslator(source='auto', target=target_lang).translate(spoken_text)
            self.transcript_area.append(f"🌍 [{target_lang_key}] Translation: {translated}")
            self.save_translation(spoken_text, translated, source_lang_key, target_lang_key)

            if self.save_audio:
                tts = gTTS(translated, lang=target_lang)
                tts.save("translated.mp3")
                os.system("start translated.mp3" if os.name == "nt" else "afplay translated.mp3")

        except sr.UnknownValueError:
            self.transcript_area.append("❌ Could not understand audio")
        except sr.RequestError as e:
            self.transcript_area.append(f"⚠️ Could not request results: {e}")
        except Exception as ex:
            self.transcript_area.append(f"❗ Error: {str(ex)}")

    def handle_text_translation(self):
        source_lang_key = self.source_lang.currentText()
        target_lang_key = self.target_lang.currentText()
        target_lang = LANG_CODES[target_lang_key]
        typed_text = self.input_area.toPlainText().strip()

        if typed_text:
            try:
                translated = GoogleTranslator(source='auto', target=target_lang).translate(typed_text)
                self.transcript_area.append(f"⌨️ Typed: {typed_text}")
                self.transcript_area.append(f"🌍 Translation: {translated}")
                self.save_translation(typed_text, translated, source_lang_key, target_lang_key)

                if self.save_audio:
                    tts = gTTS(translated, lang=target_lang)
                    tts.save("translated.mp3")
                    os.system("start translated.mp3" if os.name == "nt" else "afplay translated.mp3")

            except Exception as ex:
                self.transcript_area.append(f"❗ Error during translation: {str(ex)}")

    def live_translate_typing(self):
        typed_text = self.input_area.toPlainText().strip()
        if typed_text:
            source_lang_key = self.source_lang.currentText()
            target_lang_key = self.target_lang.currentText()
            target_lang = LANG_CODES[target_lang_key]
            try:
                translated = GoogleTranslator(source='auto', target=target_lang).translate(typed_text)
                self.transcript_area.setPlainText(f"🌍 Live Translation: {translated}")
            except:
                pass

    def save_translation(self, original, translated, source_lang, target_lang):
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": source_lang,
            "to": target_lang,
            "original": original,
            "translated": translated
        }
        self.history.append(entry)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                self.history = json.load(f)

    def show_history(self):
        if self.history:
            text = "\n\n".join([f"🕒 {h['time']}\nFrom [{h['from']}]: {h['original']}\nTo [{h['to']}]: {h['translated']}" for h in self.history])
        else:
            text = "No history available."
        QMessageBox.information(self, "📜 Translation History", text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YassinTranslator()
    window.show()
    sys.exit(app.exec())
