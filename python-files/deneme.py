
# ///// OTO KUTUPHANE İNDİRME SİSTEMİ ///////

import sys
import subprocess
import importlib
import os
import time
from PyQt5.QtWidgets import QMessageBox, QApplication

# YAZILARI TEMİZLE (HER SİSTEM İCİN  | CLS-CLEAR-NT)
os.system('cls' if os.name == 'nt' else 'clear')

def install_module(module_name, display_name=None):
# KÜTÜPHANE KONTROLÜ
    try:
        importlib.import_module(module_name)
        print(f"{display_name or module_name} zaten yüklü.")
    except ImportError:
        print(f"{display_name or module_name} yükleniyor...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", module_name], check=True)
            print(f"{display_name or module_name} başarıyla yüklendi.")
        except subprocess.CalledProcessError as e:
            print(f"{display_name or module_name} yüklenirken hata: {e}")
            raise

def install_required_modules():
    app = QApplication(sys.argv) 
    msg = QMessageBox()
    msg.setWindowTitle("Bilgi")
    msg.setText("Kütüphaneler İndiriliyor...\nLütfen bekleyin.")
    msg.setStandardButtons(QMessageBox.NoButton)
    msg.show()
    QApplication.processEvents() 

    modules = [
        ("requests", "requests"),
        ("pyperclip", "pyperclip"),
        ("PyQt5", "PyQt5")
    ]
    
    for module_name, display_name in modules:
        install_module(module_name, display_name)
    
    msg.close()
    print("Tüm Kütüphaneler yüklendi.")

install_required_modules() 

time.sleep(0.9)

# YAZILARI TEMİZLE (HER SİSTEM İCİN  | CLS-CLEAR-NT)
os.system('cls' if os.name == 'nt' else 'clear')

import sys
import requests
import threading
import time
import pyperclip
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, 
                            QLabel, QVBoxLayout, QWidget, QHBoxLayout, QDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor
from tkinter import filedialog

class ImgurUploaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.history_window = None
        self.uploaded_window = None  
        self.history_entries = []
        self.uploaded_entries = []  
        self.current_color = None
        self.is_dark_theme = True  
        self.load_uploaded_entries()  
        self.change_background_color("#000000")  
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("ImGur")
        self.setFixedSize(300, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(5)

        self.upload_btn = QPushButton("Resim Yükle")
        self.upload_btn.clicked.connect(self.select_file)
        self.upload_btn.setFixedWidth(120)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: gray;
                padding: 8px;
                margin: 3px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #90EE90;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)

        # Color buttons ve tema düğmesi
        color_layout = QHBoxLayout()
        color_layout.setSpacing(10)
        
        self.orange_btn = QPushButton("Turuncu")
        self.orange_btn.clicked.connect(lambda: self.change_background_color("#FF6347"))
        self.orange_btn.setFixedWidth(80)
        self.orange_btn.setStyleSheet("""
            QPushButton {
                background-color: gray;
                padding: 8px;
                margin: 3px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FF6347;
                border-radius: 8px;
            }
        """)
        color_layout.addWidget(self.orange_btn)

        # Tema değiştirme düğmesi (Güneş/Ay)
        self.theme_btn = QPushButton("☀")  # Güneş simgesi (beyaz tema için)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setFixedWidth(40)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: gray;
                padding: 5px;
                margin: 3px;
                border-radius: 8px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #FFD700;  /* Sarı hover efekti */
                border-radius: 8px;
            }
        """)
        color_layout.addWidget(self.theme_btn)
        
        self.purple_btn = QPushButton("Mor")
        self.purple_btn.clicked.connect(lambda: self.change_background_color("#4B0082"))
        self.purple_btn.setFixedWidth(80)
        self.purple_btn.setStyleSheet("""
            QPushButton {
                background-color: gray;
                padding: 8px;
                margin: 3px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #4B0082;
                border-radius: 8px;
            }
        """)
        color_layout.addWidget(self.purple_btn)
        
        layout.addLayout(color_layout)

        self.history_btn = QPushButton("Geçmiş")
        self.history_btn.clicked.connect(self.toggle_history)
        self.history_btn.setFixedWidth(120)
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: gray;
                padding: 8px;
                margin: 3px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FFFF00;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.history_btn, alignment=Qt.AlignCenter)

        # Yüklenenler butonu
        self.uploaded_btn = QPushButton("Yüklenenler")
        self.uploaded_btn.clicked.connect(self.toggle_uploaded)
        self.uploaded_btn.setFixedWidth(120)
        self.uploaded_btn.setStyleSheet("""
            QPushButton {
                background-color: gray;
                padding: 8px;
                margin: 3px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #00CED1;  /* Turkuaz hover rengi */
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.uploaded_btn, alignment=Qt.AlignCenter)

        self.exit_btn = QPushButton("Çıkış")
        self.exit_btn.clicked.connect(self.close)
        self.exit_btn.setFixedWidth(120)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: gray;
                padding: 8px;
                margin: 3px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: red;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.exit_btn, alignment=Qt.AlignCenter)

        self.history_placeholder = QLabel("")
        self.history_placeholder.setFixedHeight(150)
        layout.addWidget(self.history_placeholder)

        self.url_label = QLabel("")
        self.url_label.setWordWrap(True)
        self.url_label.setAlignment(Qt.AlignCenter)
        self.url_label.mousePressEvent = self.copy_url
        layout.addWidget(self.url_label)

    def change_background_color(self, color):
        self.current_color = color
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)
        # Açık pencereler varsa onların da temasını güncelle
        if self.history_window and self.history_window.isVisible():
            self.history_window.setPalette(palette)
        if self.uploaded_window and self.uploaded_window.isVisible():
            self.uploaded_window.setPalette(palette)

    def toggle_theme(self):
        if self.is_dark_theme:
            self.change_background_color("#FFFFFF")  # Beyaz tema
            self.theme_btn.setText("☾")  # Ay simgesi
            self.is_dark_theme = False
        else:
            self.change_background_color("#000000")  # Siyah tema
            self.theme_btn.setText("☀")  # Güneş simgesi
            self.is_dark_theme = True

    def upload_image_to_imgur(self, image_path):
        try:
            url = "https://api.imgur.com/3/image"
            headers = {"Authorization": "Client-ID ecca3842e118f1f"}
            with open(image_path, 'rb') as img:
                files = {'image': img}
                response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response.json()['data']['link']
        except Exception as e:
            print(f"Error uploading {image_path}: {str(e)}")
            return None

    def select_file(self):
        file_paths = filedialog.askopenfilenames(
            title="Resim Dosyaları Seçin",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        if file_paths:
            threading.Thread(target=self.process_files, args=(file_paths,)).start()

    def process_files(self, file_paths):
        for file_path in file_paths:
            link = self.upload_image_to_imgur(file_path)
            if link:
                file_name = file_path.split("/")[-1]
                entry = f"{file_name} = {link}"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                uploaded_entry = {"file": file_name, "url": link, "timestamp": timestamp}
                self.update_history(entry)
                self.update_uploaded(uploaded_entry)
                self.show_url_for_30_seconds(link)
            else:
                self.update_history(f"{file_path.split('/')[-1]} yüklenemedi!")

    def update_history(self, text):
        self.history_entries.append(text)

    def update_uploaded(self, entry):
        self.uploaded_entries.append(entry)
        self.save_uploaded_entries()  # Her eklemede dosyaya kaydet

    def save_uploaded_entries(self):
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            with open(config_path, "w") as f:
                json.dump(self.uploaded_entries, f, indent=4)
        except PermissionError as e:
            QMessageBox.critical(self, "Hata", f"Dosya yazma izni yok: {e}\nLütfen dosya izinlerini kontrol edin veya Python'u yönetici olarak çalıştırın.")
            print(f"İzin hatası: {e}")
            raise
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya yazma hatası: {e}")
            print(f"Dosya yazma hatası: {e}")
            raise

    def load_uploaded_entries(self):
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    self.uploaded_entries = json.load(f)
            else:
                self.uploaded_entries = []
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Uyarı", f"config.json format hatası: {e}\nBoş liste ile başlatılıyor.")
            print(f"config.json format hatası: {e}")
            self.uploaded_entries = []
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya okuma hatası: {e}")
            print(f"Dosya okuma hatası: {e}")
            self.uploaded_entries = []

    def show_url_for_30_seconds(self, url):
        self.current_url = url
        self.url_label.setText(f"Foto: {url} (Tıklayın kopyalamak için)")
        self.url_label.setStyleSheet("color: #00FF00; font-size: 14px;")
        QTimer.singleShot(30000, self.hide_url)

    def hide_url(self):
        self.url_label.setText("")

    def copy_url(self, event):
        if hasattr(self, 'current_url'):
            pyperclip.copy(self.current_url)
            self.url_label.setText(f"Foto: {self.current_url} (Kopyalandı!)")
            self.url_label.setStyleSheet("color: #00FFFF; font-size: 14px;")

    def toggle_history(self):
        if not self.history_window or not self.history_window.isVisible():
            self.history_window = HistoryDialog(self.history_entries, self, self.current_color)
            self.history_window.show()
        else:
            self.history_window.close()

    def toggle_uploaded(self):
        if not self.uploaded_window or not self.uploaded_window.isVisible():
            self.uploaded_window = UploadedDialog(self.uploaded_entries, self, self.current_color)
            self.uploaded_window.show()
        else:
            self.uploaded_window.close()

class HistoryDialog(QDialog):
    def __init__(self, history_entries, parent=None, current_color=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Geçmiş")
        self.setFixedSize(300, 250)
        
        if current_color:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(current_color))
            self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        self.history_labels = []
        for entry in history_entries:
            label = QLabel(entry)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #1E90FF; font-size: 12px;")
            label.mousePressEvent = lambda event, e=entry: self.copy_history_entry(e)
            layout.addWidget(label)
            self.history_labels.append(label)
        
        self.clear_btn = QPushButton("Geçmişi Temizle")
        self.clear_btn.clicked.connect(self.clear_history)
        self.clear_btn.setFixedWidth(120)
        layout.addWidget(self.clear_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QPushButton {
                background-color: gray;
                padding: 8px;
                margin: 3px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #666666;
                border-radius: 8px;
            }
        """)

    def copy_history_entry(self, entry):
        try:
            url = entry.split(" = ")[1]
            pyperclip.copy(url)
            for label in self.history_labels:
                if label.text() == entry:
                    label.setText(f"{entry} (Kopyalandı!)")
                    label.setStyleSheet("color: #FFFF00; font-size: 14px;")
                    QTimer.singleShot(2000, lambda: self.reset_label(label, entry))
        except IndexError:
            print(f"Geçmiş girişi format hatası: {entry}")

    def reset_label(self, label, original_text):
        label.setText(original_text)
        label.setStyleSheet("color: #1E90FF; font-size: 12px;")

    def clear_history(self):
        self.parent.history_entries.clear()
        for label in self.history_labels:
            label.deleteLater()
        self.history_labels.clear()

class UploadedDialog(QDialog):
    def __init__(self, uploaded_entries, parent=None, current_color=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Yüklenenler")
        self.setFixedSize(300, 250)
        
        if current_color:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(current_color))
            self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        self.uploaded_labels = []
        for entry in uploaded_entries:
            text = f"{entry['file']} = {entry['url']} ({entry['timestamp']})"
            label = QLabel(text)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #1E90FF; font-size: 12px;")
            label.mousePressEvent = lambda event, e=entry['url']: self.copy_uploaded_entry(e)
            layout.addWidget(label)
            self.uploaded_labels.append(label)
        
        self.clear_btn = QPushButton("Yüklenenleri Temizle")
        self.clear_btn.clicked.connect(self.clear_uploaded)
        self.clear_btn.setFixedWidth(120)
        layout.addWidget(self.clear_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QPushButton {
                background-color: gray;
                padding: 8px;
                margin: 3px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #666666;
                border-radius: 8px;
            }
        """)

    def copy_uploaded_entry(self, url):
        pyperclip.copy(url)
        for label in self.uploaded_labels:
            if url in label.text():
                original_text = label.text()
                label.setText(f"{original_text} (Kopyalandı!)")
                label.setStyleSheet("color: #00FFFF; font-size: 12px;")
                QTimer.singleShot(2000, lambda: self.reset_label(label, original_text))

    def reset_label(self, label, original_text):
        label.setText(original_text)
        label.setStyleSheet("color: #1E90FF; font-size: 12px;")

    def clear_uploaded(self):
        self.parent.uploaded_entries.clear()
        self.parent.save_uploaded_entries()
        for label in self.uploaded_labels:
            label.deleteLater()
        self.uploaded_labels.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImgurUploaderApp()
    window.show()
    sys.exit(app.exec_())