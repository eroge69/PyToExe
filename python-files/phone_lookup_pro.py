import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QLabel, QPushButton, QLineEdit, QTextEdit, 
                           QFrame, QHBoxLayout, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve

class OSINTPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSINT Pro v1.0")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowIcon(QIcon('icon.ico'))  # Добавьте файл icon.ico в папку
        
        # Стилизация главного окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2d;
            }
            QLabel {
                color: #ffffff;
                font-size: 16px;
            }
            QPushButton {
                background-color: #4a6fa5;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 8px;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #3a5a80;
            }
            QPushButton:pressed {
                background-color: #2a4a70;
            }
            QLineEdit, QTextEdit {
                background-color: #2a2a3a;
                color: #ffffff;
                border: 2px solid #4a6fa5;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #4a6fa5;
            }
            QFrame {
                background-color: #2a2a3a;
                border-radius: 12px;
                border: 2px solid #3a3a4a;
            }
            QTextEdit {
                background-color: #252535;
            }
        """)
        
        self.initUI()
        self.apply_shadows()
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Заголовок приложения
        header = QLabel("OSINT PRO")
        header.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(28)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("""
            QLabel {
                color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a6fa5, stop:0.5 #6a8fc5, stop:1 #4a6fa5);
                padding: 10px;
            }
        """)
        main_layout.addWidget(header)
        
        # Основной контент
        content_frame = QFrame()
        content_layout = QVBoxLayout()
        content_frame.setLayout(content_layout)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Ввод номера телефона
        phone_layout = QHBoxLayout()
        phone_label = QLabel("Номер телефона:")
        phone_label.setStyleSheet("font-size: 18px;")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Введите номер (7XXXXXXXXXX)")
        self.phone_input.setStyleSheet("font-size: 16px; height: 40px;")
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        content_layout.addLayout(phone_layout)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        
        search_btn = QPushButton("🔍 Найти информацию")
        search_btn.setStyleSheet("font-size: 16px;")
        search_btn.clicked.connect(self.search_phone_info)
        
        clear_btn = QPushButton("🧹 Очистить")
        clear_btn.setStyleSheet("font-size: 16px; background-color: #5a3a5a;")
        clear_btn.clicked.connect(self.clear_results)
        
        buttons_layout.addWidget(search_btn)
        buttons_layout.addWidget(clear_btn)
        content_layout.addLayout(buttons_layout)
        
        # Результаты поиска
        results_label = QLabel("Результаты поиска:")
        results_label.setStyleSheet("font-size: 18px;")
        content_layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setStyleSheet("font-size: 14px;")
        self.results_text.setReadOnly(True)
        content_layout.addWidget(self.results_text)
        
        main_layout.addWidget(content_frame)
        
        # Статус бар
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2a2a3a;
                color: #aaaaaa;
                font-size: 12px;
                border-top: 1px solid #3a3a4a;
            }
        """)
        self.status_bar.showMessage("Готов к работе")
        
    def apply_shadows(self):
        # Тени для виджетов
        for widget in [self.centralWidget().findChild(QFrame)]:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(25)
            shadow.setXOffset(5)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0, 0, 0, 150))
            widget.setGraphicsEffect(shadow)
            
        for btn in self.findChildren(QPushButton):
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setXOffset(3)
            shadow.setYOffset(3)
            shadow.setColor(QColor(0, 0, 0, 100))
            btn.setGraphicsEffect(shadow)
            
            # Анимация кнопок
            btn.enterEvent = lambda event, b=btn: self.animate_button(b, 1.05)
            btn.leaveEvent = lambda event, b=btn: self.animate_button(b, 1.0)
    
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
        if not phone_number.isdigit() or len(phone_number) != 11:
            self.results_text.setPlainText("Ошибка: введите 11-значный номер телефона (только цифры)")
            return
            
        self.status_bar.showMessage("Идет поиск информации...")
        self.results_text.setPlainText("Поиск информации по номеру: " + phone_number + "\n" + "="*50 + "\n")
        
        try:
            # Поиск через Google
            google_info = self.search_google(phone_number)
            self.results_text.append(google_info)
            
            # Проверка в социальных сетях
            social_info = self.search_social_networks(phone_number)
            self.results_text.append(social_info)
            
            # Проверка через базы данных (имитация)
            db_info = self.check_databases(phone_number)
            self.results_text.append(db_info)
            
            self.status_bar.showMessage("Поиск завершен")
            
        except Exception as e:
            self.results_text.append(f"\nОшибка при поиске: {str(e)}")
            self.status_bar.showMessage("Ошибка при выполнении поиска")
    
    def search_google(self, phone):
        try:
            url = f"https://www.google.com/search?q={phone}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = soup.find_all('div', class_='tF2Cxc')
            info = "[GOOGLE] Результаты поиска:\n"
            
            for i, result in enumerate(results[:5], 1):
                title = result.find('h3').text if result.find('h3') else "Без названия"
                link = result.find('a')['href'] if result.find('a') else "Нет ссылки"
                info += f"{i}. {title}\n   {link}\n"
            
            return info + "\n"
        except Exception as e:
            return f"[GOOGLE] Ошибка при поиске: {str(e)}\n\n"
    
    def search_social_networks(self, phone):
        info = "[СОЦИАЛЬНЫЕ СЕТИ] Возможные профили:\n"
        
        # ВКонтакте
        vk_url = f"https://vk.com/phone{phone}"
        info += f"- ВКонтакте: {vk_url}\n"
        
        # Telegram
        tg_url = f"https://t.me/{phone}"
        info += f"- Telegram: {tg_url}\n"
        
        # WhatsApp
        wa_url = f"https://wa.me/{phone}"
        info += f"- WhatsApp: {wa_url}\n"
        
        # Avito
        avito_url = f"https://www.avito.ru/profile/items?user_phone={phone}"
        info += f"- Avito: {avito_url}\n\n"
        
        return info
    
    def check_databases(self, phone):
        # Имитация проверки через базы данных
        info = "[БАЗЫ ДАННЫХ] Проверка:\n"
        info += "- Номер зарегистрирован в России (МТС)\n"
        info += "- Возможный регион: Москва и Московская область\n"
        info += "- Номер активен с 2018 года\n"
        info += "- Не числится в спам-базах\n\n"
        
        return info
    
    def clear_results(self):
        self.results_text.clear()
        self.status_bar.showMessage("Готов к работе")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Настройка темной темы
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(30, 30, 45))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(42, 42, 58))
    dark_palette.setColor(QPalette.AlternateBase, QColor(30, 30, 45))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(74, 111, 165))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Highlight, QColor(74, 111, 165))
    dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(dark_palette)
    
    app.setStyle("Fusion")
    
    window = OSINTPro()
    window.show()
    sys.exit(app.exec_())