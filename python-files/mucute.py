import os
import pygame
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QSlider, QPushButton, QLabel, QFileDialog, 
                             QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5 import QtGui

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # تنظیمات اولیه پنجره
        self.setWindowTitle("پخش کننده موسیقی کیوت ♪")
        self.setGeometry(100, 100, 500, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffebee;
            }
            QListWidget {
                background-color: #fce4ec;
                border: 2px solid #f8bbd0;
                border-radius: 10px;
                font-family: 'Arial Rounded MT Bold';
                font-size: 14px;
                color: #880e4f;
            }
            QPushButton {
                background-color: #f8bbd0;
                border: 2px solid #f48fb1;
                border-radius: 15px;
                padding: 8px;
                font-family: 'Comic Sans MS';
                font-size: 14px;
                color: #ad1457;
            }
            QPushButton:hover {
                background-color: #f48fb1;
            }
            QSlider::groove:horizontal {
                height: 10px;
                background: #f8bbd0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                width: 20px;
                height: 20px;
                background: #ec407a;
                border-radius: 10px;
            }
            QLabel {
                font-family: 'Comic Sans MS';
                color: #c2185b;
                font-size: 16px;
            }
            QTextEdit {
                background-color: #fce4ec;
                border: 2px solid #f8bbd0;
                border-radius: 10px;
                font-family: 'Comic Sans MS';
                font-size: 14px;
                color: #880e4f;
            }
        """)
        
        # آیکون برنامه
        self.setWindowIcon(QIcon('icon.png'))  # می‌توانید یک آیکون مناسب اضافه کنید
        
        # تنظیمات پخش موسیقی
        pygame.mixer.init()
        self.current_song = ""
        self.paused = False
        self.lyrics = {}
        
        # ایجاد ویجت‌ها
        self.init_ui()
        
    def init_ui(self):
        # ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # تصویر آلبوم
        self.album_art = QLabel()
        self.album_art.setAlignment(Qt.AlignCenter)
        self.album_art.setPixmap(QPixmap("default_cover.png").scaled(300, 300, Qt.KeepAspectRatio))
        layout.addWidget(self.album_art)
        
        # نمایش نام آهنگ
        self.song_label = QLabel("هیچ آهنگی انتخاب نشده")
        self.song_label.setAlignment(Qt.AlignCenter)
        self.song_label.setFont(QFont('Comic Sans MS', 16))
        layout.addWidget(self.song_label)
        
        # نوار پیشرفت
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.progress_slider)
        
        # تایمر برای آپدیت نوار پیشرفت
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_slider)
        self.timer.start(1000)
        
        # کنترل‌های پخش
        controls_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("⏮ قبلی")
        self.prev_btn.clicked.connect(self.prev_song)
        controls_layout.addWidget(self.prev_btn)
        
        self.play_btn = QPushButton("▶ پخش")
        self.play_btn.clicked.connect(self.play_music)
        controls_layout.addWidget(self.play_btn)
        
        self.pause_btn = QPushButton("⏸ توقف")
        self.pause_btn.clicked.connect(self.pause_music)
        controls_layout.addWidget(self.pause_btn)
        
        self.next_btn = QPushButton("⏭ بعدی")
        self.next_btn.clicked.connect(self.next_song)
        controls_layout.addWidget(self.next_btn)
        
        layout.addLayout(controls_layout)
        
        # کنترل ولوم
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("صدا:"))
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        
        layout.addLayout(volume_layout)
        
        # لیست پخش
        self.playlist = QListWidget()
        self.playlist.itemDoubleClicked.connect(self.play_selected_song)
        layout.addWidget(self.playlist)
        
        # دکمه‌های مدیریت لیست پخش
        playlist_btns_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ اضافه کردن آهنگ")
        self.add_btn.clicked.connect(self.add_songs)
        playlist_btns_layout.addWidget(self.add_btn)
        
        self.remove_btn = QPushButton("❌ حذف آهنگ")
        self.remove_btn.clicked.connect(self.remove_song)
        playlist_btns_layout.addWidget(self.remove_btn)
        
        layout.addLayout(playlist_btns_layout)
        
        # دکمه‌های متن آهنگ
        lyrics_btns_layout = QHBoxLayout()
        
        self.add_lyrics_btn = QPushButton("✍️ افزودن متن آهنگ")
        self.add_lyrics_btn.clicked.connect(self.show_add_lyrics_dialog)
        lyrics_btns_layout.addWidget(self.add_lyrics_btn)
        
        self.view_lyrics_btn = QPushButton("📖 مشاهده متن آهنگ")
        self.view_lyrics_btn.clicked.connect(self.show_lyrics)
        lyrics_btns_layout.addWidget(self.view_lyrics_btn)
        
        layout.addLayout(lyrics_btns_layout)
        
    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "آهنگ‌ها را انتخاب کنید", "", "فایل‌های صوتی (*.mp3 *.wav *.ogg)")
        if files:
            for file in files:
                self.playlist.addItem(file)
    
    def remove_song(self):
        current_row = self.playlist.currentRow()
        if current_row >= 0:
            self.playlist.takeItem(current_row)
    
    def play_music(self):
        if self.playlist.count() == 0:
            return
            
        if not self.current_song:
            self.current_song = self.playlist.item(0).text()
            self.playlist.setCurrentRow(0)
        
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.play_btn.setText("▶ پخش")
        else:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play()
            self.update_song_info()
    
    def pause_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True
            self.play_btn.setText("▶ ادامه")
    
    def play_selected_song(self, item):
        self.current_song = item.text()
        self.play_music()
    
    def prev_song(self):
        current_row = self.playlist.currentRow()
        if current_row > 0:
            self.playlist.setCurrentRow(current_row - 1)
            self.current_song = self.playlist.currentItem().text()
            self.play_music()
    
    def next_song(self):
        current_row = self.playlist.currentRow()
        if current_row < self.playlist.count() - 1:
            self.playlist.setCurrentRow(current_row + 1)
            self.current_song = self.playlist.currentItem().text()
            self.play_music()
    
    def set_volume(self, value):
        pygame.mixer.music.set_volume(value / 100)
    
    def set_position(self, position):
        if pygame.mixer.music.get_busy():
            song_length = pygame.mixer.Sound(self.current_song).get_length()
            pygame.mixer.music.set_pos(song_length * position / 100)
    
    def update_slider(self):
        if pygame.mixer.music.get_busy():
            current_pos = pygame.mixer.music.get_pos() / 1000  # به ثانیه
            song_length = pygame.mixer.Sound(self.current_song).get_length()
            self.progress_slider.setValue(int((current_pos / song_length) * 100))
    
    def update_song_info(self):
        if self.current_song:
            song_name = os.path.basename(self.current_song)
            self.song_label.setText(song_name)
            
            # در یک برنامه واقعی می‌توانید متادیتاهای آهنگ را خوانده و تصویر آلبوم را نمایش دهید
            # اینجا فقط یک تصویر پیش‌فرض نمایش می‌دهیم
            self.album_art.setPixmap(QPixmap("default_cover.png").scaled(300, 300, Qt.KeepAspectRatio))
    
    def show_add_lyrics_dialog(self):
        if not self.current_song:
            QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک آهنگ انتخاب کنید")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("متن آهنگ را اضافه کنید")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #fce4ec;
            }
            QTextEdit {
                background-color: #fff;
                border: 1px solid #f8bbd0;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        lyrics_edit = QTextEdit()
        if self.current_song in self.lyrics:
            lyrics_edit.setText(self.lyrics[self.current_song])
        layout.addWidget(lyrics_edit)
        
        btn_box = QHBoxLayout()
        save_btn = QPushButton("ذخیره")
        save_btn.clicked.connect(lambda: self.save_lyrics(lyrics_edit.toPlainText(), dialog))
        btn_box.addWidget(save_btn)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(dialog.reject)
        btn_box.addWidget(cancel_btn)
        
        layout.addLayout(btn_box)
        dialog.exec_()
    
    def save_lyrics(self, text, dialog):
        self.lyrics[self.current_song] = text
        dialog.accept()
        QMessageBox.information(self, "موفق", "متن آهنگ با موفقیت ذخیره شد")
    
    def show_lyrics(self):
        if not self.current_song:
            QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک آهنگ انتخاب کنید")
            return
            
        if self.current_song not in self.lyrics or not self.lyrics[self.current_song]:
            QMessageBox.information(self, "متن آهنگ", "متن آهنگ برای این آهنگ ذخیره نشده است")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle(f"متن آهنگ: {os.path.basename(self.current_song)}")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #fce4ec;
            }
            QTextEdit {
                background-color: #fff;
                border: none;
                font-family: 'Comic Sans MS';
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        lyrics_view = QTextEdit()
        lyrics_view.setText(self.lyrics[self.current_song])
        lyrics_view.setReadOnly(True)
        layout.addWidget(lyrics_view)
        
        close_btn = QPushButton("بستن")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication([])
    
    # تنظیم فونت برای نمایش صحیح متن فارسی
    font = QtGui.QFont()
    font.setFamily("Arial")
    font.setPointSize(10)
    app.setFont(font)
    
    player = MusicPlayer()
    player.show()
    app.exec_()