import sys
import json
import serial
import serial.tools.list_ports
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import (QIcon, QKeySequence, QPainter, QColor,
                         QConicalGradient, QLinearGradient, QBrush, QFont)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QComboBox,
                             QGroupBox, QStyleFactory, QKeySequenceEdit)

SETTINGS_FILE = "bindings.json"


class AudioController:
    def __init__(self):
        self.volume_interface = None
        try:
            devices = AudioUtilities.GetSpeakers()
            self.volume_interface = devices.Activate(
                IAudioEndpointVolume._iid_,
                CLSCTX_ALL,
                None)
            self.volume = self.volume_interface.QueryInterface(IAudioEndpointVolume)
        except Exception as e:
            print(f"Audio init error: {e}")

    def set_volume(self, level):
        if self.volume_interface:
            try:
                min_db = self.volume.GetVolumeRange()[0]
                max_db = self.volume.GetVolumeRange()[1]
                volume_db = min_db + (max_db - min_db) * level
                self.volume.SetMasterVolumeLevel(volume_db, None)
            except Exception as e:
                print(f"Volume control error: {e}")

    def get_mute_state(self):
        if self.volume_interface:
            try:
                return self.volume.GetMute()
            except Exception as e:
                print(f"Mute state error: {e}")
        return None


class SerialThread(QThread):
    data_received = pyqtSignal(str, int, str)
    connected = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.serial = None
        self.running = True

    def run(self):
        while self.running:
            if self.serial and self.serial.is_open:
                try:
                    line = self.serial.readline().decode().strip()
                    if line.startswith("BTN:"):
                        parts = line.split(':')
                        btn_num = int(parts[1])
                        state = parts[2]
                        self.data_received.emit('BTN', btn_num, state)
                    elif line.startswith("POT:"):
                        pot_value = int(line.split(':')[1])
                        self.data_received.emit('POT', pot_value, '')
                except Exception as e:
                    print(f"Serial error: {e}")
                    self.connected.emit(False)
                    self.serial.close()
            else:
                self.msleep(100)

    def connect(self, port):
        try:
            self.serial = serial.Serial(port, 115200, timeout=1)
            self.connected.emit(True)
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected.emit(False)

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.connected.emit(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio_controller = AudioController()
        self.current_bindings = self.load_bindings()
        self.button_states = [False] * 4
        self.setWindowTitle("Arduino Controller")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()
        self.init_serial()

    def init_serial(self):
        self.serial_thread = SerialThread()
        self.serial_thread.data_received.connect(self.handle_data)
        self.serial_thread.connected.connect(self.handle_connection)
        self.serial_thread.start()

    def init_ui(self):
        self.angle = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_background)
        self.animation_timer.start(30)

        self.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(255, 255, 255, 100);
                border-radius: 8px;
                margin-top: 1ex;
                background-color: rgba(40, 40, 40, 180);
            }
            QGroupBox::title {
                color: white;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(255, 255, 255, 150);
                border-radius: 5px;
                padding: 8px;
                min-width: 100px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
            QComboBox {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(255, 255, 255, 150);
                padding: 5px;
                min-width: 120px;
                color: white;
            }
            QKeySequenceEdit {
                background-color: rgba(70, 70, 70, 200);
                color: white;
                border: 1px solid rgba(255, 255, 255, 150);
                border-radius: 3px;
                padding: 5px;
            }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.create_connection_group()
        self.create_bindings_group()
        self.create_volume_group()
        self.create_potentiometer_group()

    def create_connection_group(self):
        self.connection_group = QGroupBox("Настройки подключения")
        self.connection_layout = QHBoxLayout()

        self.port_combo = QComboBox()
        self.refresh_ports()
        self.connect_btn = QPushButton("Подключить")
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.connection_status = QLabel("Отключено")
        self.connection_status.setStyleSheet("font-weight: bold;")

        self.connection_layout.addWidget(QLabel("Порт:"))
        self.connection_layout.addWidget(self.port_combo)
        self.connection_layout.addWidget(self.connect_btn)
        self.connection_layout.addWidget(self.connection_status)
        self.connection_group.setLayout(self.connection_layout)
        self.main_layout.addWidget(self.connection_group)

    def create_bindings_group(self):
        self.bindings_group = QGroupBox("Состояние кнопок и настройки")
        self.bindings_layout = QVBoxLayout()

        self.button_widgets = []
        for i in range(4):
            widget = QWidget()
            layout = QHBoxLayout()

            state_label = QLabel(f"Кнопка {i + 1}:")
            state_label.setFont(QFont("Arial", 12))
            self.state_indicator = QLabel("Отпущена")
            self.state_indicator.setStyleSheet("font-weight: bold;")

            key_edit = QKeySequenceEdit()
            key_edit.setMaximumWidth(150)
            if str(i) in self.current_bindings:
                key_edit.setKeySequence(QKeySequence(self.current_bindings[str(i)]))

            apply_btn = QPushButton("Применить")
            apply_btn.clicked.connect(self.create_apply_handler(i, key_edit))
            apply_btn.setEnabled(False)

            key_edit.keySequenceChanged.connect(lambda _, btn=apply_btn: btn.setEnabled(True))

            layout.addWidget(state_label)
            layout.addWidget(self.state_indicator)
            layout.addWidget(key_edit)
            layout.addWidget(apply_btn)

            widget.setLayout(layout)
            self.button_widgets.append((key_edit, apply_btn, self.state_indicator))
            self.bindings_layout.addWidget(widget)

        self.bindings_group.setLayout(self.bindings_layout)
        self.main_layout.addWidget(self.bindings_group)

    def create_volume_group(self):
        self.volume_group = QGroupBox("Управление громкостью")
        volume_layout = QHBoxLayout()

        self.volume_label = QLabel("Громкость: 0%")
        self.volume_label.setStyleSheet("font-size: 18px; color: #88ff88;")

        # Инициализация кнопки с правильным начальным состоянием
        self.mute_button = QPushButton()
        self.update_mute_button_text()

        self.mute_button.clicked.connect(self.toggle_mute)

        volume_layout.addWidget(self.volume_label)
        volume_layout.addWidget(self.mute_button)
        self.volume_group.setLayout(volume_layout)
        self.main_layout.addWidget(self.volume_group)

    def update_mute_button_text(self):
        mute_state = self.audio_controller.get_mute_state()
        if mute_state is not None:
            self.mute_button.setText("Unmute" if mute_state else "Mute")
        else:
            self.mute_button.setText("Mute")

    def create_potentiometer_group(self):
        self.potentiometer_group = QGroupBox("Потенциометр")
        self.pot_layout = QVBoxLayout()

        self.pot_value = QLabel("0%")
        self.pot_value.setAlignment(Qt.AlignCenter)
        self.pot_value.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #88ff88;
        """)

        self.pot_layout.addWidget(self.pot_value)
        self.potentiometer_group.setLayout(self.pot_layout)
        self.main_layout.addWidget(self.potentiometer_group)

    def paintEvent(self, event):
        painter = QPainter(self)

        gradient = QConicalGradient(self.rect().center(), self.angle)
        colors = [
            QColor(255, 0, 0), QColor(255, 255, 0),
            QColor(0, 255, 0), QColor(0, 255, 255),
            QColor(0, 0, 255), QColor(255, 0, 255),
            QColor(255, 0, 0)
        ]
        for i, color in enumerate(colors):
            gradient.setColorAt(i / 6, color)

        overlay = QLinearGradient(0, 0, 0, self.height())
        overlay.setColorAt(0, QColor(0, 0, 0, 180))
        overlay.setColorAt(1, QColor(0, 0, 0, 220))

        painter.fillRect(self.rect(), QBrush(gradient))
        painter.fillRect(self.rect(), QBrush(overlay))

    def update_background(self):
        self.angle = (self.angle + 1.5) % 360
        self.update()

    def create_apply_handler(self, button_idx, key_edit):
        def handler():
            sequence = key_edit.keySequence().toString()
            self.current_bindings[str(button_idx)] = sequence
            self.save_bindings()
            key_edit.clearFocus()
            self.button_widgets[button_idx][1].setEnabled(False)

        return handler

    def load_bindings(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_bindings(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.current_bindings, f)

    def handle_data(self, data_type, value, state):
        if data_type == 'BTN':
            btn_num = value
            state_text = "Нажата" if state == "PRESSED" else "Отпущена"
            color = "#ff8888" if state == "PRESSED" else "#88ff88"
            self.button_widgets[btn_num][2].setText(state_text)
            self.button_widgets[btn_num][2].setStyleSheet(f"color: {color};")

            if state == "PRESSED":
                binding = self.current_bindings.get(str(btn_num))
                if binding:
                    try:
                        keys = [k.strip() for k in binding.split('+') if k.strip()]
                        pyautogui.hotkey(*keys)
                    except Exception as e:
                        print(f"Ошибка эмуляции клавиш: {e}")

        elif data_type == 'POT':
            percentage = int((value / 1023) * 100)
            self.pot_value.setText(f"{percentage}%")
            if self.audio_controller.volume_interface:
                volume_level = percentage / 100
                self.audio_controller.set_volume(volume_level)
                self.volume_label.setText(f"Громкость: {percentage}%")

    def toggle_mute(self):
        if self.audio_controller.volume_interface:
            try:
                is_muted = self.audio_controller.volume.GetMute()
                self.audio_controller.volume.SetMute(not is_muted, None)
                self.update_mute_button_text()
            except Exception as e:
                print(f"Ошибка переключения звука: {e}")

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def toggle_connection(self):
        if self.serial_thread.serial and self.serial_thread.serial.is_open:
            self.serial_thread.disconnect()
        else:
            self.serial_thread.connect(self.port_combo.currentText())

    def handle_connection(self, connected):
        if connected:
            self.connection_status.setText("Подключено ✓")
            self.connection_status.setStyleSheet("color: #88ff88;")
            self.connect_btn.setText("Отключить")
        else:
            self.connection_status.setText("Отключено ✗")
            self.connection_status.setStyleSheet("color: #ff8888;")
            self.connect_btn.setText("Подключить")

    def closeEvent(self, event):
        self.serial_thread.running = False
        self.serial_thread.disconnect()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())