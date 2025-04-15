import sys
import platform
import subprocess
import traceback
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QTextEdit, QScrollArea, QMessageBox, QComboBox,
    QHBoxLayout, QSizePolicy, QFrame, QProgressBar, QFileDialog
)


class ErrorReportWindow(QMainWindow):
    """Окно для отображения подробного отчета об ошибке."""
    
    def __init__(self, error_details: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Отчет об ошибке")
        self.setMinimumSize(QSize(800, 600))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title_label = QLabel("Произошла ошибка")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #e74c3c;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Основная информация об ошибке
        error_info = QTextEdit()
        error_info.setReadOnly(True)
        error_info.setFont(QFont("Consolas", 10))
        error_info.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        error_text = f"""
        <div style="font-family: Arial; font-size: 12px; line-height: 1.6;">
            <h2 style="color: #e74c3c;">{error_details.get('title', 'Неизвестная ошибка')}</h2>
            <p><b>Время:</b> {error_details.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
            <p><b>Тип ошибки:</b> {error_details.get('type', 'Неизвестно')}</p>
            <p><b>Описание:</b> {error_details.get('message', 'Нет описания')}</p>
            
            <h3 style="color: #f39c12;">Детали:</h3>
            <pre>{error_details.get('details', 'Нет дополнительных деталей')}</pre>
            
            <h3 style="color: #3498db;">Контекст:</h3>
            <pre>{error_details.get('context', 'Нет информации о контексте')}</pre>
        </div>
        """
        
        error_info.setHtml(error_text)
        
        scroll = QScrollArea()
        scroll.setWidget(error_info)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)


class DriveAnalyzerApp(QMainWindow):
    """Главное окно приложения для анализа дисков."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Диагностика дисков v1.0")
        self.setMinimumSize(QSize(1150, 540))
        self.setWindowIcon(QIcon("disk_icon.png"))  # Добавьте иконку в папку с программой
        
        # Настройка цветовой палитры
        self.setup_palette()
        
        self._init_ui()
        self._setup_ui()
        
    def setup_palette(self) -> None:
        """Настраивает цветовую палитру приложения."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.setPalette(palette)
        
    def show_error_report(self, error: Exception, context: str = "") -> None:
        """Показывает подробный отчет об ошибке."""
        error_details = {
            "title": "Ошибка при выполнении операции",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": error.__class__.__name__,
            "message": str(error),
            "details": traceback.format_exc(),
            "context": context
        }
        
        # Показываем окно с отчетом
        error_window = ErrorReportWindow(error_details, self)
        error_window.show()
        
    def _init_ui(self) -> None:
        """Инициализация основного интерфейса."""
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        
    def _setup_ui(self) -> None:
        """Настройка элементов интерфейса."""
        self._add_header()
        self._add_action_buttons()
        self._add_status_bar()
        
    def _add_header(self) -> None:
        """Добавляет заголовок приложения."""
        header = QFrame()
        header.setStyleSheet("background-color: #2a2a2a; border-radius: 8px;")
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)
        
        title = QLabel("Диагностика и анализ дисков")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #ffffff; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Мониторинг и обслуживание накопителей")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setStyleSheet("color: #aaaaaa; padding-bottom: 10px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        self.layout.addWidget(header)
        
    def _add_action_buttons(self) -> None:
        """Добавляет кнопки действий."""
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("background-color: #353535; border-radius: 8px; padding: 15px;")
        buttons_layout = QVBoxLayout()
        buttons_frame.setLayout(buttons_layout)
        
        buttons = [
            ("Анализ накопителей", self.analyze_drives, "#6a3093"),
            ("График использования", self.show_disk_usage_graph, "#3498db"),
            ("Советы по обслуживанию", self.show_maintenance_tips, "#f39c12"),
            ("Информация о системе", self.show_system_info, "#2ecc71")
        ]
        
        for text, handler, color in buttons:
            btn = self._create_button(text, color)
            btn.clicked.connect(handler)
            buttons_layout.addWidget(btn)
            
        buttons_layout.addStretch()
        self.layout.addWidget(buttons_frame, stretch=1)
    
    def _add_status_bar(self) -> None:
        """Добавляет улучшенный статус бар с дополнительной информацией."""
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #2a2a2a;
                color: white;
                border-top: 1px solid #444;
                padding: 5px;
            }
        """)
        
        # Виджет для отображения статуса дисков
        self.disk_status_widget = QFrame()
        self.disk_status_widget.setStyleSheet("background-color: transparent;")
        status_layout = QHBoxLayout()
        self.disk_status_widget.setLayout(status_layout)
        
        # Иконка статуса
        self.status_icon = QLabel()
        self.status_icon.setPixmap(QIcon.fromTheme("drive-harddisk").pixmap(24, 24))
        self.status_icon.setStyleSheet("margin-left: 5px;")
        status_layout.addWidget(self.status_icon)
        
        # Метка статуса
        self.status_label = QLabel("Статус:")
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                min-width: 50px;
            }
        """)
        status_layout.addWidget(self.status_label)
        
        # Прогресс-бар с текстом
        self.disk_space_bar = QProgressBar()
        self.disk_space_bar.setRange(0, 100)
        self.disk_space_bar.setFormat("Общее заполнение: %v%")
        self.disk_space_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
                color: white;
                background: #353535;
                height: 22px;
                min-width: 200px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:0.5 #f39c12, stop:1 #2ecc71);
                border-radius: 2px;
            }
        """)
        status_layout.addWidget(self.disk_space_bar, stretch=1)
        
        # Индикатор количества дисков
        self.disk_count_label = QLabel()
        self.disk_count_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                min-width: 120px;
                padding: 0 10px;
            }
        """)
        status_layout.addWidget(self.disk_count_label)
        
        # Индикатор последнего обновления
        self.last_update_label = QLabel()
        self.last_update_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 11px;
                min-width: 150px;
            }
        """)
        status_layout.addWidget(self.last_update_label)
        
        # Добавляем виджет в статус бар
        self.statusBar().addPermanentWidget(self.disk_status_widget)
        
        # Обновление статус бара каждые 5 секунд
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_bar)
        self.status_timer.start(5000)
        self.update_status_bar()
    
    def update_status_bar(self) -> None:
        """Обновляет информацию в статус баре."""
        try:
            total_usage = 0
            total_partitions = 0
            partitions = psutil.disk_partitions(all=False)
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_usage += usage.percent
                    total_partitions += 1
                except Exception as e:
                    self.show_error_report(e, "Обновление статус бара: анализ раздела")
                    continue
            
            # Обновляем информацию о количестве дисков
            self.disk_count_label.setText(f"Дисков: {len(partitions)} | Разделов: {total_partitions}")
            
            # Обновляем время последнего обновления
            now = datetime.now().strftime("%H:%M:%S")
            self.last_update_label.setText(f"Обновлено: {now}")
            
            if total_partitions > 0:
                avg_usage = total_usage / total_partitions
                self.disk_space_bar.setValue(int(avg_usage))
                
                # Устанавливаем иконку в зависимости от состояния
                if avg_usage > 90:
                    self.status_icon.setPixmap(QIcon.fromTheme("dialog-error").pixmap(24, 24))
                    self.status_label.setText("<span style='color:#e74c3c;'>Критическое заполнение!</span>")
                    self.disk_space_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #444;
                            background: #353535;
                        }
                        QProgressBar::chunk { background: #e74c3c; }
                    """)
                elif avg_usage > 70:
                    self.status_icon.setPixmap(QIcon.fromTheme("dialog-warning").pixmap(24, 24))
                    self.status_label.setText("<span style='color:#f39c12;'>Высокое заполнение</span>")
                    self.disk_space_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #444;
                            background: #353535;
                        }
                        QProgressBar::chunk { background: #f39c12; }
                    """)
                else:
                    self.status_icon.setPixmap(QIcon.fromTheme("drive-harddisk").pixmap(24, 24))
                    self.status_label.setText("<span style='color:#2ecc71;'>Норма</span>")
                    self.disk_space_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #444;
                            background: #353535;
                        }
                        QProgressBar::chunk { background: #2ecc71; }
                    """)
        except Exception as e:
            self.show_error_report(e, "Обновление статус бара")
            self.status_label.setText("<span style='color:#e74c3c;'>Ошибка обновления</span>")
            self.status_icon.setPixmap(QIcon.fromTheme("dialog-error").pixmap(24, 24))
    
    def _create_button(self, text: str, color: str) -> QPushButton:
        """Создает стилизованную кнопку."""
        btn = QPushButton(text)
        btn.setFont(QFont("Arial", 12))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
                min-width: 250px;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color)};
                padding-top: 16px;
                padding-bottom: 14px;
            }}
        """)
        btn.setCursor(Qt.PointingHandCursor)
        return btn
    
    def _lighten_color(self, hex_color: str, amount=30) -> str:
        """Осветляет цвет."""
        color = QColor(hex_color)
        return color.lighter(100 + amount).name()
    
    def _darken_color(self, hex_color: str, amount=20) -> str:
        """Затемняет цвет."""
        color = QColor(hex_color)
        return color.darker(100 + amount).name()
    
    def _get_drive_info(self, partition: psutil._common.sdiskpart) -> Dict[str, Any]:
        """Собирает информацию о дисковом разделе."""
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            return {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "type": self._get_drive_type(partition),
                "fstype": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            }
        except Exception as e:
            return {"error": f"Ошибка анализа диска {partition.device}: {str(e)}"}
    
    def _get_drive_type(self, partition: psutil._common.sdiskpart) -> str:
        """Определяет тип накопителя в зависимости от ОС."""
        system = platform.system()
        try:
            if system == "Windows":
                return self._get_windows_drive_type(partition.device)
            elif system == "Linux":
                return self._get_linux_drive_type(partition.device)
            return "Неизвестная ОС"
        except Exception:
            return "Ошибка определения"
    
    def _get_windows_drive_type(self, device: str) -> str:
        """Определяет тип накопителя для Windows."""
        try:
            drive_letter = device.replace("\\", "").replace(":", "")
            command = f"wmic diskdrive where DeviceID='{drive_letter}' get MediaType"
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                shell=True,
                check=True
            )
            output = result.stdout.strip().splitlines()
            return output[1].strip() if len(output) > 1 else "Неизвестный тип"
        except subprocess.SubprocessError:
            return "Неизвестный тип"
    
    def _get_linux_drive_type(self, device: str) -> str:
        """Определяет тип накопителя для Linux."""
        try:
            drive_name = device.split('/')[-1]
            command = f"lsblk -o NAME,ROTA | grep {drive_name}"
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                shell=True,
                check=True
            )
            output = result.stdout.strip().splitlines()
            if output:
                return "SSD" if output[0].split()[-1] == "0" else "HDD"
            return "Неизвестный тип"
        except subprocess.SubprocessError:
            return "Неизвестный тип"
    
    def _create_info_window(self, title: str) -> Tuple[QMainWindow, QTextEdit]:
        """Создает стандартное окно для отображения информации."""
        window = QMainWindow(self)
        window.setWindowTitle(title)
        window.setMinimumSize(QSize(800, 600))
        
        # Центральный виджет с градиентным фоном
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        # Градиентный фон
        central_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1a2e, stop:1 #16213e);
            border-radius: 10px;
        """)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Заголовок окна
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("""
            color: white;
            padding: 15px;
            background-color: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Текстовое поле с прокруткой
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Consolas", 10))
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.2);
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        scroll = QScrollArea()
        scroll.setWidget(text_edit)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        layout.addWidget(scroll)
        
        return window, text_edit
    
    def analyze_drives(self) -> None:
        """Анализ и отображение информации о накопителях."""
        self.analysis_window, self.drives_text = self._create_info_window("Анализ накопителей")
        
        # Кнопка обновления
        update_btn = self._create_button("Обновить информацию", "#3498db")
        update_btn.clicked.connect(self._update_drives_info)
        
        layout = self.analysis_window.centralWidget().layout()
        layout.addWidget(update_btn)
        
        self._update_drives_info()
        self.analysis_window.show()
    
    def _update_drives_info(self) -> None:
        """Обновляет информацию о дисках в столбик."""
        drives_info = []
        for partition in psutil.disk_partitions(all=False):
            info = self._get_drive_info(partition)
            
            if "error" in info:
                drives_info.append(f"""
                    <div style="margin-bottom: 20px; border: 1px solid #444; border-radius: 5px; padding: 10px; background-color: rgba(255,0,0,0.1);">
                        <span style="color: #e74c3c; font-weight: bold;">❌ Ошибка:</span> {info['error']}
                    </div>
                """)
                continue
                
            # Определяем иконку в зависимости от типа диска
            if "SSD" in info['type']:
                icon = "💾"  # Иконка SSD
                type_color = "#3498db"
            elif "HDD" in info['type']:
                icon = "💽"  # Иконка HDD
                type_color = "#f39c12"
            else:
                icon = "📁"  # Иконка по умолчанию
                type_color = "#aaaaaa"
                
            # Цвет для процента заполнения
            percent_color = "#2ecc71"  # Зеленый
            if info['percent'] > 90:
                percent_color = "#e74c3c"  # Красный
            elif info['percent'] > 70:
                percent_color = "#f39c12"  # Оранжевый
            
            # Прогресс-бар в HTML
            progress_bar = f"""
            <div style="width: 100%; background-color: #353535; border-radius: 3px; margin: 5px 0;">
                <div style="width: {info['percent']}%; height: 20px; background-color: {percent_color}; border-radius: 3px; 
                     display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                    {info['percent']}%
                </div>
            </div>
            """
                
            drives_info.append(f"""
                <div style="margin-bottom: 30px; border: 1px solid #444; border-radius: 8px; padding: 15px; background-color: rgba(255,255,255,0.05);">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
                        <h3 style="margin: 0; color: white;">{info['device']}</h3>
                    </div>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px;">
                        <tr>
                            <td style="width: 40%; padding: 5px 0; color: #aaaaaa;">Точка монтирования:</td>
                            <td style="padding: 5px 0; color: white;">{info['mountpoint']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; color: #aaaaaa;">Тип накопителя:</td>
                            <td style="padding: 5px 0; color: {type_color};">{info['type']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; color: #aaaaaa;">Файловая система:</td>
                            <td style="padding: 5px 0; color: white;">{info['fstype']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; color: #aaaaaa;">Общий размер:</td>
                            <td style="padding: 5px 0; color: white;">{info['total'] / (1024**3):.2f} ГБ</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; color: #aaaaaa;">Использовано:</td>
                            <td style="padding: 5px 0; color: white;">{info['used'] / (1024**3):.2f} ГБ</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; color: #aaaaaa;">Свободно:</td>
                            <td style="padding: 5px 0; color: white;">{info['free'] / (1024**3):.2f} ГБ</td>
                        </tr>
                    </table>
                    
                    <div style="margin-top: 10px;">
                        <div style="color: #aaaaaa; margin-bottom: 5px;">Заполнение диска:</div>
                        {progress_bar}
                    </div>
                </div>
            """)

        self.drives_text.setHtml('<div style="font-family: Arial;">' + ''.join(drives_info) + '</div>')
    
    def show_disk_usage_graph(self) -> None:
        """Отображает график использования дисков."""
        try:
            partitions = psutil.disk_partitions(all=False)
            if not partitions:
                raise ValueError("Не найдено доступных разделов диска")
                
            labels = []
            sizes = []
            colors = []

            for partition in partitions:
                usage = psutil.disk_usage(partition.mountpoint)
                labels.append(f"{partition.device}\n({partition.mountpoint})")
                sizes.append(usage.percent)
                
                # Разные цвета для разных уровней заполнения
                if usage.percent > 90:
                    colors.append("#e74c3c")  # Красный
                elif usage.percent > 70:
                    colors.append("#f39c12")  # Оранжевый
                else:
                    colors.append("#2ecc71")  # Зеленый

            # Создаем фигуру с темной темой
            plt.style.use('dark_background')
            fig = Figure(figsize=(12, 8), facecolor='#2a2a2a')
            ax = fig.add_subplot(111, facecolor='#2a2a2a')
            
            # Гистограмма с градиентной заливкой
            bars = ax.bar(labels, sizes, color=colors, edgecolor='white', linewidth=1)
            
            # Добавляем значения на столбцы
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2., 
                    height,
                    f'{height:.1f}%', 
                    ha='center', 
                    va='bottom',
                    color='white',
                    fontsize=10,
                    fontweight='bold'
                )

            # Настройка осей и заголовка
            ax.set_title('Использование дискового пространства', 
                        fontsize=16, color='white', pad=20)
            ax.set_xlabel('Диски', fontsize=14, color='white')
            ax.set_ylabel('Процент использования (%)', fontsize=14, color='white')
            ax.set_ylim(0, 100)
            
            # Настройка сетки
            ax.grid(True, linestyle='--', alpha=0.3, color='white')
            
            # Настройка цветов меток
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            
            # Убираем рамку
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            fig.tight_layout()
            
            self._show_graph_window(fig, "График использования дисков")
            
        except Exception as e:
            self.show_error_report(e, "Построение графика использования дисков")
    
    def _show_graph_window(self, figure: Figure, title: str) -> None:
        """Создает окно для отображения графика."""
        window = QMainWindow(self)
        window.setWindowTitle(title)
        window.setMinimumSize(QSize(1000, 800))
        
        # Центральный виджет с темным фоном
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #2a2a2a;")
        window.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Холст для графика
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        
        # Кнопка сохранения
        save_btn = self._create_button("Сохранить график", "#2ecc71")
        save_btn.clicked.connect(lambda: self._save_figure(figure))
        layout.addWidget(save_btn)
        
        window.show()
    
    def _save_figure(self, figure: Figure) -> None:
        """Сохраняет график в файл."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить график",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        
        if file_name:
            try:
                figure.savefig(file_name, dpi=300, facecolor=figure.get_facecolor())
                QMessageBox.information(self, "Успех", "График успешно сохранен!")
            except Exception as e:
                self.show_error_report(e, "Сохранение графика")
    
    def show_maintenance_tips(self) -> None:
        """Отображает советы по обслуживанию дисков."""
        tips_window, text_edit = self._create_info_window("Советы по обслуживанию")
        
        tips_text = """
        <div style="font-family: Arial; font-size: 12px; line-height: 1.6;">
            <h2 style="color: #6a3093;">🔹 Для SSD накопителей:</h2>
            <ul>
                <li>Не заполняйте полностью (оставляйте 10-15% свободного места)</li>
                <li>Включите TRIM (для Windows: <code>fsutil behavior set DisableDeleteNotify 0</code>)</li>
                <li>Регулярно обновляйте прошивку</li>
                <li>Избегайте частой дефрагментации (это сокращает срок службы)</li>
            </ul>
            
            <h2 style="color: #e74c3c;">🔹 Для HDD накопителей:</h2>
            <ul>
                <li>Периодически проверяйте диск на ошибки</li>
                <li>Избегайте ударов и вибраций</li>
                <li>Контролируйте температуру (не выше 45°C)</li>
                <li>Проводите дефрагментацию раз в 3-6 месяцев</li>
            </ul>
            
            <h2 style="color: #3498db;">🔹 Для всех накопителей:</h2>
            <ul>
                <li>Регулярно создавайте резервные копии</li>
                <li>Используйте стабилизированное питание</li>
                <li>Проверяйте S.M.A.R.T. статус диска</li>
                <li>Следите за свободным местом (минимум 10-15%)</li>
                <li>Избегайте резкого отключения питания</li>
            </ul>
        </div>
        """
        
        text_edit.setHtml(tips_text)
        tips_window.show()
    
    def show_system_info(self) -> None:
        """Показывает информацию о системе."""
        info_window, text_edit = self._create_info_window("Информация о системе")
        
        try:
            # Информация о системе
            sys_info = f"""
            <div style="font-family: Arial; font-size: 12px; line-height: 1.6;">
                <h2 style="color: #6a3093;">Системная информация</h2>
                <p><b>ОС:</b> {platform.system()} {platform.release()}</p>
                <p><b>Версия:</b> {platform.version()}</p>
                <p><b>Архитектура:</b> {platform.machine()}</p>
                <p><b>Процессор:</b> {platform.processor()}</p>
                <p><b>Память:</b> {psutil.virtual_memory().total / (1024**3):.2f} ГБ</p>
                
                <h2 style="color: #e74c3c;">Дисковая подсистема</h2>
                <p><b>Всего дисков:</b> {len(psutil.disk_partitions(all=False))}</p>
            """
            
            # Информация о дисках
            disk_info = []
            for partition in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append(f"""
                        <p><b>Диск:</b> {partition.device}</p>
                        <p><b>Точка монтирования:</b> {partition.mountpoint}</p>
                        <p><b>Файловая система:</b> {partition.fstype}</p>
                        <p><b>Общий размер:</b> {usage.total / (1024**3):.2f} ГБ</p>
                        <hr style="border-color: #444; margin: 10px 0;">
                    """)
                except Exception as e:
                    self.show_error_report(e, "Получение информации о разделе диска")
                    continue
            
            text_edit.setHtml(sys_info + "".join(disk_info) + "</div>")
            info_window.show()
        except Exception as e:
            self.show_error_report(e, "Получение системной информации")


def main() -> None:
    """Точка входа в приложение."""
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        font = QFont("Arial", 10)
        app.setFont(font)
        
        window = DriveAnalyzerApp()
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        # Если произошла критическая ошибка при запуске
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("Критическая ошибка")
        error_msg.setText("Не удалось запустить приложение")
        error_msg.setInformativeText(str(e))
        error_msg.setDetailedText(traceback.format_exc())
        error_msg.exec_()


if __name__ == "__main__":
    main()
