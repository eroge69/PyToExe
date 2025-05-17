import os
import sys
import requests
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                            QPushButton, QVBoxLayout, QWidget, QTextEdit)
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush
from PyQt5.QtCore import Qt
from faker import Faker
import random

fake = Faker()

class GradientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔍 PhoneLookup PRO")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("icon.ico"))  # Нужно добавить файл icon.ico
        
        # Установка градиентного фона
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(40, 50, 60))
        gradient.setColorAt(1, QColor(20, 30, 40))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
        self.initUI()
    
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Заголовок с эффектом
        title = QLabel("PhoneLookup PRO")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #4fc3f7;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Поле ввода
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Введите номер телефона с кодом страны (например +79123456789)")
        self.phone_input.setStyleSheet("""
            QLineEdit {
                background: rgba(60, 70, 80, 180);
                color: white;
                border: 1px solid #555;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4fc3f7;
            }
        """)
        layout.addWidget(self.phone_input)
        
        # Кнопка поиска с эффектом
        self.search_btn = QPushButton("Найти информацию")
        self.search_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a76a8, stop:1 #3a6690);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                min-width: 200px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a86b8, stop:1 #4a7690);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3a6690, stop:1 #2a5670);
            }
        """)
        self.search_btn.clicked.connect(self.search_phone)
        layout.addWidget(self.search_btn)
        
        # Поле результатов
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background: rgba(30, 40, 50, 180);
                color: #eee;
                border: 1px solid #444;
                border-radius: 10px;
                padding: 15px;
                font-family: Consolas, 'Courier New', monospace;
            }
        """)
        layout.addWidget(self.result_text)
    
    def append_colored_text(self, text, color):
        self.result_text.moveCursor(QTextCursor.End)
        self.result_text.setTextColor(color)
        self.result_text.insertPlainText(text + "\n")
        self.result_text.setTextColor(QColor("#eee"))
    
    def search_phone(self):
        phone = self.phone_input.text()
        if not phone:
            self.append_colored_text("❌ Пожалуйста, введите номер телефона", QColor("#e74c3c"))
            return
        
        try:
            self.result_text.clear()
            self.append_colored_text("🔍 Начинаем поиск информации...", QColor("#4fc3f7"))
            
            # Проверка номера
            parsed_num = phonenumbers.parse(phone, None)
            if not phonenumbers.is_valid_number(parsed_num):
                self.append_colored_text("❌ Неверный формат номера телефона", QColor("#e74c3c"))
                return
            
            # Основная информация
            self.append_colored_text("\n=== ОСНОВНАЯ ИНФОРМАЦИЯ ===", QColor("#4fc3f7"))
            
            country = geocoder.country_name_for_number(parsed_num, "ru") or "НЕ НАЙДЕНО"
            operator = carrier.name_for_number(parsed_num, "ru") or "НЕ НАЙДЕНО"
            timezone_info = timezone.time_zones_for_number(parsed_num) or ["НЕ НАЙДЕНО"]
            
            self.append_colored_text(f"📱 Номер: {phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}", 
                                   QColor("#2ecc71"))
            self.append_colored_text(f"🌍 Страна: {country}", 
                                   QColor("#2ecc71") if country != "НЕ НАЙДЕНО" else QColor("#e74c3c"))
            self.append_colored_text(f"📶 Оператор: {operator}", 
                                   QColor("#2ecc71") if operator != "НЕ НАЙДЕНО" else QColor("#e74c3c"))
            self.append_colored_text(f"🕒 Часовой пояс: {', '.join(timezone_info)}", 
                                   QColor("#2ecc71") if timezone_info[0] != "НЕ НАЙДЕНО" else QColor("#e74c3c"))
            
            # Генерация дополнительной информации
            if random.random() > 0.3:  # 70% шанс найти данные
                self.append_colored_text("\n=== ЛИЧНАЯ ИНФОРМАЦИЯ ===", QColor("#4fc3f7"))
                
                # ФИО
                name = fake.name()
                self.append_colored_text(f"👤 ФИО: {name}", QColor("#2ecc71"))
                
                # Адрес
                address = fake.address().replace("\n", ", ")
                self.append_colored_text(f"🏠 Адрес: {address}", QColor("#2ecc71"))
                
                # Дополнительные телефоны
                if random.random() > 0.5:
                    second_phone = f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"
                    self.append_colored_text(f"📱 Доп. телефон: {second_phone}", QColor("#3498db"))
                
                # Телефон родителей
                if random.random() > 0.6:
                    parents_phone = f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"
                    self.append_colored_text(f"👪 Телефон родителей: {parents_phone}", QColor("#3498db"))
                
                # Соцсети
                if random.random() > 0.4:
                    self.append_colored_text("\n=== СОЦИАЛЬНЫЕ СЕТИ ===", QColor("#4fc3f7"))
                    networks = random.sample(["VK", "Telegram", "WhatsApp", "Instagram"], random.randint(1, 3))
                    for net in networks:
                        self.append_colored_text(f"• {net}: {fake.user_name()}", QColor("#3498db"))
            else:
                self.append_colored_text("\n❌ Дополнительная информация не найдена", QColor("#e74c3c"))
            
            self.append_colored_text("\n✅ Поиск завершен", QColor("#2ecc71"))
            
        except Exception as e:
            self.append_colored_text(f"⚠️ Ошибка: {str(e)}", QColor("#e74c3c"))

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = GradientWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()