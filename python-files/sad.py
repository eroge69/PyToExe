import os
import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QPushButton, QLineEdit, QTextEdit, 
                            QFrame, QHBoxLayout)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

class OSINTPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSINT Pro")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 16px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit, QTextEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QFrame {
                background-color: #34495e;
                border-radius: 10px;
                border: 1px solid #7f8c8d;
            }
        """)
        
        self.initUI()
        self.apply_shadows()
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header = QLabel("OSINT Pro")
        header.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(24)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: #3498db;")
        main_layout.addWidget(header)
        
        # Main content frame
        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.StyledPanel)
        content_layout = QVBoxLayout()
        content_frame.setLayout(content_layout)
        
        # Phone number input
        phone_layout = QHBoxLayout()
        phone_label = QLabel("Номер телефона:")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Введите номер телефона (например: 79991234567)")
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        content_layout.addLayout(phone_layout)
        
        # Search button
        search_btn = QPushButton("Найти информацию")
        search_btn.clicked.connect(self.search_phone_info)
        content_layout.addWidget(search_btn, alignment=Qt.AlignCenter)
        
        # Results
        results_label = QLabel("Результаты поиска:")
        content_layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        content_layout.addWidget(self.results_text)
        
        main_layout.addWidget(content_frame)
        
        # Footer
        footer = QLabel("© 2023 OSINT Pro | Все права защищены")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        main_layout.addWidget(footer)
        
        # Add some spacing
        main_layout.setSpacing(20)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
    def apply_shadows(self):
        # Apply shadow effects to widgets
        for widget in self.findChildren(QFrame):
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setXOffset(5)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0, 0, 0, 150))
            widget.setGraphicsEffect(shadow)
            
        for widget in self.findChildren(QPushButton):
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setXOffset(3)
            shadow.setYOffset(3)
            shadow.setColor(QColor(0, 0, 0, 100))
            widget.setGraphicsEffect(shadow)
            
            # Add animation on hover
            widget.enterEvent = lambda event, w=widget: self.animate_button(w, 1.05)
            widget.leaveEvent = lambda event, w=widget: self.animate_button(w, 1.0)
    
    def animate_button(self, widget, scale):
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.OutBack)
        
        current_geom = widget.geometry()
        center = current_geom.center()
        
        new_width = int(current_geom.width() * scale)
        new_height = int(current_geom.height() * scale)
        
        new_geom = QRect(
            center.x() - new_width // 2,
            center.y() - new_height // 2,
            new_width,
            new_height
        )
        
        animation.setStartValue(current_geom)
        animation.setEndValue(new_geom)
        animation.start()
    
    def search_phone_info(self):
        phone_number = self.phone_input.text().strip()
        if not phone_number:
            self.results_text.setPlainText("Пожалуйста, введите номер телефона")
            return
            
        self.results_text.setPlainText("Идет поиск информации...")
        
        try:
            # Здесь можно добавить реальные API для поиска информации
            # Это пример с использованием публичных сервисов
            
            info = f"Информация по номеру: {phone_number}\n\n"
            
            # Проверка номера через NumVerify (пример)
            info += self.check_numverify(phone_number)
            
            # Проверка через Google поиск
            info += self.check_google(phone_number)
            
            # Проверка через социальные сети (пример)
            info += self.check_social_networks(phone_number)
            
            self.results_text.setPlainText(info)
            
        except Exception as e:
            self.results_text.setPlainText(f"Ошибка при поиске информации: {str(e)}")
    
    def check_numverify(self, phone):
        # Это пример, для реального использования нужно получить API ключ на numverify.com
        return "[NumVerify] Сервис проверки номера (требуется API ключ)\n\n"
    
    def check_google(self, phone):
        try:
            url = f"https://www.google.com/search?q={phone}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = soup.find_all('div', class_='tF2Cxc')
            info = "[Google Search] Возможные упоминания:\n"
            
            for i, result in enumerate(results[:5], 1):
                title = result.find('h3').text if result.find('h3') else "Без названия"
                link = result.find('a')['href'] if result.find('a') else "Нет ссылки"
                info += f"{i}. {title}\n   {link}\n"
            
            return info + "\n"
        except Exception as e:
            return f"[Google Search] Ошибка при поиске: {str(e)}\n\n"
    
    def check_social_networks(self, phone):
        info = "[Социальные сети] Проверка:\n"
        
        # Пример проверки через ВКонтакте (нужна авторизация для реального использования)
        vk_url = f"https://vk.com/phone/{phone}"
        info += f"- ВКонтакте: {vk_url}\n"
        
        # Пример проверки через Telegram
        tg_url = f"https://t.me/{phone}"
        info += f"- Telegram: {tg_url}\n"
        
        # Пример проверки через WhatsApp
        wa_url = f"https://wa.me/{phone}"
        info += f"- WhatsApp: {wa_url}\n\n"
        
        return info

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Установка стиля для красивого интерфейса
    app.setStyle("Fusion")
    
    # Настройка палитры для темной темы
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(44, 62, 80))
    palette.setColor(QPalette.WindowText, QColor(236, 240, 241))
    palette.setColor(QPalette.Base, QColor(52, 73, 94))
    palette.setColor(QPalette.AlternateBase, QColor(44, 62, 80))
    palette.setColor(QPalette.ToolTipBase, QColor(236, 240, 241))
    palette.setColor(QPalette.ToolTipText, QColor(236, 240, 241))
    palette.setColor(QPalette.Text, QColor(236, 240, 241))
    palette.setColor(QPalette.Button, QColor(52, 152, 219))
    palette.setColor(QPalette.ButtonText, QColor(236, 240, 241))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(41, 128, 185))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = OSINTPro()
    window.show()
    sys.exit(app.exec_())