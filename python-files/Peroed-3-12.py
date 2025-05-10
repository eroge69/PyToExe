import os
import sys
import json
import threading
import tempfile
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
                            QFileDialog, QAction, QToolBar, QLabel, QMenu, QMessageBox,
                            QListWidget, QListWidgetItem, QPushButton, QDialog, QLineEdit,
                            QFormLayout, QDialogButtonBox, QFrame, QShortcut, QGraphicsView,
                            QGraphicsScene, QGraphicsProxyWidget)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QTimer, QSize, QRectF
from PyQt5.QtGui import QClipboard, QIcon, QFont, QColor, QKeySequence
import folium
from folium.plugins import MousePosition
from qt_material import apply_stylesheet

class DeviceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить устройство")
        self.setWindowIcon(QIcon("icon.ico"))
        
        layout = QFormLayout(self)
        
        self.ip_edit = QLineEdit()
        self.ip_edit.setStyleSheet("color: #E0E0E0; background-color: #424242;")
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet("color: #E0E0E0; background-color: #424242;")
        self.coords_edit = QLineEdit()
        self.coords_edit.setStyleSheet("color: #E0E0E0; background-color: #424242;")
        
        layout.addRow("IP-адрес:", self.ip_edit)
        layout.addRow("Имя устройства:", self.name_edit)
        layout.addRow("Координаты (широта долгота):", self.coords_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet("""
            QPushButton {
                color: #E0E0E0;
                background-color: #424242;
                padding: 5px 10px;
            }
        """)
        
        layout.addRow(buttons)
    
    def get_data(self):
        return {
            "ip": self.ip_edit.text(),
            "name": self.name_edit.text(),
            "coords": self.coords_edit.text()
        }

class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Создаем графическую сцену
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background: transparent; border: none;")
        
        # Создаем контейнер для карты
        self.map_container = QWidget()
        self.map_container.setStyleSheet("background: transparent;")
        self.map_proxy = self.scene.addWidget(self.map_container)
        
        # Браузер с картой
        self.browser = QWebEngineView()
        self.browser.setStyleSheet("background: transparent;")
        browser_proxy = self.scene.addWidget(self.browser)
        browser_proxy.setPos(0, 0)
        
        #Панель для закрытия нижней части карты
        #Панель для закрытия нижней части карты
        # self.bottom_panel = QFrame()
        # self.bottom_panel.setFixedHeight(40)
        # self.bottom_panel.setStyleSheet("background-color: #424242; border: none;")
        # panel_proxy = self.scene.addWidget(self.bottom_panel)
        # panel_proxy.setZValue(1)  # Устанавливаем выше карты
        # panel_proxy.setPos(0, self.scene.height())
        
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)
        
        self.temp_dir = tempfile.gettempdir()
        self.temp_file = os.path.join(self.temp_dir, "osm_map_temp.html")
        self.init_map()
        
        self.browser.setContextMenuPolicy(Qt.NoContextMenu)
        self.tiles_dir = None

    def init_map(self):
        try:
            self.map = folium.Map(location=[55.7558, 37.6173], zoom_start=10)
            MousePosition().add_to(self.map)
            self.save_map()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать карту: {str(e)}")

    def save_map(self):
        try:
            self.map.save(self.temp_file)
            self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath(self.temp_file)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить карту: {str(e)}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.view.setSceneRect(QRectF(0, 0, self.width(), self.height()))
        if hasattr(self, 'browser'):
            self.browser.setFixedSize(self.width(), self.height())
        if hasattr(self, 'bottom_panel'):
            panel_proxy = self.scene.items()[-1]
            panel_proxy.setPos(0, self.height() - 20)

    def load_offline_tiles(self, tiles_dir):
        try:
            if not os.path.exists(tiles_dir):
                QMessageBox.warning(self, "Ошибка", "Указанная папка не существует")
                return
                
            self.tiles_dir = tiles_dir
            self.map = folium.Map(location=[55.7558, 37.6173], zoom_start=10, tiles=None)
            
            abs_tiles_path = os.path.abspath(tiles_dir).replace('\\', '/')
            
            folium.TileLayer(
                tiles=f"file:///{abs_tiles_path}/z{{z}}/{{y}}/{{x}}.png",
                attr="GMT Offline Tiles",
                name="Offline Map",
                min_zoom=0,
                max_zoom=18,
                detect_retina=False
            ).add_to(self.map)
            
            MousePosition().add_to(self.map)
            self.save_map()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", 
                f"Не удалось загрузить автономные тайлы: {str(e)}\n"
                f"Проверьте структуру папок: z{{Z}}/{{Y}}/{{X}}.png")

    def load_online_map(self):
        try:
            self.map = folium.Map(location=[55.7558, 37.6173], zoom_start=10)
            MousePosition().add_to(self.map)
            self.save_map()
            self.tiles_dir = None
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить онлайн карту: {str(e)}")

    def add_device_marker(self, lat, lon, name, ip):
        try:
            folium.Marker(
                location=[lat, lon],
                popup=f"{name} ({ip})",
                tooltip=f"{name} ({ip})"
            ).add_to(self.map)
            self.save_map()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить маркер: {str(e)}")

    def toggle_visibility(self):
        self.setVisible(not self.isVisible())

class DeviceWidget(QFrame):
    status_updated = pyqtSignal(str, str)
    
    def __init__(self, ip, name, lat, lon, status="unknown", parent=None):
        super().__init__(parent)
        self.ip = ip
        self.name = name
        self.lat = lat
        self.lon = lon
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(1)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.info_label = QLabel(f"{name} ({ip})")
        self.info_label.setFont(QFont("Arial", 10))
        self.info_label.setStyleSheet("color: #E0E0E0;")
        layout.addWidget(self.info_label)
        
        self.btn_on = QPushButton("ВКЛ")
        self.btn_on.setStyleSheet("""
            background-color: #4CAF50; 
            color: white;
            padding: 5px 10px;
            min-width: 60px;
        """)
        self.btn_on.clicked.connect(self._turn_on)
        layout.addWidget(self.btn_on)
        
        self.btn_off = QPushButton("ВЫКЛ")
        self.btn_off.setStyleSheet("""
            background-color: #F44336; 
            color: white;
            padding: 5px 10px;
            min-width: 60px;
        """)
        self.btn_off.clicked.connect(self._turn_off)
        layout.addWidget(self.btn_off)
        
        self.status_label = QLabel()
        self.update_status(status)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _turn_on(self):
        threading.Thread(target=self._send_turn_on, daemon=True).start()
    
    def _turn_off(self):
        threading.Thread(target=self._send_turn_off, daemon=True).start()
    
    def _send_turn_on(self):
        try:
            response = requests.get(f"http://{self.ip}/on", timeout=2)
            if response.status_code == 200:
                self.status_updated.emit(self.ip, "on")
        except Exception as e:
            self.status_updated.emit(self.ip, "no_connection")
    
    def _send_turn_off(self):
        try:
            response = requests.get(f"http://{self.ip}/off", timeout=2)
            if response.status_code == 200:
                self.status_updated.emit(self.ip, "off")
        except Exception as e:
            self.status_updated.emit(self.ip, "no_connection")
    
    def update_status(self, status):
        if status == "on":
            self.status_label.setText("ВКЛЮЧЕНО")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        elif status == "off":
            self.status_label.setText("ВЫКЛЮЧЕНО")
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")
        else:
            self.status_label.setText("НЕТ СВЯЗИ")
            self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пероед-GUI-3-3")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("icon.ico"))
        
        self.config_file = "config.json"
        self.config = self._load_config()
        self.last_tiles_dir = ""
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.left_panel = QWidget()
        self.left_panel.setMaximumWidth(400)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(5, 5, 5, 5)
        
        self.control_panel = QWidget()
        self.control_layout = QHBoxLayout(self.control_panel)
        self.control_layout.setContentsMargins(0, 0, 0, 0)
        self.control_layout.setSpacing(5)
        
        self.btn_add = QPushButton("Добавить")
        self.btn_add.setIcon(QIcon.fromTheme("list-add"))
        self.btn_add.setStyleSheet("padding: 5px 10px;")
        self.btn_add.clicked.connect(self._add_device)
        self.control_layout.addWidget(self.btn_add)
        
        self.btn_remove = QPushButton("Удалить")
        self.btn_remove.setIcon(QIcon.fromTheme("list-remove"))
        self.btn_remove.setStyleSheet("padding: 5px 10px;")
        self.btn_remove.clicked.connect(self._remove_device)
        self.control_layout.addWidget(self.btn_remove)
        
        self.btn_on_all = QPushButton("Вкл все")
        self.btn_on_all.setIcon(QIcon.fromTheme("media-playback-start"))
        self.btn_on_all.setStyleSheet("padding: 5px 10px;")
        self.btn_on_all.clicked.connect(self._turn_on_all)
        self.control_layout.addWidget(self.btn_on_all)
        
        self.btn_off_all = QPushButton("Выкл все")
        self.btn_off_all.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.btn_off_all.setStyleSheet("padding: 5px 10px;")
        self.btn_off_all.clicked.connect(self._turn_off_all)
        self.control_layout.addWidget(self.btn_off_all)
        
        self.left_layout.addWidget(self.control_panel)
        
        self.devices_list = QListWidget()
        self.devices_list.setSelectionMode(QListWidget.SingleSelection)
        self.left_layout.addWidget(self.devices_list)
        
        self.devices_panel = QWidget()
        self.devices_layout = QVBoxLayout(self.devices_panel)
        self.devices_layout.setContentsMargins(0, 5, 0, 0)
        self.devices_layout.setSpacing(5)
        self.left_layout.addWidget(self.devices_panel)
        
        self.main_layout.addWidget(self.left_panel)
        
        self.map_widget = MapWidget()
        self.main_layout.addWidget(self.map_widget)
        
        self.status_bar = self.statusBar()
        self.coords_label = QLabel("Готов к работе")
        self.coords_label.setStyleSheet("color: #E0E0E0;")
        self.status_bar.addPermanentWidget(self.coords_label)
        
        self._load_devices()
        
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_devices_status)
        self.status_timer.start(5000)
        
        self._create_toolbar()
        self._create_shortcuts()
        
        apply_stylesheet(self, theme='dark_blue.xml')
    
    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        online_action = QAction(QIcon.fromTheme("network-wireless"), "Онлайн карта", self)
        online_action.setToolTip("Переключиться на онлайн карту OSM")
        online_action.triggered.connect(self.map_widget.load_online_map)
        toolbar.addAction(online_action)
        
        offline_action = QAction(QIcon.fromTheme("folder-network"), "GMT Тайлы", self)
        offline_action.setToolTip("Загрузить тайлы в формате GMT (z{Z}/{Y}/{X}.png)")
        offline_action.triggered.connect(self._select_tiles_directory)
        toolbar.addAction(offline_action)
        
        toggle_map_action = QAction(QIcon.fromTheme("view-hidden"), "Скрыть/показать карту", self)
        toggle_map_action.setToolTip("Скрыть или показать карту (Ctrl+M)")
        toggle_map_action.triggered.connect(self.map_widget.toggle_visibility)
        toolbar.addAction(toggle_map_action)
        
        help_action = QAction(QIcon.fromTheme("help-contents"), "Инструкция", self)
        help_action.setToolTip("Показать горячие клавиши")
        help_action.triggered.connect(self._show_help)
        toolbar.addAction(help_action)
    
    def _create_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+N"), self, self._add_device)
        QShortcut(QKeySequence("Ctrl+D"), self, self._remove_device)
        QShortcut(QKeySequence("Ctrl+O"), self, self._turn_on_all)
        QShortcut(QKeySequence("Ctrl+F"), self, self._turn_off_all)
        QShortcut(QKeySequence("Ctrl+L"), self, self.map_widget.load_online_map)
        QShortcut(QKeySequence("Ctrl+T"), self, self._select_tiles_directory)
        QShortcut(QKeySequence("Ctrl+M"), self, self.map_widget.toggle_visibility)
        QShortcut(QKeySequence("F1"), self, self._show_help)
    
    def _show_help(self):
        help_text = """
        <h3>Горячие клавиши:</h3>
        <ul>
            <li><b>Ctrl+N</b> - Добавить новое устройство</li>
            <li><b>Ctrl+D</b> - Удалить выбранное устройство</li>
            <li><b>Ctrl+O</b> - Включить все устройства</li>
            <li><b>Ctrl+F</b> - Выключить все устройства</li>
            <li><b>Ctrl+L</b> - Переключиться на онлайн карту</li>
            <li><b>Ctrl+T</b> - Загрузить оффлайн тайлы</li>
            <li><b>Ctrl+M</b> - Скрыть/показать карту</li>
            <li><b>F1</b> - Показать эту инструкцию</li>
        </ul>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Инструкция")
        msg.setIcon(QMessageBox.Information)
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.exec_()
    
    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {"devices": []}
    
    def _save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)
    
    def _load_devices(self):
        self.devices_list.clear()
        for i in reversed(range(self.devices_layout.count())): 
            self.devices_layout.itemAt(i).widget().setParent(None)
        
        for device in self.config["devices"]:
            item = QListWidgetItem(f"{device['name']} ({device['ip']})")
            item.setData(Qt.UserRole, device["ip"])
            self.devices_list.addItem(item)
            
            device_widget = DeviceWidget(
                device["ip"],
                device["name"],
                device["lat"],
                device["lon"],
                device.get("status", "unknown")
            )
            device_widget.status_updated.connect(self._update_device_status)
            self.devices_layout.addWidget(device_widget)
            
            self.map_widget.add_device_marker(
                device["lat"],
                device["lon"],
                device["name"],
                device["ip"]
            )
    
    def _update_devices_status(self):
        for device in self.config["devices"]:
            threading.Thread(target=self._check_device_status, args=(device["ip"],), daemon=True).start()
    
    def _check_device_status(self, ip):
        try:
            response = requests.get(f"http://{ip}/status", timeout=2)
            if response.status_code == 200:
                status = response.text.strip()
                self._update_device_status(ip, status)
        except Exception as e:
            self._update_device_status(ip, "no_connection")
    
    def _update_device_status(self, ip, status):
        for device in self.config["devices"]:
            if device["ip"] == ip:
                device["status"] = status
                break
        
        for i in range(self.devices_layout.count()):
            widget = self.devices_layout.itemAt(i).widget()
            if isinstance(widget, DeviceWidget) and widget.ip == ip:
                widget.update_status(status)
                break
        
        self._save_config()
    
    def _add_device(self):
        dialog = DeviceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                lat, lon = map(float, data["coords"].split())
                self.config["devices"].append({
                    "ip": data["ip"],
                    "name": data["name"],
                    "lat": lat,
                    "lon": lon,
                    "status": "unknown"
                })
                self._save_config()
                self._load_devices()
                threading.Thread(target=self._check_device_status, args=(data["ip"],), daemon=True).start()
            except ValueError:
                QMessageBox.critical(self, "Ошибка", "Некорректный формат координат. Введите два числа через пробел.")
    
    def _remove_device(self):
        selected = self.devices_list.currentRow()
        if selected >= 0:
            ip = self.devices_list.item(selected).data(Qt.UserRole)
            device_name = self.devices_list.item(selected).text()
            reply = QMessageBox.question(
                self, 
                "Подтверждение удаления", 
                f"Вы уверены, что хотите удалить устройство {device_name}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.config["devices"] = [d for d in self.config["devices"] if d["ip"] != ip]
                self._save_config()
                self._load_devices()
    
    def _turn_on_all(self):
        for device in self.config["devices"]:
            threading.Thread(target=self._send_turn_on, args=(device["ip"],), daemon=True).start()
    
    def _turn_off_all(self):
        for device in self.config["devices"]:
            threading.Thread(target=self._send_turn_off, args=(device["ip"],), daemon=True).start()
    
    def _send_turn_on(self, ip):
        try:
            response = requests.get(f"http://{ip}/on", timeout=2)
            if response.status_code == 200:
                self._update_device_status(ip, "on")
        except Exception as e:
            self._update_device_status(ip, "no_connection")
    
    def _send_turn_off(self, ip):
        try:
            response = requests.get(f"http://{ip}/off", timeout=2)
            if response.status_code == 200:
                self._update_device_status(ip, "off")
        except Exception as e:
            self._update_device_status(ip, "no_connection")
    
    def _select_tiles_directory(self):
        tiles_dir = QFileDialog.getExistingDirectory(
            self, 
            "Выберите папку с тайлами (формат GMT: z{Z}/{Y}/{X}.png)", 
            self.last_tiles_dir if self.last_tiles_dir else "", 
            QFileDialog.ShowDirsOnly
        )
        if tiles_dir:
            self.last_tiles_dir = tiles_dir
            self.map_widget.load_offline_tiles(tiles_dir)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Критическая ошибка", f"Не удалось запустить приложение: {str(e)}")
        sys.exit(1)