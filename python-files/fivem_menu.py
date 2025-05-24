import sys
import os
import subprocess
import psutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMessageBox, QListWidget, QListWidgetItem, QStackedWidget, QFrame, QToolTip, QSlider, QComboBox, QCheckBox, QScrollArea
)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont
from PyQt5.QtCore import Qt
import pyautogui
import pygetwindow as gw

FIVEM_PATH = r"C:\\Program Files\\FiveM\\FiveM.exe"  # Passe diesen Pfad ggf. an
FIVEM_PROCESS_NAME = "FiveM_b2372_GTAProcess.exe"  # Beispiel, ggf. anpassen

# Offsets zentral importieren
try:
    from offsets import *
except ImportError:
    # Fallback: Platzhalter falls Datei fehlt
    GODMODE_OFFSET = 0x12345678
    HEALTH_OFFSET = 0x12345679
    X_OFFSET = 0x12345680
    Y_OFFSET = 0x12345684
    Z_OFFSET = 0x12345688
    SPEED_OFFSET = 0x12345690
    VEHICLE_SPAWN_OFFSET = 0x12345700
    REPAIR_OFFSET = 0x12345710
    FLIP_OFFSET = 0x12345720
    VEHICLE_SPEED_OFFSET = 0x12345730
    WEAPON_OFFSET = 0x12345740

# Sidebar Kategorien (Icon, Name, Tooltip)
CATEGORIES = [
    ("👤", "Player", "Spieler-Optionen"),
    ("👁️", "ESP", "Visuals & ESP"),
    ("💣", "Weapons", "Waffen & Aim"),
    ("🚗", "Vehicle", "Fahrzeug-Optionen"),
    ("🗂️", "Misc", "Sonstiges"),
    ("⚙️", "Settings", "Einstellungen")
]

class FiveMMenu(QMainWindow):
    def auto_find_offsets_and_port(self):
        # Automatisches Scannen aller nötigen Offsets, Spielport und FiveM-Version beim Start
        try:
            import pymem
            import pymem.pattern
            import socket
            import psutil
            import os
            import re
            pm = self.get_fivem_handle()
            if pm:
                # Mapping: Funktion -> Pattern für Offset
                offset_patterns = {
                    'HEALTH_OFFSET': {
                        'pattern': b'\x8B\x83....\x89\x87....',
                        'used_by': ['heal_player']
                    },
                    'GODMODE_OFFSET': {
                        'pattern': b'\x80\xB8....\x00',
                        'used_by': ['godmode_toggle']
                    },
                    'X_OFFSET': {
                        'pattern': b'\xF3\x0F\x10\x80....',
                        'used_by': ['teleport_player']
                    },
                    'Y_OFFSET': {
                        'pattern': b'\xF3\x0F\x10\x80....',
                        'used_by': ['teleport_player']
                    },
                    'Z_OFFSET': {
                        'pattern': b'\xF3\x0F\x10\x80....',
                        'used_by': ['teleport_player']
                    },
                    'SPEED_OFFSET': {
                        'pattern': b'\xF3\x0F\x11\x80....',
                        'used_by': ['set_player_speed']
                    },
                    'VEHICLE_SPAWN_OFFSET': {
                        'pattern': b'\xC7\x80....',
                        'used_by': ['spawn_vehicle']
                    },
                    'REPAIR_OFFSET': {
                        'pattern': b'\xC7\x80....',
                        'used_by': ['repair_vehicle']
                    },
                    'FLIP_OFFSET': {
                        'pattern': b'\xC7\x80....',
                        'used_by': ['flip_vehicle']
                    },
                    'VEHICLE_SPEED_OFFSET': {
                        'pattern': b'\xF3\x0F\x11\x80....',
                        'used_by': ['set_vehicle_speed']
                    },
                    'WEAPON_OFFSET': {
                        'pattern': b'\xC7\x80....',
                        'used_by': ['spawner_give_weapon']
                    },
                }
                for name, entry in offset_patterns.items():
                    try:
                        matches = pymem.pattern.pattern_scan_all(pm.process_handle, entry['pattern'])
                        if matches:
                            addr = matches[0]
                            globals()[name] = addr
                            print(f"{name} (benötigt für {', '.join(entry['used_by'])}) automatisch gefunden: {hex(addr)}")
                    except Exception as e:
                        print(f"Pattern-Scan für {name} fehlgeschlagen: {e}")
            # Spielport automatisch suchen
            fivem_ports = set()
            for conn in psutil.net_connections(kind='inet'):
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        if FIVEM_PROCESS_NAME.lower() in proc.name().lower():
                            if conn.status == psutil.CONN_ESTABLISHED:
                                fivem_ports.add(conn.laddr.port)
                    except Exception:
                        pass
            if fivem_ports:
                print(f"FiveM läuft auf Port(s): {', '.join(map(str, fivem_ports))}")
                self.fivem_ports = list(fivem_ports)
            else:
                print("Kein aktiver FiveM-Port gefunden.")
            # FiveM-Version automatisch auslesen
            self.fivem_version = None
            try:
                # Suche laufenden FiveM-Prozess und lese die Dateiversion
                for proc in psutil.process_iter(['name', 'exe']):
                    if FIVEM_PROCESS_NAME.lower() in proc.info['name'].lower():
                        exe_path = proc.info.get('exe')
                        if exe_path and os.path.exists(exe_path):
                            import win32api
                            info = win32api.GetFileVersionInfo(exe_path, '\\')
                            ms = info['FileVersionMS']
                            ls = info['FileVersionLS']
                            version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
                            self.fivem_version = version
                            print(f"FiveM Version automatisch erkannt: {version}")
                            break
                if not self.fivem_version:
                    # Fallback: Suche im Installationsverzeichnis
                    exe_path = FIVEM_PATH
                    if os.path.exists(exe_path):
                        import win32api
                        info = win32api.GetFileVersionInfo(exe_path, '\\')
                        ms = info['FileVersionMS']
                        ls = info['FileVersionLS']
                        version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
                        self.fivem_version = version
                        print(f"FiveM Version (Fallback): {version}")
            except Exception as e:
                print(f"Fehler beim Auslesen der FiveM-Version: {e}")
        except Exception as e:
            print(f"Fehler beim automatischen Suchen der Offsets/Ports/Version: {e}")

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Shadow FiveM')
        self.setGeometry(100, 100, 1000, 650)
        self.setStyleSheet("background-color: #18191c; color: #e6e6e6;")
        self.fivem_ports = []
        self.auto_find_offsets_and_port()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        # Sidebar (TZ-Style)
        sidebar = QVBoxLayout()
        sidebar.setSpacing(0)
        sidebar.setAlignment(Qt.AlignTop)
        # Logo oben
        logo = QLabel()
        logo.setPixmap(QPixmap(48, 48))
        logo.setStyleSheet("background: none; min-width:48px; min-height:48px; margin: 24px auto 24px auto;")
        sidebar.addWidget(logo, alignment=Qt.AlignHCenter)
        # Kategorie-Icons
        self.category_list = QListWidget()
        self.category_list.setStyleSheet("QListWidget { background: #18191c; border: none; } QListWidget::item { height: 56px; margin: 0 0 8px 0; border-radius: 16px; text-align: center; color: #888; } QListWidget::item:selected { background: #23232b; color: #b388ff; }")
        for icon, name, tip in CATEGORIES:
            item = QListWidgetItem(f"{icon}")
            item.setFont(QFont('Arial', 24))
            item.setToolTip(tip)
            self.category_list.addItem(item)
        self.category_list.setCurrentRow(2)  # Default: Weapons
        self.category_list.currentRowChanged.connect(self.switch_category)
        sidebar.addWidget(self.category_list)
        sidebar.addStretch()
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(90)
        sidebar_widget.setStyleSheet("background: #18191c;")
        main_layout.addWidget(sidebar_widget)
        # Content-Bereich (TZ-Style)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        # Topbar
        topbar = QHBoxLayout()
        topbar.setContentsMargins(0, 0, 0, 0)
        topbar.setSpacing(0)
        # App-Überschrift links
        app_title = QLabel("Shadow FiveM")
        app_title.setFont(QFont('Arial', 28, QFont.Bold))
        app_title.setStyleSheet("color: #b388ff; padding: 0 0 0 40px;")
        topbar.addWidget(app_title, alignment=Qt.AlignVCenter)
        # Kategorie-Name groß, mittig
        self.topbar_title = QLabel(CATEGORIES[2][1])
        self.topbar_title.setFont(QFont('Arial', 22, QFont.Bold))
        self.topbar_title.setStyleSheet("color: #e6e6e6; padding: 0 0 0 40px;")
        topbar.addWidget(self.topbar_title, alignment=Qt.AlignVCenter)
        topbar.addStretch()
        # FiveM-Version rechts oben anzeigen (optional)
        self.version_label = QLabel()
        self.version_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.version_label.setStyleSheet("color: #b388ff; margin-right: 20px;")
        if hasattr(self, 'fivem_version') and self.fivem_version:
            self.version_label.setText(f"FiveM v{self.fivem_version}")
        else:
            self.version_label.setText("")
        topbar.addWidget(self.version_label, alignment=Qt.AlignRight)
        # User-Avatar rechts
        avatar = QLabel()
        avatar.setPixmap(QPixmap(40, 40))
        avatar.setStyleSheet("background: #b388ff; border-radius: 20px; min-width:40px; min-height:40px; margin: 0 40px 0 0;")
        topbar.addWidget(avatar, alignment=Qt.AlignRight)
        topbar_widget = QWidget()
        topbar_widget.setLayout(topbar)
        topbar_widget.setStyleSheet("background: #18191c; min-height: 80px;")
        content_layout.addWidget(topbar_widget)
        # Dynamischer Content
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_player_page())
        self.stack.addWidget(self.create_esp_page())
        self.stack.addWidget(self.create_weapons_page())
        self.stack.addWidget(self.create_vehicle_page())
        self.stack.addWidget(self.create_misc_page())
        self.stack.addWidget(self.create_settings_page())
        content_layout.addWidget(self.stack)
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        # Haupt-Widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        # Version-Label ggf. updaten, falls Version erst nachträglich erkannt wurde
        if hasattr(self, 'fivem_version') and self.fivem_version:
            self.version_label.setText(f"FiveM v{self.fivem_version}")
        else:
            self.version_label.setText("")

    def switch_category(self, idx):
        self.topbar_title.setText(CATEGORIES[idx][1])
        self.stack.setCurrentIndex(idx)

    def start_fivem(self):
        try:
            proc = subprocess.Popen([FIVEM_PATH])
            # Warte kurz, prüfe ob Prozess läuft
            import time
            time.sleep(1)
            found = False
            for p in psutil.process_iter(['name']):
                if FIVEM_PROCESS_NAME.lower() in p.info['name'].lower():
                    found = True
                    break
            if found:
                QMessageBox.information(self, "Info", "FiveM wurde gestartet.")
            else:
                QMessageBox.warning(self, "Fehler", "FiveM-Prozess wurde nicht gefunden!")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"FiveM konnte nicht gestartet werden: {e}")

    def stop_fivem(self):
        try:
            found = False
            for proc in psutil.process_iter(['name']):
                if FIVEM_PROCESS_NAME.lower() in proc.info['name'].lower():
                    proc.terminate()
                    found = True
            if found:
                QMessageBox.information(self, "Info", "FiveM wurde beendet.")
            else:
                QMessageBox.information(self, "Info", "Kein FiveM-Prozess gefunden.")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"FiveM konnte nicht beendet werden: {e}")

    def run_script(self, script):
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
            if not os.path.exists(script_path):
                QMessageBox.warning(self, "Fehler", f"Skript nicht gefunden: {script_path}")
                return
            subprocess.Popen([sys.executable, script_path])
            QMessageBox.information(self, "Info", f"{script} wurde gestartet.")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Skript konnte nicht ausgeführt werden: {e}")

    # Hilfsfunktion: pymem-Handle holen
    def get_fivem_handle(self):
        try:
            import pymem
            for proc in psutil.process_iter(['name']):
                if FIVEM_PROCESS_NAME.lower() in proc.info['name'].lower():
                    return pymem.Pymem(proc.info['name'])
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"pymem-Fehler: {e}")
        return None

    def godmode_toggle(self, state):
        try:
            pm = self.get_fivem_handle()
            if not pm:
                return
            value = 1 if state else 0
            pm.write_int(GODMODE_OFFSET, value)
            print(f"Godmode {'AN' if state else 'AUS'} (Offset: {hex(GODMODE_OFFSET)})")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Godmode-Fehler: {e}")

    def heal_player(self):
        try:
            pm = self.get_fivem_handle()
            if not pm:
                return
            pm.write_int(HEALTH_OFFSET, 200)
            print("Heal ausgeführt")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Heal-Fehler: {e}")

    def teleport_player(self):
        try:
            pm = self.get_fivem_handle()
            if not pm:
                return
            pm.write_float(X_OFFSET, 100.0)
            pm.write_float(Y_OFFSET, 200.0)
            pm.write_float(Z_OFFSET, 30.0)
            print("Teleport ausgeführt")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Teleport-Fehler: {e}")

    def set_player_speed(self, value):
        try:
            pm = self.get_fivem_handle()
            if not pm:
                return
            speed = value / 10.0
            pm.write_float(SPEED_OFFSET, speed)
            print(f"Speed gesetzt: {speed:.1f}x")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Speed-Fehler: {e}")

    def spawn_vehicle(self, name):
        try:
            pm = self.get_fivem_handle()
            if not pm:
                return
            pm.write_string(VEHICLE_SPAWN_OFFSET, name)
            print(f"Fahrzeug gespawnt: {name}")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Vehicle-Spawn-Fehler: {e}")

    def repair_vehicle(self):
        try:
            pm = self.get_fivem_handle()
            if not pm:
                return
            pm.write_int(REPAIR_OFFSET, 1)
            print("Fahrzeug repariert")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Repair-Fehler: {e}")

    def flip_vehicle(self):
        try:
            pm = self.get_fivem_handle()
            if not pm:
                return
            pm.write_int(FLIP_OFFSET, 1)
            print("Fahrzeug geflippt")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Flip-Fehler: {e}")

    def set_vehicle_speed(self, value):
        try:
            pm = self.get_fivem_handle()
            if not pm:
                return
            speed = value / 10.0
            pm.write_float(VEHICLE_SPEED_OFFSET, speed)
            print(f"Vehicle Speed gesetzt: {speed:.1f}x")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Vehicle-Speed-Fehler: {e}")

    def spawner_give_weapon(self, weapon):
        try:
            pm = self.get_fivem_handle()
            if not pm:
                return
            pm.write_string(WEAPON_OFFSET, weapon)
            print(f"Waffe gegeben: {weapon}")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Weapon-Spawn-Fehler: {e}")

    def show_esp_overlay(self):
        # Beispiel: Einfaches Overlay-Fenster (transparent, always on top)
        import threading
        import tkinter as tk
        def overlay():
            root = tk.Tk()
            root.title('ESP Overlay')
            root.attributes('-topmost', True)
            root.attributes('-alpha', 0.4)
            root.geometry('800x600+100+100')
            root.overrideredirect(True)
            canvas = tk.Canvas(root, width=800, height=600, bg='black')
            canvas.pack()
            # Beispiel: Zeichne eine Box (hier statisch, später dynamisch)
            canvas.create_rectangle(200, 200, 400, 400, outline='purple', width=3)
            canvas.create_text(300, 190, text='Spieler', fill='white')
            root.mainloop()
        t = threading.Thread(target=overlay, daemon=True)
        t.start()
        print('ESP Overlay gestartet (Demo)')

    def esp_option_changed(self, option, state):
        try:
            print(f"ESP Option {option}: {state}")
            if option == 'Box' and state:
                self.show_esp_overlay()  # Overlay starten, wenn ESP aktiviert
            # TODO: ESP-Overlay-Logik implementieren
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"ESP-Fehler: {e}")

    def set_esp_color(self, color):
        try:
            print(f"ESP Farbe: {color}")
            # TODO: ESP-Overlay-Farbe setzen
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"ESP-Farb-Fehler: {e}")

    def create_misc_page(self):
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        main_layout = QHBoxLayout(content)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(32)
        misc_panel = QFrame()
        misc_panel.setStyleSheet("background: #19191c; border-radius: 18px; border: none; border-left: 4px solid #b388ff;")
        misc_layout = QVBoxLayout()
        misc_layout.setContentsMargins(28, 24, 28, 24)
        misc_layout.setSpacing(12)
        misc_title = QLabel("Misc")
        misc_title.setFont(QFont('Arial', 18, QFont.Bold))
        misc_title.setStyleSheet("color: #e6e6e6; border-bottom: 1px solid #444; margin-bottom: 12px;")
        misc_layout.addWidget(misc_title)
        fivem_start_btn = QPushButton("FiveM starten")
        fivem_start_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        fivem_start_btn.clicked.connect(self.start_fivem)
        misc_layout.addWidget(fivem_start_btn)
        fivem_stop_btn = QPushButton("FiveM beenden")
        fivem_stop_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        fivem_stop_btn.clicked.connect(self.stop_fivem)
        misc_layout.addWidget(fivem_stop_btn)
        trigger_btn = QPushButton("Trigger Finder öffnen")
        trigger_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        trigger_btn.clicked.connect(lambda: self.run_script('trigger_finder.py'))
        misc_layout.addWidget(trigger_btn)
        dumper_btn = QPushButton("Dumper starten")
        dumper_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        dumper_btn.clicked.connect(lambda: self.run_script('dumper.py'))
        misc_layout.addWidget(dumper_btn)
        executor_btn = QPushButton("Executor öffnen")
        executor_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        executor_btn.clicked.connect(lambda: self.run_script('executor.py'))
        misc_layout.addWidget(executor_btn)
        misc_panel.setLayout(misc_layout)
        main_layout.addWidget(misc_panel, 2)
        content.setLayout(main_layout)
        scroll.setWidget(content)
        page_layout = QVBoxLayout(page)
        page_layout.addWidget(scroll)
        return page

    def create_player_page(self):
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        main_layout = QHBoxLayout(content)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(32)
        player_panel = QFrame()
        player_panel.setStyleSheet("background: #19191c; border-radius: 18px; border: none; border-left: 4px solid #b388ff;")
        player_layout = QVBoxLayout()
        player_layout.setContentsMargins(28, 24, 28, 24)
        player_layout.setSpacing(12)
        player_title = QLabel("Player")
        player_title.setFont(QFont('Arial', 18, QFont.Bold))
        player_title.setStyleSheet("color: #e6e6e6; border-bottom: 1px solid #444; margin-bottom: 12px;")
        player_layout.addWidget(player_title)
        godmode_cb = QCheckBox("Godmode")
        godmode_cb.setStyleSheet("QCheckBox { font-size: 15px; color: #e6e6e6; } QCheckBox::indicator { width: 22px; height: 22px; border-radius: 11px; border: 2px solid #b388ff; background: #23232b; } QCheckBox::indicator:checked { background: #b388ff; border: 2px solid #b388ff; }")
        godmode_cb.stateChanged.connect(self.godmode_toggle)
        player_layout.addWidget(godmode_cb)
        heal_btn = QPushButton("Heilen")
        heal_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        heal_btn.clicked.connect(self.heal_player)
        player_layout.addWidget(heal_btn)
        teleport_btn = QPushButton("Teleport")
        teleport_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        teleport_btn.clicked.connect(self.teleport_player)
        player_layout.addWidget(teleport_btn)
        speed_label = QLabel("Speed: 1.0x")
        speed_label.setStyleSheet("color: #b388ff; min-width: 60px;")
        speed_slider = QSlider(Qt.Horizontal)
        speed_slider.setMinimum(10)
        speed_slider.setMaximum(50)
        speed_slider.setValue(10)
        speed_slider.setStyleSheet("QSlider::groove:horizontal { height: 8px; background: #23232b; border-radius: 4px; } QSlider::handle:horizontal { background: #b388ff; border: 2px solid #b388ff; width: 22px; margin: -8px 0; border-radius: 11px; }")
        speed_slider.valueChanged.connect(lambda v: [speed_label.setText(f'Speed: {v/10:.1f}x'), self.set_player_speed(v)])
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(speed_slider)
        speed_layout.addWidget(speed_label)
        player_layout.addLayout(speed_layout)
        player_panel.setLayout(player_layout)
        main_layout.addWidget(player_panel, 2)
        content.setLayout(main_layout)
        scroll.setWidget(content)
        page_layout = QVBoxLayout(page)
        page_layout.addWidget(scroll)
        return page

    def create_vehicle_page(self):
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        main_layout = QHBoxLayout(content)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(32)
        vehicle_panel = QFrame()
        vehicle_panel.setStyleSheet("background: #19191c; border-radius: 18px; border: none; border-left: 4px solid #b388ff;")
        vehicle_layout = QVBoxLayout()
        vehicle_layout.setContentsMargins(28, 24, 28, 24)
        vehicle_layout.setSpacing(12)
        vehicle_title = QLabel("Vehicle")
        vehicle_title.setFont(QFont('Arial', 18, QFont.Bold))
        vehicle_title.setStyleSheet("color: #e6e6e6; border-bottom: 1px solid #444; margin-bottom: 12px;")
        vehicle_layout.addWidget(vehicle_title)
        spawner_dropdown = QComboBox()
        spawner_dropdown.addItems(["Adder", "Kuruma", "T20", "Zentorno"])
        spawner_dropdown.setStyleSheet("QComboBox { background: #23232b; color: #e6e6e6; border: 1px solid #b388ff; border-radius: 8px; padding: 4px 12px; min-width: 180px; } QComboBox QAbstractItemView { background: #23232b; color: #e6e6e6; }")
        vehicle_layout.addWidget(spawner_dropdown)
        spawn_btn = QPushButton("Fahrzeug spawnen")
        spawn_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        spawn_btn.clicked.connect(lambda: self.spawn_vehicle(spawner_dropdown.currentText()))
        vehicle_layout.addWidget(spawn_btn)
        repair_btn = QPushButton("Reparieren")
        repair_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        repair_btn.clicked.connect(self.repair_vehicle)
        vehicle_layout.addWidget(repair_btn)
        flip_btn = QPushButton("Flip")
        flip_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        flip_btn.clicked.connect(self.flip_vehicle)
        vehicle_layout.addWidget(flip_btn)
        speed_label = QLabel("Speed: 1.0x")
        speed_label.setStyleSheet("color: #b388ff; min-width: 60px;")
        speed_slider = QSlider(Qt.Horizontal)
        speed_slider.setMinimum(10)
        speed_slider.setMaximum(50)
        speed_slider.setValue(10)
        speed_slider.setStyleSheet("QSlider::groove:horizontal { height: 8px; background: #23232b; border-radius: 4px; } QSlider::handle:horizontal { background: #b388ff; border: 2px solid #b388ff; width: 22px; margin: -8px 0; border-radius: 11px; }")
        speed_slider.valueChanged.connect(lambda v: [speed_label.setText(f'Speed: {v/10:.1f}x'), self.set_vehicle_speed(v)])
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(speed_slider)
        speed_layout.addWidget(speed_label)
        vehicle_layout.addLayout(speed_layout)
        vehicle_panel.setLayout(vehicle_layout)
        main_layout.addWidget(vehicle_panel, 2)
        content.setLayout(main_layout)
        scroll.setWidget(content)
        page_layout = QVBoxLayout(page)
        page_layout.addWidget(scroll)
        return page

    def create_weapons_page(self):
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        main_layout = QHBoxLayout(content)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(32)
        # AIM PANEL (links)
        aim_panel = QFrame()
        aim_panel.setStyleSheet("background: #19191c; border-radius: 18px; border: none; border-left: 4px solid #b388ff;")
        aim_layout = QVBoxLayout()
        aim_layout.setContentsMargins(28, 24, 28, 24)
        aim_layout.setSpacing(12)
        aim_title = QLabel("Aim")
        aim_title.setFont(QFont('Arial', 18, QFont.Bold))
        aim_title.setStyleSheet("color: #e6e6e6; border-bottom: 1px solid #444; margin-bottom: 12px;")
        aim_layout.addWidget(aim_title)
        # Checkboxen
        aimbot_cb = QCheckBox("Aimbot")
        fov_cb = QCheckBox("FOV")
        fov_filled_cb = QCheckBox("FOV Filled")
        for cb in [aimbot_cb, fov_cb, fov_filled_cb]:
            cb.setStyleSheet("QCheckBox { font-size: 15px; color: #e6e6e6; } QCheckBox::indicator { width: 22px; height: 22px; border-radius: 11px; border: 2px solid #b388ff; background: #23232b; } QCheckBox::indicator:checked { background: #b388ff; border: 2px solid #b388ff; }")
            cb.stateChanged.connect(lambda state, name=cb.text(): print(f"{name}: {state}"))  # TODO: Echte Aimbot/FOV-Logik
            aim_layout.addWidget(cb)  # <-- Checkboxen explizit zum Layout hinzufügen
        # FOV Size Slider
        fov_size_layout = QHBoxLayout()
        fov_size_slider = QSlider(Qt.Horizontal)
        fov_size_slider.setMinimum(0)
        fov_size_slider.setMaximum(400)
        fov_size_slider.setValue(229)
        fov_size_slider.setStyleSheet("QSlider::groove:horizontal { height: 8px; background: #23232b; border-radius: 4px; } QSlider::handle:horizontal { background: #b388ff; border: 2px solid #b388ff; width: 22px; margin: -8px 0; border-radius: 11px; }")
        fov_size_label = QLabel("229 px")
        fov_size_label.setStyleSheet("color: #b388ff; min-width: 60px;")
        fov_size_slider.valueChanged.connect(lambda v: [fov_size_label.setText(f"{v} px"), print(f"FOV Size: {v}")])
        fov_size_layout.addWidget(fov_size_slider)
        fov_size_layout.addWidget(fov_size_label)
        aim_layout.addLayout(fov_size_layout)
        # Silent Aim
        silent_label = QLabel("Silent Aim")
        silent_label.setFont(QFont('Arial', 13, QFont.Bold))
        silent_label.setStyleSheet("color: #888; margin-top: 10px;")
        aim_layout.addWidget(silent_label)
        magic_bullet_cb = QCheckBox("Magic Bullet")
        fov2_cb = QCheckBox("FOV 2")
        for cb in [magic_bullet_cb, fov2_cb]:
            cb.setStyleSheet("QCheckBox { font-size: 15px; color: #e6e6e6; } QCheckBox::indicator { width: 22px; height: 22px; border-radius: 11px; border: 2px solid #b388ff; background: #23232b; } QCheckBox::indicator:checked { background: #b388ff; border: 2px solid #b388ff; }")
            cb.stateChanged.connect(lambda state, name=cb.text(): print(f"{name}: {state}"))  # TODO: Echte Silent Aim-Logik
            aim_layout.addWidget(cb)  # <-- Checkboxen explizit zum Layout hinzufügen
        # FOV Size 2
        fov2_size_layout = QHBoxLayout()
        fov2_size_slider = QSlider(Qt.Horizontal)
        fov2_size_slider.setMinimum(0)
        fov2_size_slider.setMaximum(400)
        fov2_size_slider.setValue(200)
        fov2_size_slider.setStyleSheet("QSlider::groove:horizontal { height: 8px; background: #23232b; border-radius: 4px; } QSlider::handle:horizontal { background: #b388ff; border: 2px solid #b388ff; width: 22px; margin: -8px 0; border-radius: 11px; }")
        fov2_size_label = QLabel("200 px")
        fov2_size_label.setStyleSheet("color: #b388ff; min-width: 60px;")
        fov2_size_slider.valueChanged.connect(lambda v: [fov2_size_label.setText(f"{v} px"), print(f"FOV2 Size: {v}")])
        fov2_size_layout.addWidget(fov2_size_slider)
        fov2_size_layout.addWidget(fov2_size_label)
        aim_layout.addLayout(fov2_size_layout)
        # Hit Chance
        hit_label = QLabel("Hit Chance")
        hit_label.setStyleSheet("color: #e6e6e6; margin-top: 10px;")
        hit_layout = QHBoxLayout()
        hit_slider = QSlider(Qt.Horizontal)
        hit_slider.setMinimum(0)
        hit_slider.setMaximum(100)
        hit_slider.setValue(70)
        hit_slider.setStyleSheet("QSlider::groove:horizontal { height: 8px; background: #23232b; border-radius: 4px; } QSlider::handle:horizontal { background: #b388ff; border: 2px solid #b388ff; width: 22px; margin: -8px 0; border-radius: 11px; }")
        hit_value = QLabel("70 pct")
        hit_value.setStyleSheet("color: #b388ff; min-width: 60px;")
        hit_slider.valueChanged.connect(lambda v: [hit_value.setText(f"{v} pct"), print(f"Hit Chance: {v}")])
        hit_layout.addWidget(hit_slider)
        hit_layout.addWidget(hit_value)
        aim_layout.addWidget(hit_label)
        aim_layout.addLayout(hit_layout)
        # Crosshair
        crosshair_layout = QHBoxLayout()
        crosshair_label = QLabel("Crosshair")
        crosshair_label.setStyleSheet("color: #e6e6e6;")
        crosshair_cb = QCheckBox()
        crosshair_cb.setStyleSheet("QCheckBox::indicator { width: 22px; height: 22px; border-radius: 6px; border: 2px solid #b388ff; background: #23232b; } QCheckBox::indicator:checked { background: #b388ff; border: 2px solid #b388ff; }")
        crosshair_cb.stateChanged.connect(lambda state: print(f"Crosshair: {state}"))  # TODO: Crosshair-Overlay
        crosshair_layout.addWidget(crosshair_label)
        crosshair_layout.addWidget(crosshair_cb)
        crosshair_layout.addStretch()
        aim_layout.addLayout(crosshair_layout)
        aim_panel.setLayout(aim_layout)
        main_layout.addWidget(aim_panel, 2)
        # RIGHT PANEL (Sliders, Dropdown, Spawner)
        right_panel = QVBoxLayout()
        # Smooth Panel
        smooth_panel = QFrame()
        smooth_panel.setStyleSheet("background: #19191c; border-radius: 18px; border: none; border-left: 4px solid #b388ff;")
        smooth_layout = QVBoxLayout()
        smooth_layout.setContentsMargins(28, 24, 28, 24)
        smooth_layout.setSpacing(12)
        # Smooth Horizontal
        smooth_h_label = QLabel("Smooth Horizontal")
        smooth_h_label.setStyleSheet("color: #e6e6e6;")
        smooth_h_slider = QSlider(Qt.Horizontal)
        smooth_h_slider.setMinimum(0)
        smooth_h_slider.setMaximum(100)
        smooth_h_slider.setValue(23)
        smooth_h_slider.setStyleSheet("QSlider::groove:horizontal { height: 8px; background: #23232b; border-radius: 4px; } QSlider::handle:horizontal { background: #b388ff; border: 2px solid #b388ff; width: 22px; margin: -8px 0; border-radius: 11px; }")
        smooth_h_value = QLabel("22.87 pct")
        smooth_h_value.setStyleSheet("color: #b388ff; min-width: 60px;")
        smooth_h_slider.valueChanged.connect(lambda v: [smooth_h_value.setText(f"{v/100*100:.2f} pct"), print(f"Smooth Horizontal: {v}")])
        smooth_h_layout = QHBoxLayout()
        smooth_h_layout.addWidget(smooth_h_slider)
        smooth_h_layout.addWidget(smooth_h_value)
        # Smooth Vertical
        smooth_v_label = QLabel("Smooth Vertical")
        smooth_v_label.setStyleSheet("color: #e6e6e6;")
        smooth_v_slider = QSlider(Qt.Horizontal)
        smooth_v_slider.setMinimum(0)
        smooth_v_slider.setMaximum(100)
        smooth_v_slider.setValue(49)
        smooth_v_slider.setStyleSheet("QSlider::groove:horizontal { height: 8px; background: #23232b; border-radius: 4px; } QSlider::handle:horizontal { background: #b388ff; border: 2px solid #b388ff; width: 22px; margin: -8px 0; border-radius: 11px; }")
        smooth_v_value = QLabel("48.94 pct")
        smooth_v_value.setStyleSheet("color: #b388ff; min-width: 60px;")
        smooth_v_slider.valueChanged.connect(lambda v: [smooth_v_value.setText(f"{v/100*100:.2f} pct"), print(f"Smooth Vertical: {v}")])
        smooth_v_layout = QHBoxLayout()
        smooth_v_layout.addWidget(smooth_v_slider)
        smooth_v_layout.addWidget(smooth_v_value)
        # Aimbot Distance
        aimbot_dist_label = QLabel("Aimbot Distance")
        aimbot_dist_label.setStyleSheet("color: #e6e6e6;")
        aimbot_dist_slider = QSlider(Qt.Horizontal)
        aimbot_dist_slider.setMinimum(0)
        aimbot_dist_slider.setMaximum(1000)
        aimbot_dist_slider.setValue(692)
        aimbot_dist_slider.setStyleSheet("QSlider::groove:horizontal { height: 8px; background: #23232b; border-radius: 4px; } QSlider::handle:horizontal { background: #b388ff; border: 2px solid #b388ff; width: 22px; margin: -8px 0; border-radius: 11px; }")
        aimbot_dist_value = QLabel("692.35 m")
        aimbot_dist_value.setStyleSheet("color: #b388ff; min-width: 60px;")
        aimbot_dist_slider.valueChanged.connect(lambda v: [aimbot_dist_value.setText(f"{v/1000*1000:.2f} m"), print(f"Aimbot Distance: {v}")])
        aimbot_dist_layout = QHBoxLayout()
        aimbot_dist_layout.addWidget(aimbot_dist_slider)
        aimbot_dist_layout.addWidget(aimbot_dist_value)
        # Bone Selector
        bone_dropdown = QComboBox()
        bone_dropdown.addItems(["Head", "Neck", "Chest", "Pelvis"])
        bone_dropdown.setStyleSheet("QComboBox { background: #23232b; color: #e6e6e6; border: 1px solid #b388ff; border-radius: 8px; padding: 4px 12px; min-width: 120px; } QComboBox QAbstractItemView { background: #23232b; color: #e6e6e6; }")
        bone_dropdown.currentTextChanged.connect(lambda text: print(f"Bone: {text}"))
        # Add all to smooth_layout
        smooth_layout.addWidget(smooth_h_label)
        smooth_layout.addLayout(smooth_h_layout)
        smooth_layout.addWidget(smooth_v_label)
        smooth_layout.addLayout(smooth_v_layout)
        smooth_layout.addWidget(aimbot_dist_label)
        smooth_layout.addLayout(aimbot_dist_layout)
        smooth_layout.addWidget(bone_dropdown)
        smooth_panel.setLayout(smooth_layout)
        right_panel.addWidget(smooth_panel)
        # Spawner Panel
        spawner_panel = QFrame()
        spawner_panel.setStyleSheet("background: #19191c; border-radius: 18px; border: none; border-left: 4px solid #b388ff; margin-top: 24px;")
        spawner_layout = QVBoxLayout()
        spawner_layout.setContentsMargins(28, 24, 28, 24)
        spawner_layout.setSpacing(12)
        spawner_title = QLabel("Spawner")
        spawner_title.setFont(QFont('Arial', 16, QFont.Bold))
        spawner_title.setStyleSheet("color: #e6e6e6; border-bottom: 1px solid #444; margin-bottom: 12px;")
        spawner_layout.addWidget(spawner_title)
        weapon_dropdown = QComboBox()
        weapon_dropdown.addItems(["Micro SMG", "Pistol", "SMG", "Rifle", "Sniper"])
        weapon_dropdown.setStyleSheet("QComboBox { background: #23232b; color: #e6e6e6; border: 1px solid #b388ff; border-radius: 8px; padding: 4px 12px; min-width: 180px; } QComboBox QAbstractItemView { background: #23232b; color: #e6e6e6; }")
        spawner_layout.addWidget(weapon_dropdown)
        give_btn = QPushButton("Give Micro SMG")
        give_btn.setStyleSheet("QPushButton { background: #b388ff; color: #18191c; border-radius: 8px; font-weight: bold; min-height: 38px; font-size: 16px; } QPushButton:hover { background: #d1aaff; }")
        give_btn.clicked.connect(lambda: self.spawner_give_weapon(weapon_dropdown.currentText()))
        weapon_dropdown.currentTextChanged.connect(lambda text: give_btn.setText(f"Give {text}"))
        spawner_layout.addWidget(give_btn)
        spawner_panel.setLayout(spawner_layout)
        right_panel.addWidget(spawner_panel)
        main_layout.addLayout(right_panel, 2)
        content.setLayout(main_layout)
        scroll.setWidget(content)
        page_layout = QVBoxLayout(page)
        page_layout.addWidget(scroll)
        return page

    def create_esp_page(self):
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        main_layout = QHBoxLayout(content)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(32)
        esp_panel = QFrame()
        esp_panel.setStyleSheet("background: #19191c; border-radius: 18px; border: none; border-left: 4px solid #b388ff;")
        esp_layout = QVBoxLayout()
        esp_layout.setContentsMargins(28, 24, 28, 24)
        esp_layout.setSpacing(12)
        esp_title = QLabel("ESP")
        esp_title.setFont(QFont('Arial', 18, QFont.Bold))
        esp_title.setStyleSheet("color: #e6e6e6; border-bottom: 1px solid #444; margin-bottom: 12px;")
        esp_layout.addWidget(esp_title)
        box_cb = QCheckBox("Box")
        name_cb = QCheckBox("Name")
        health_cb = QCheckBox("Health")
        dist_cb = QCheckBox("Distance")
        for cb in [box_cb, name_cb, health_cb, dist_cb]:
            cb.setStyleSheet("QCheckBox { font-size: 15px; color: #e6e6e6; } QCheckBox::indicator { width: 22px; height: 22px; border-radius: 11px; border: 2px solid #b388ff; background: #23232b; } QCheckBox::indicator:checked { background: #b388ff; border: 2px solid #b388ff; }")
            cb.stateChanged.connect(lambda state, name=cb.text(): self.esp_option_changed(name, state))
            esp_layout.addWidget(cb)
        color_label = QLabel("Farbe:")
        color_label.setStyleSheet("color: #e6e6e6; margin-top: 8px;")
        color_dropdown = QComboBox()
        color_dropdown.addItems(["Lila", "Rot", "Grün", "Blau", "Gelb"])
        color_dropdown.setStyleSheet("QComboBox { background: #23232b; color: #e6e6e6; border: 1px solid #b388ff; border-radius: 8px; padding: 4px 12px; min-width: 120px; } QComboBox QAbstractItemView { background: #23232b; color: #e6e6e6; }")
        color_dropdown.currentTextChanged.connect(self.set_esp_color)
        esp_layout.addWidget(color_label)
        esp_layout.addWidget(color_dropdown)
        esp_panel.setLayout(esp_layout)
        main_layout.addWidget(esp_panel, 2)
        content.setLayout(main_layout)
        scroll.setWidget(content)
        page_layout = QVBoxLayout(page)
        page_layout.addWidget(scroll)
        return page

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Settings (Platzhalter)")
        label.setFont(QFont('Arial', 18, QFont.Bold))
        label.setStyleSheet("color: #e6e6e6; margin: 40px;")
        layout.addWidget(label)
        page.setLayout(layout)
        return page

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FiveMMenu()
    window.show()
    sys.exit(app.exec_())
