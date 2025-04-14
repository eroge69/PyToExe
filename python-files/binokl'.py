import sys
import json

# Проверка, какой набор модулей Qt доступен. Если возникают проблемы с PyQt5, можно попробовать использовать PySide6.
# Для сборки через auto-py-to-exe рекомендуется использовать стабильную версию PyQt5 (например, 5.15.9) или указать дополнительные hidden-imports.

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
    QT_LIB = 'PyQt5'
except ImportError:
    try:
        from PySide6 import QtWidgets, QtGui, QtCore
        QT_LIB = 'PySide6'
    except ImportError:
        print('Ошибка: Не найден ни PyQt5, ни PySide6. Установите один из пакетов.')
        sys.exit(1)

CONFIG_FILE = 'lag_switch_config.json'

class LagSwitchUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lag Switch by Binokl")
        self.setGeometry(100, 100, 400, 400)
        self.initUI()
        self.load_config()
        self.create_system_tray()

    def initUI(self):
        # Главный виджет и layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Tab widget для вкладок
        self.tabs = QtWidgets.QTabWidget()
        self.layout.addWidget(self.tabs)

        self.main_tab = QtWidgets.QWidget()
        self.settings_tab = QtWidgets.QWidget()

        self.tabs.addTab(self.main_tab, "Main")
        self.tabs.addTab(self.settings_tab, "Settings")

        self.init_main_tab()
        self.init_settings_tab()

    def init_main_tab(self):
        layout = QtWidgets.QVBoxLayout()
        self.main_tab.setLayout(layout)

        # 1. Enable Lag Switch
        self.cb_enable = QtWidgets.QCheckBox("Enable Lag Switch by Binokl")
        self.cb_enable.setChecked(True)
        layout.addWidget(self.cb_enable)

        # 2. Keybind (default Insert)
        keybind_layout = QtWidgets.QHBoxLayout()
        lbl_keybind = QtWidgets.QLabel("Keybind:")
        self.edit_keybind = QtWidgets.QLineEdit()
        self.edit_keybind.setText("Insert")
        keybind_layout.addWidget(lbl_keybind)
        keybind_layout.addWidget(self.edit_keybind)
        layout.addLayout(keybind_layout)

        # 3. Traffic ComboBox
        traffic_layout = QtWidgets.QHBoxLayout()
        lbl_traffic = QtWidgets.QLabel("Traffic:")
        self.combo_traffic = QtWidgets.QComboBox()
        self.combo_traffic.addItems(["Incoming", "Outgoing", "All"])
        traffic_layout.addWidget(lbl_traffic)
        traffic_layout.addWidget(self.combo_traffic)
        layout.addLayout(traffic_layout)

        # 4. Duration
        duration_layout = QtWidgets.QHBoxLayout()
        lbl_duration = QtWidgets.QLabel("Duration (ms):")
        self.spin_duration = QtWidgets.QSpinBox()
        self.spin_duration.setRange(0, 10000)
        self.spin_duration.setValue(100)
        duration_layout.addWidget(lbl_duration)
        duration_layout.addWidget(self.spin_duration)
        layout.addLayout(duration_layout)

        # 5. Delay After
        delay_layout = QtWidgets.QHBoxLayout()
        lbl_delay = QtWidgets.QLabel("Delay After (ms):")
        self.spin_delay = QtWidgets.QSpinBox()
        self.spin_delay.setRange(0, 10000)
        self.spin_delay.setValue(50)
        delay_layout.addWidget(lbl_delay)
        delay_layout.addWidget(self.spin_delay)
        layout.addLayout(delay_layout)

        # 6. Hold Key функция
        self.cb_hold_key = QtWidgets.QCheckBox("Hold Key ")
        self.cb_hold_key.setChecked(False)
        layout.addWidget(self.cb_hold_key)

        layout.addStretch()

    def init_settings_tab(self):
        layout = QtWidgets.QVBoxLayout()
        self.settings_tab.setLayout(layout)

        # Сохранить/Сброс конфигурации
        config_buttons_layout = QtWidgets.QHBoxLayout()
        self.btn_save = QtWidgets.QPushButton("Save Config")
        self.btn_reset = QtWidgets.QPushButton("Reset Config")
        config_buttons_layout.addWidget(self.btn_save)
        config_buttons_layout.addWidget(self.btn_reset)
        layout.addLayout(config_buttons_layout)

        self.btn_save.clicked.connect(self.save_config)
        self.btn_reset.clicked.connect(self.reset_config)

        # Randomization Checkbox
        self.cb_random = QtWidgets.QCheckBox("Randomization")
        self.cb_random.setChecked(False)
        layout.addWidget(self.cb_random)

        # Группа настроек Lag Switch
        lag_group = QtWidgets.QGroupBox("Lag Switch Settings (ms)")
        lag_layout = QtWidgets.QHBoxLayout()
        lag_group.setLayout(lag_layout)
        lbl_min_lag = QtWidgets.QLabel("Min:")
        self.spin_min_lag = QtWidgets.QSpinBox()
        self.spin_min_lag.setRange(0, 10000)
        self.spin_min_lag.setValue(50)
        lbl_max_lag = QtWidgets.QLabel("Max:")
        self.spin_max_lag = QtWidgets.QSpinBox()
        self.spin_max_lag.setRange(0, 10000)
        self.spin_max_lag.setValue(300)
        lag_layout.addWidget(lbl_min_lag)
        lag_layout.addWidget(self.spin_min_lag)
        lag_layout.addWidget(lbl_max_lag)
        lag_layout.addWidget(self.spin_max_lag)
        layout.addWidget(lag_group)

        # Группа настроек Fake Lag
        fake_group = QtWidgets.QGroupBox("Fake Lag Settings (ms)")
        fake_layout = QtWidgets.QHBoxLayout()
        fake_group.setLayout(fake_layout)
        lbl_min_fake = QtWidgets.QLabel("Min:")
        self.spin_min_fake = QtWidgets.QSpinBox()
        self.spin_min_fake.setRange(0, 10000)
        self.spin_min_fake.setValue(50)
        lbl_max_fake = QtWidgets.QLabel("Max:")
        self.spin_max_fake = QtWidgets.QSpinBox()
        self.spin_max_fake.setRange(0, 10000)
        self.spin_max_fake.setValue(300)
        fake_layout.addWidget(lbl_min_fake)
        fake_layout.addWidget(self.spin_min_fake)
        fake_layout.addWidget(lbl_max_fake)
        fake_layout.addWidget(self.spin_max_fake)
        layout.addWidget(fake_group)

        layout.addStretch()

    def save_config(self):
        config = {
            'enable': self.cb_enable.isChecked(),
            'keybind': self.edit_keybind.text(),
            'traffic': self.combo_traffic.currentText(),
            'duration': self.spin_duration.value(),
            'delay_after': self.spin_delay.value(),
            'hold_key': self.cb_hold_key.isChecked(),
            'randomization': self.cb_random.isChecked(),
            'lag_switch': {
                'min': self.spin_min_lag.value(),
                'max': self.spin_max_lag.value()
            },
            'fake_lag': {
                'min': self.spin_min_fake.value(),
                'max': self.spin_max_fake.value()
            }
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            QtWidgets.QMessageBox.information(self, "Config Saved", "Configuration saved successfully.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to save configuration: {e}")

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            self.cb_enable.setChecked(config.get('enable', True))
            self.edit_keybind.setText(config.get('keybind', 'Insert'))
            traffic = config.get('traffic', 'Incoming')
            index = self.combo_traffic.findText(traffic)
            if index >= 0:
                self.combo_traffic.setCurrentIndex(index)
            self.spin_duration.setValue(config.get('duration', 100))
            self.spin_delay.setValue(config.get('delay_after', 50))
            self.cb_hold_key.setChecked(config.get('hold_key', False))
            self.cb_random.setChecked(config.get('randomization', False))
            lag = config.get('lag_switch', {})
            self.spin_min_lag.setValue(lag.get('min', 50))
            self.spin_max_lag.setValue(lag.get('max', 300))
            fake = config.get('fake_lag', {})
            self.spin_min_fake.setValue(fake.get('min', 50))
            self.spin_max_fake.setValue(fake.get('max', 300))
        except Exception as e:
            # Если конфигурация отсутствует или произошла ошибка, используем значения по умолчанию
            pass

    def reset_config(self):
        self.cb_enable.setChecked(True)
        self.edit_keybind.setText("Insert")
        self.combo_traffic.setCurrentIndex(0)
        self.spin_duration.setValue(100)
        self.spin_delay.setValue(50)
        self.cb_hold_key.setChecked(False)
        self.cb_random.setChecked(False)
        self.spin_min_lag.setValue(50)
        self.spin_max_lag.setValue(300)
        self.spin_min_fake.setValue(50)
        self.spin_max_fake.setValue(300)
        self.save_config()
        QtWidgets.QMessageBox.information(self, "Config Reset", "Configuration reset to default.")

    def create_system_tray(self):
        # Создание системного трей-иконки для фоновой работы
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        # Используем стандартную иконку
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Lag Switch by Binokl")

        show_action = QtWidgets.QAction("Show", self)
        quit_action = QtWidgets.QAction("Quit", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QtWidgets.QApplication.quit)

        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.showNormal()
            self.activateWindow()

    def closeEvent(self, event):
        # При попытке закрытия окна, сворачиваем его в трей
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Running in background",
            "Lag Switch is still running. Double-click the tray icon to restore.",
            QtWidgets.QSystemTrayIcon.Information,
            2000
        )

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # Применяем стиль для привлекательного интерфейса
    app.setStyle('Fusion')
    window = LagSwitchUI()
    window.show()
    sys.exit(app.exec_())

