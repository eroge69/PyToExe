import sys
import json
import subprocess
import os
import platform
import re
import time
from datetime import datetime
from threading import Thread, Event
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit, 
                             QTabWidget, QCheckBox, QMessageBox, QSystemTrayIcon, 
                             QMenu, QAction, QStyle, QFileDialog, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer, QTranslator, QLocale, QSize
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont
import requests
from scapy.all import sniff, Dot11, Dot11Deauth
import smtplib
from email.mime.text import MIMEText
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type

class WiFiProtectorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_name = "WiFi Protector"
        self.version = "1.0.0"
        self.config_file = "config.json"
        self.running = False
        self.deauth_detected = False
        self.stop_sniffing = Event()
        
        self.load_config()
        self.setup_translations()
        self.init_ui()
        self.setup_tray_icon()
        self.check_dependencies()

    def load_config(self):
        default_config = {
            "language": "en",
            "theme": "dark",
            "email": "",
            "phone": "",
            "router_type": "auto",
            "router_ip": "192.168.1.1",
            "router_username": "admin",
            "router_password": "admin",
            "auto_change_password": False,
            "password_change_interval": 7,
            "notify_email": True,
            "notify_sms": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "sms_gateway": "",
            "known_devices": [],
            "protection_active": True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    for key in default_config:
                        if key not in self.config:
                            self.config[key] = default_config[key]
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_translations(self):
        self.translator = QTranslator()
        self.load_language(self.config["language"])
    
    def load_language(self, lang_code):
        lang_file = f"translations/{lang_code}.json"
        if os.path.exists(lang_file):
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except Exception as e:
                print(f"Error loading translations: {e}")
                self.translations = {}
        else:
            self.translations = {}
    
    def tr(self, text):
        return self.translations.get(text, text)
    
    def init_ui(self):
        self.setWindowTitle(f"{self.app_name} v{self.version}")
        self.setWindowIcon(QIcon("icons/app_icon.ico"))
        self.setMinimumSize(800, 600)
        
        self.create_menu_bar()
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        self.tabs = QTabWidget()
        
        self.status_tab = QWidget()
        self.setup_status_tab()
        self.tabs.addTab(self.status_tab, self.tr("Status"))
        
        self.settings_tab = QWidget()
        self.setup_settings_tab()
        self.tabs.addTab(self.settings_tab, self.tr("Settings"))
        
        self.alerts_tab = QWidget()
        self.setup_alerts_tab()
        self.tabs.addTab(self.alerts_tab, self.tr("Alerts"))
        
        self.devices_tab = QWidget()
        self.setup_devices_tab()
        self.tabs.addTab(self.devices_tab, self.tr("Known Devices"))
        
        main_layout.addWidget(self.tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.apply_theme(self.config["theme"])
        
        if not self.config.get("email") or not self.config.get("phone"):
            self.show_setup_wizard()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu(self.tr("File"))
        exit_action = QAction(QIcon.fromTheme("application-exit"), self.tr("Exit"), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu(self.tr("View"))
        
        lang_menu = view_menu.addMenu(self.tr("Language"))
        self.english_action = QAction("English", self)
        self.english_action.setCheckable(True)
        self.english_action.triggered.connect(lambda: self.change_language("en"))
        lang_menu.addAction(self.english_action)
        
        self.arabic_action = QAction("العربية", self)
        self.arabic_action.setCheckable(True)
        self.arabic_action.triggered.connect(lambda: self.change_language("ar"))
        lang_menu.addAction(self.arabic_action)
        
        self.update_language_actions()
        
        theme_menu = view_menu.addMenu(self.tr("Theme"))
        self.light_theme_action = QAction(self.tr("Light"), self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(self.light_theme_action)
        
        self.dark_theme_action = QAction(self.tr("Dark"), self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(self.dark_theme_action)
        
        self.update_theme_actions()
        
        help_menu = menubar.addMenu(self.tr("Help"))
        about_action = QAction(self.tr("About"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_tab(self):
        layout = QVBoxLayout()
        
        self.protection_status = QLabel(self.tr("Protection Status: Active" if self.config["protection_active"] else "Protection Status: Inactive"))
        self.protection_status.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.protection_status)
        
        self.toggle_protection_btn = QPushButton(self.tr("Deactivate Protection") if self.config["protection_active"] else self.tr("Activate Protection"))
        self.toggle_protection_btn.clicked.connect(self.toggle_protection)
        layout.addWidget(self.toggle_protection_btn)
        
        self.network_info = QTextEdit()
        self.network_info.setReadOnly(True)
        self.update_network_info()
        layout.addWidget(QLabel(self.tr("Network Information:")))
        layout.addWidget(self.network_info)
        
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        layout.addWidget(QLabel(self.tr("Event Log:")))
        layout.addWidget(self.event_log)
        
        refresh_btn = QPushButton(self.tr("Refresh Information"))
        refresh_btn.clicked.connect(self.update_network_info)
        layout.addWidget(refresh_btn)
        
        self.status_tab.setLayout(layout)
    
    def setup_settings_tab(self):
        layout = QVBoxLayout()
        
        router_group = QWidget()
        router_layout = QVBoxLayout()
        
        router_layout.addWidget(QLabel(self.tr("Router Settings:")))
        
        router_layout.addWidget(QLabel(self.tr("Router Type:")))
        self.router_type_combo = QComboBox()
        self.router_type_combo.addItems(["auto", "tp-link", "d-link", "huawei", "asus", "netgear", "zte", "other"])
        self.router_type_combo.setCurrentText(self.config["router_type"])
        router_layout.addWidget(self.router_type_combo)
        
        router_layout.addWidget(QLabel(self.tr("Router IP:")))
        self.router_ip_input = QLineEdit(self.config["router_ip"])
        router_layout.addWidget(self.router_ip_input)
        
        router_layout.addWidget(QLabel(self.tr("Username:")))
        self.router_username_input = QLineEdit(self.config["router_username"])
        router_layout.addWidget(self.router_username_input)
        
        router_layout.addWidget(QLabel(self.tr("Password:")))
        self.router_password_input = QLineEdit(self.config["router_password"])
        self.router_password_input.setEchoMode(QLineEdit.Password)
        router_layout.addWidget(self.router_password_input)
        
        self.auto_change_pass_check = QCheckBox(self.tr("Automatically change WiFi password periodically"))
        self.auto_change_pass_check.setChecked(self.config["auto_change_password"])
        router_layout.addWidget(self.auto_change_pass_check)
        
        router_layout.addWidget(QLabel(self.tr("Password change interval (days):")))
        self.pass_change_interval = QLineEdit(str(self.config["password_change_interval"]))
        router_layout.addWidget(self.pass_change_interval)
        
        router_group.setLayout(router_layout)
        layout.addWidget(router_group)
        
        test_router_btn = QPushButton(self.tr("Test Router Connection"))
        test_router_btn.clicked.connect(self.test_router_connection)
        layout.addWidget(test_router_btn)
        
        save_settings_btn = QPushButton(self.tr("Save Settings"))
        save_settings_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_settings_btn)
        
        self.settings_tab.setLayout(layout)
    
    def setup_alerts_tab(self):
        layout = QVBoxLayout()
        
        email_group = QWidget()
        email_layout = QVBoxLayout()
        
        email_layout.addWidget(QLabel(self.tr("Email Settings:")))
        
        email_layout.addWidget(QLabel(self.tr("Your Email:")))
        self.email_input = QLineEdit(self.config["email"])
        email_layout.addWidget(self.email_input)
        
        self.notify_email_check = QCheckBox(self.tr("Receive email alerts"))
        self.notify_email_check.setChecked(self.config["notify_email"])
        email_layout.addWidget(self.notify_email_check)
        
        email_layout.addWidget(QLabel(self.tr("SMTP Server:")))
        self.smtp_server_input = QLineEdit(self.config["smtp_server"])
        email_layout.addWidget(self.smtp_server_input)
        
        email_layout.addWidget(QLabel(self.tr("SMTP Port:")))
        self.smtp_port_input = QLineEdit(str(self.config["smtp_port"]))
        email_layout.addWidget(self.smtp_port_input)
        
        email_layout.addWidget(QLabel(self.tr("SMTP Username:")))
        self.smtp_username_input = QLineEdit(self.config["smtp_username"])
        email_layout.addWidget(self.smtp_username_input)
        
        email_layout.addWidget(QLabel(self.tr("SMTP Password:")))
        self.smtp_password_input = QLineEdit(self.config["smtp_password"])
        self.smtp_password_input.setEchoMode(QLineEdit.Password)
        email_layout.addWidget(self.smtp_password_input)
        
        email_group.setLayout(email_layout)
        layout.addWidget(email_group)
        
        sms_group = QWidget()
        sms_layout = QVBoxLayout()
        
        sms_layout.addWidget(QLabel(self.tr("SMS Settings:")))
        
        sms_layout.addWidget(QLabel(self.tr("Phone Number:")))
        self.phone_input = QLineEdit(self.config["phone"])
        sms_layout.addWidget(self.phone_input)
        
        self.notify_sms_check = QCheckBox(self.tr("Receive SMS alerts"))
        self.notify_sms_check.setChecked(self.config["notify_sms"])
        sms_layout.addWidget(self.notify_sms_check)
        
        sms_layout.addWidget(QLabel(self.tr("SMS Gateway:")))
        self.sms_gateway_input = QLineEdit(self.config["sms_gateway"])
        sms_layout.addWidget(self.sms_gateway_input)
        
        sms_group.setLayout(sms_layout)
        layout.addWidget(sms_group)
        
        test_alerts_btn = QPushButton(self.tr("Test Alerts"))
        test_alerts_btn.clicked.connect(self.test_alerts)
        layout.addWidget(test_alerts_btn)
        
        save_alerts_btn = QPushButton(self.tr("Save Alert Settings"))
        save_alerts_btn.clicked.connect(self.save_alert_settings)
        layout.addWidget(save_alerts_btn)
        
        self.alerts_tab.setLayout(layout)
    
    def setup_devices_tab(self):
        layout = QVBoxLayout()
        
        self.known_devices_list = QTextEdit()
        self.known_devices_list.setReadOnly(True)
        self.update_known_devices_list()
        layout.addWidget(QLabel(self.tr("Known Devices:")))
        layout.addWidget(self.known_devices_list)
        
        add_device_group = QWidget()
        add_device_layout = QHBoxLayout()
        
        self.new_device_input = QLineEdit()
        self.new_device_input.setPlaceholderText(self.tr("Enter MAC address (00:11:22:33:44:55)"))
        add_device_layout.addWidget(self.new_device_input)
        
        add_device_btn = QPushButton(self.tr("Add Device"))
        add_device_btn.clicked.connect(self.add_known_device)
        add_device_layout.addWidget(add_device_btn)
        
        add_device_group.setLayout(add_device_layout)
        layout.addWidget(add_device_group)
        
        refresh_devices_btn = QPushButton(self.tr("Refresh Devices List"))
        refresh_devices_btn.clicked.connect(self.update_known_devices_list)
        layout.addWidget(refresh_devices_btn)
        
        self.devices_tab.setLayout(layout)
    
    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icons/app_icon.ico"))
        
        tray_menu = QMenu()
        
        show_action = QAction(self.tr("Show"), self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction(self.tr("Hide"), self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        toggle_protection_action = QAction(
            self.tr("Deactivate Protection") if self.config["protection_active"] else self.tr("Activate Protection"), 
            self
        )
        toggle_protection_action.triggered.connect(self.toggle_protection)
        tray_menu.addAction(toggle_protection_action)
        
        exit_action = QAction(self.tr("Exit"), self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
    
    def apply_theme(self, theme):
        if theme == "dark":
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            QApplication.setPalette(palette)
        else:
            QApplication.setPalette(QApplication.style().standardPalette())
        
        self.config["theme"] = theme
        self.save_config()
    
    def update_language_actions(self):
        self.english_action.setChecked(self.config["language"] == "en")
        self.arabic_action.setChecked(self.config["language"] == "ar")
    
    def update_theme_actions(self):
        self.light_theme_action.setChecked(self.config["theme"] == "light")
        self.dark_theme_action.setChecked(self.config["theme"] == "dark")
    
    def change_language(self, lang_code):
        if lang_code != self.config["language"]:
            self.config["language"] = lang_code
            self.save_config()
            self.load_language(lang_code)
            self.init_ui()
            self.update_language_actions()
    
    def change_theme(self, theme):
        if theme != self.config["theme"]:
            self.apply_theme(theme)
            self.update_theme_actions()
    
    def toggle_protection(self):
        self.config["protection_active"] = not self.config["protection_active"]
        self.save_config()
        
        if self.config["protection_active"]:
            self.start_protection()
            self.protection_status.setText(self.tr("Protection Status: Active"))
            self.toggle_protection_btn.setText(self.tr("Deactivate Protection"))
            
            for action in self.tray_icon.contextMenu().actions():
                if action.text() in [self.tr("Activate Protection"), self.tr("Deactivate Protection")]:
                    action.setText(self.tr("Deactivate Protection"))
        else:
            self.stop_protection()
            self.protection_status.setText(self.tr("Protection Status: Inactive"))
            self.toggle_protection_btn.setText(self.tr("Activate Protection"))
            
            for action in self.tray_icon.contextMenu().actions():
                if action.text() in [self.tr("Activate Protection"), self.tr("Deactivate Protection")]:
                    action.setText(self.tr("Activate Protection"))
        
        self.log_event(self.tr("Protection {}").format(
            self.tr("activated") if self.config["protection_active"] else self.tr("deactivated")
        ))
    
    def start_protection(self):
        if not self.running:
            self.running = True
            self.stop_sniffing.clear()
            
            self.monitor_thread = Thread(target=self.monitor_deauth_attacks)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            if self.config["auto_change_password"]:
                self.start_auto_password_changer()
    
    def stop_protection(self):
        if self.running:
            self.running = False
            self.stop_sniffing.set()
            
            if hasattr(self, "password_timer"):
                self.password_timer.stop()
    
    def monitor_deauth_attacks(self):
        while not self.stop_sniffing.is_set():
            try:
                sniff(prn=self.detect_deauth, stop_filter=lambda x: self.stop_sniffing.is_set(), timeout=10)
            except Exception as e:
                self.log_event(self.tr("Error monitoring network: {}").format(str(e)))
                time.sleep(5)
    
    def detect_deauth(self, pkt):
        if pkt.haslayer(Dot11Deauth):
            if not self.deauth_detected:
                self.deauth_detected = True
                attacker = pkt.addr2
                victim = pkt.addr1
                
                msg = self.tr("Deauth attack detected! Attacker: {}, Victim: {}").format(attacker, victim)
                self.log_event(msg)
                self.send_alert(msg)
                self.respond_to_attack(attacker)
                QTimer.singleShot(60000, lambda: setattr(self, 'deauth_detected', False))
    
    def respond_to_attack(self, attacker_mac):
        try:
            if self.block_mac_on_router(attacker_mac):
                self.log_event(self.tr("Blocked attacker MAC {} on router").format(attacker_mac))
            
            self.tray_icon.showMessage(
                self.tr("Security Alert"),
                self.tr("A deauthentication attack was detected from {}").format(attacker_mac),
                QSystemTrayIcon.Critical,
                10000
            )
            
            if self.change_wifi_channel():
                self.log_event(self.tr("Changed WiFi channel to avoid attack"))
            
        except Exception as e:
            self.log_event(self.tr("Error responding to attack: {}").format(str(e)))
    
    def block_mac_on_router(self, mac_address):
        router_type = self.config["router_type"]
        
        try:
            if router_type == "tp-link":
                url = f"http://{self.config['router_ip']}/userRpm/MacFilterRpm.htm"
                params = {
                    "Add": "Add",
                    "mac": mac_address,
                    "desc": "Blocked by WiFi Protector",
                    "Save": "Save"
                }
                auth = (self.config["router_username"], self.config["router_password"])
                response = requests.get(url, params=params, auth=auth, timeout=10)
                return response.status_code == 200
                
            elif router_type == "d-link":
                url = f"http://{self.config['router_ip']}/apply.cgi"
                data = {
                    "action": "add",
                    "mac": mac_address,
                    "comment": "Blocked by WiFi Protector"
                }
                auth = (self.config["router_username"], self.config["router_password"])
                response = requests.post(url, data=data, auth=auth, timeout=10)
                return response.status_code == 200
                
            else:
                self.log_event(self.tr("MAC blocking not supported for this router type"))
                return False
                
        except Exception as e:
            self.log_event(self.tr("Error blocking MAC address: {}").format(str(e)))
            return False
    
    def change_wifi_channel(self):
        router_type = self.config["router_type"]
        
        try:
            if router_type == "tp-link":
                import random
                new_channel = random.randint(1, 11)
                
                url = f"http://{self.config['router_ip']}/userRpm/WlanNetworkRpm.htm"
                params = {
                    "channel": new_channel,
                    "Save": "Save"
                }
                auth = (self.config["router_username"], self.config["router_password"])
                response = requests.get(url, params=params, auth=auth, timeout=10)
                return response.status_code == 200
                
            elif router_type == "d-link":
                import random
                new_channel = random.randint(1, 11)
                
                url = f"http://{self.config['router_ip']}/apply.cgi"
                data = {
                    "WirelessChannel": new_channel,
                    "save": "Apply"
                }
                auth = (self.config["router_username"], self.config["router_password"])
                response = requests.post(url, data=data, auth=auth, timeout=10)
                return response.status_code == 200
                
            else:
                self.log_event(self.tr("Channel changing not supported for this router type"))
                return False
                
        except Exception as e:
            self.log_event(self.tr("Error changing WiFi channel: {}").format(str(e)))
            return False
    
    def start_auto_password_changer(self):
        interval_days = int(self.config["password_change_interval"])
        interval_ms = interval_days * 24 * 60 * 60 * 1000
        
        self.password_timer = QTimer()
        self.password_timer.timeout.connect(self.change_wifi_password)
        self.password_timer.start(interval_ms)
        self.change_wifi_password()
    
    def change_wifi_password(self):
        try:
            new_password = self.generate_strong_password()
            router_type = self.config["router_type"]
            
            success = False
            if router_type == "auto":
                detected_type = self.detect_router_type()
                if detected_type:
                    success = self.change_password_for_router(detected_type, new_password)
                else:
                    self.log_event(self.tr("Could not automatically detect router type"))
            else:
                success = self.change_password_for_router(router_type, new_password)
            
            if success:
                msg = self.tr("WiFi password changed successfully. New password: {}").format(new_password)
                self.log_event(msg)
                self.send_alert(msg)
            else:
                self.log_event(self.tr("Failed to change WiFi password"))
                
        except Exception as e:
            self.log_event(self.tr("Error changing WiFi password: {}").format(str(e)))
    
    def detect_router_type(self):
        try:
            router_ip = self.config["router_ip"]
            response = requests.get(f"http://{router_ip}", timeout=5)
            
            if "TP-Link" in response.text:
                return "tp-link"
            elif "D-Link" in response.text:
                return "d-link"
            elif "Huawei" in response.text:
                return "huawei"
            elif "Asus" in response.text:
                return "asus"
            elif "Netgear" in response.text:
                return "netgear"
            elif "ZTE" in response.text:
                return "zte"
            else:
                return None
                
        except:
            return None
    
    def change_password_for_router(self, router_type, new_password):
        try:
            if router_type == "tp-link":
                url = f"http://{self.config['router_ip']}/userRpm/WlanSecurityRpm.htm"
                params = {
                    "secType": "3",
                    "pskSecret": new_password,
                    "Save": "Save"
                }
                auth = (self.config["router_username"], self.config["router_password"])
                response = requests.get(url, params=params, auth=auth, timeout=10)
                return response.status_code == 200
                
            elif router_type == "d-link":
                url = f"http://{self.config['router_ip']}/apply.cgi"
                data = {
                    "WEPEncryption": "WPA2",
                    "PreSharedKey": new_password,
                    "save": "Apply"
                }
                auth = (self.config["router_username"], self.config["router_password"])
                response = requests.post(url, data=data, auth=auth, timeout=10)
                return response.status_code == 200
                
            else:
                self.log_event(self.tr("Password changing not supported for this router type"))
                return False
                
        except Exception as e:
            self.log_event(self.tr("Error changing password: {}").format(str(e)))
            return False
    
    def generate_strong_password(self, length=12):
        import random
        import string
        
        chars = string.ascii_letters + string.digits + "!@#$%^&*()"
        return ''.join(random.choice(chars) for _ in range(length))
    
    def send_alert(self, message):
        if self.config["notify_email"] and self.config["email"]:
            self.send_email_alert(message)
        
        if self.config["notify_sms"] and self.config["phone"] and self.config["sms_gateway"]:
            self.send_sms_alert(message)
    
    def send_email_alert(self, message):
        try:
            msg = MIMEText(message)
            msg['Subject'] = self.tr("WiFi Protector Alert")
            msg['From'] = self.config["smtp_username"]
            msg['To'] = self.config["email"]
            
            with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"]) as server:
                server.starttls()
                server.login(self.config["smtp_username"], self.config["smtp_password"])
                server.send_message(msg)
            
            self.log_event(self.tr("Email alert sent successfully"))
            return True
        except Exception as e:
            self.log_event(self.tr("Failed to send email alert: {}").format(str(e)))
            return False
    
    def send_sms_alert(self, message):
        try:
            phone = self.config["phone"]
            gateway = self.config["sms_gateway"]
            phone = ''.join(filter(str.isdigit, phone))
            
            if "@" in gateway:
                msg = MIMEText(message)
                msg['Subject'] = self.tr("WiFi Protector Alert")
                msg['From'] = self.config["smtp_username"]
                msg['To'] = gateway.replace("PHONE", phone)
                
                with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"]) as server:
                    server.starttls()
                    server.login(self.config["smtp_username"], self.config["smtp_password"])
                    server.send_message(msg)
            
            self.log_event(self.tr("SMS alert sent successfully"))
            return True
        except Exception as e:
            self.log_event(self.tr("Failed to send SMS alert: {}").format(str(e)))
            return False
    
    def update_network_info(self):
        try:
            info = []
            info.append(self.tr("=== System Information ==="))
            info.append(f"{self.tr('Operating System')}: {platform.system()} {platform.release()}")
            info.append(f"{self.tr('Python Version')}: {platform.python_version()}")
            
            if platform.system() == "Windows":
                try:
                    ipconfig = subprocess.check_output("ipconfig /all", shell=True).decode('utf-8', errors='ignore')
                    wifi_info = re.search(r"Wireless LAN adapter WiFi.*?SSID.*?:(.*?)\n.*?Physical Address.*?:(.*?)\n", ipconfig, re.DOTALL)
                    
                    if wifi_info:
                        info.append("\n" + self.tr("=== WiFi Information ==="))
                        info.append(f"{self.tr('SSID')}: {wifi_info.group(1).strip()}")
                        info.append(f"{self.tr('MAC Address')}: {wifi_info.group(2).strip()}")
                except:
                    pass
            elif platform.system() == "Linux":
                try:
                    iwconfig = subprocess.check_output("iwconfig", shell=True).decode('utf-8', errors='ignore')
                    wifi_info = re.search(r"wlan0.*?ESSID:\"(.*?)\".*?Access Point: (.*?) ", iwconfig)
                    
                    if wifi_info:
                        info.append("\n" + self.tr("=== WiFi Information ==="))
                        info.append(f"{self.tr('SSID')}: {wifi_info.group(1)}")
                        info.append(f"{self.tr('MAC Address')}: {wifi_info.group(2)}")
                except:
                    pass
            
            info.append("\n" + self.tr("=== Router Information ==="))
            info.append(f"{self.tr('Router IP')}: {self.config['router_ip']}")
            info.append(f"{self.tr('Router Type')}: {self.config['router_type']}")
            
            self.network_info.setText("\n".join(info))
            
        except Exception as e:
            self.network_info.setText(self.tr("Error getting network information: {}").format(str(e)))
    
    def update_known_devices_list(self):
        try:
            devices = self.config["known_devices"]
            if devices:
                self.known_devices_list.setText("\n".join(devices))
            else:
                self.known_devices_list.setText(self.tr("No known devices yet"))
        except Exception as e:
            self.known_devices_list.setText(self.tr("Error loading devices: {}").format(str(e)))
    
    def add_known_device(self):
        mac = self.new_device_input.text().strip()
        if not mac:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Please enter a MAC address"))
            return
        
        # التحقق من صيغة عنوان MAC
        if not re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", mac):
            QMessageBox.warning(self, self.tr("Error"), self.tr("Invalid MAC address format. Use 00:11:22:33:44:55"))
            return
        
        if mac in self.config["known_devices"]:
            QMessageBox.information(self, self.tr("Info"), self.tr("This device is already in the list"))
            return
        
        self.config["known_devices"].append(mac)
        self.save_config()
        self.update_known_devices_list()
        self.new_device_input.clear()
        self.log_event(self.tr("Added new device: {}").format(mac))
    
    def save_settings(self):
        self.config["router_type"] = self.router_type_combo.currentText()
        self.config["router_ip"] = self.router_ip_input.text()
        self.config["router_username"] = self.router_username_input.text()
        self.config["router_password"] = self.router_password_input.text()
        self.config["auto_change_password"] = self.auto_change_pass_check.isChecked()
        
        try:
            interval = int(self.pass_change_interval.text())
            if interval < 1:
                raise ValueError
            self.config["password_change_interval"] = interval
        except ValueError:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Please enter a valid number of days (1 or more)"))
            return
        
        self.save_config()
        QMessageBox.information(self, self.tr("Success"), self.tr("Settings saved successfully"))
        self.log_event(self.tr("Router settings updated"))
    
    def save_alert_settings(self):
        email = self.email_input.text().strip()
        if email and "@" not in email:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Please enter a valid email address"))
            return
        
        phone = self.phone_input.text().strip()
        if phone:
            try:
                parsed = phonenumbers.parse(phone, None)
                if not phonenumbers.is_valid_number(parsed):
                    raise ValueError
            except:
                QMessageBox.warning(self, self.tr("Error"), self.tr("Please enter a valid phone number"))
                return
        
        self.config["email"] = email
        self.config["phone"] = phone
        self.config["notify_email"] = self.notify_email_check.isChecked()
        self.config["notify_sms"] = self.notify_sms_check.isChecked()
        self.config["smtp_server"] = self.smtp_server_input.text()
        
        try:
            port = int(self.smtp_port_input.text())
            if port < 1 or port > 65535:
                raise ValueError
            self.config["smtp_port"] = port
        except ValueError:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Please enter a valid SMTP port (1-65535)"))
            return
        
        self.config["smtp_username"] = self.smtp_username_input.text()
        self.config["smtp_password"] = self.smtp_password_input.text()
        self.config["sms_gateway"] = self.sms_gateway_input.text()
        
        self.save_config()
        QMessageBox.information(self, self.tr("Success"), self.tr("Alert settings saved successfully"))
        self.log_event(self.tr("Alert settings updated"))
    
    def test_router_connection(self):
        try:
            router_ip = self.config["router_ip"]
            response = requests.get(f"http://{router_ip}", timeout=5)
            
            if response.status_code == 200:
                QMessageBox.information(self, self.tr("Success"), self.tr("Router connection successful"))
                self.log_event(self.tr("Router connection test successful"))
            else:
                QMessageBox.warning(self, self.tr("Error"), self.tr("Could not connect to router (HTTP {})").format(response.status_code))
                self.log_event(self.tr("Router connection test failed (HTTP {})").format(response.status_code))
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Router connection failed: {}").format(str(e)))
            self.log_event(self.tr("Router connection test failed: {}").format(str(e)))
    
    def test_alerts(self):
        test_msg = self.tr("This is a test alert from WiFi Protector")
        
        if self.config["notify_email"] and self.config["email"]:
            if self.send_email_alert(test_msg):
                QMessageBox.information(self, self.tr("Success"), self.tr("Test email sent successfully"))
            else:
                QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to send test email"))
        
        if self.config["notify_sms"] and self.config["phone"] and self.config["sms_gateway"]:
            if self.send_sms_alert(test_msg):
                QMessageBox.information(self, self.tr("Success"), self.tr("Test SMS sent successfully"))
            else:
                QMessageBox.warning(self, self.tr("Error"), self.tr("Failed to send test SMS"))
    
    def log_event(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.event_log.append(f"[{timestamp}] {message}")
    
    def show_setup_wizard(self):
        wizard = QWidget()
        wizard.setWindowTitle(self.tr("Initial Setup"))
        wizard.setWindowIcon(QIcon("icons/app_icon.ico"))
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(self.tr("Welcome to WiFi Protector!")))
        layout.addWidget(QLabel(self.tr("Please configure basic settings to get started:")))
        
        email_label = QLabel(self.tr("Your Email:"))
        email_input = QLineEdit(self.config["email"])
        layout.addWidget(email_label)
        layout.addWidget(email_input)
        
        phone_label = QLabel(self.tr("Phone Number:"))
        phone_input = QLineEdit(self.config["phone"])
        layout.addWidget(phone_label)
        layout.addWidget(phone_input)
        
        save_btn = QPushButton(self.tr("Save & Continue"))
        save_btn.clicked.connect(lambda: self.save_setup_info(email_input.text(), phone_input.text(), wizard))
        layout.addWidget(save_btn)
        
        wizard.setLayout(layout)
        wizard.show()
    
    def save_setup_info(self, email, phone, wizard):
        if email and "@" not in email:
            QMessageBox.warning(wizard, self.tr("Error"), self.tr("Please enter a valid email address"))
            return
        
        if phone:
            try:
                parsed = phonenumbers.parse(phone, None)
                if not phonenumbers.is_valid_number(parsed):
                    raise ValueError
            except:
                QMessageBox.warning(wizard, self.tr("Error"), self.tr("Please enter a valid phone number"))
                return
        
        self.config["email"] = email
        self.config["phone"] = phone
        self.save_config()
        wizard.close()
        self.log_event(self.tr("Initial setup completed"))
    
    def show_about(self):
        about_text = f"""
        <h1>{self.app_name} v{self.version}</h1>
        <p>{self.tr("A comprehensive WiFi network protection tool")}</p>
        <p>{self.tr("Features:")}</p>
        <ul>
            <li>{self.tr("Deauthentication attack detection")}</li>
            <li>{self.tr("Automatic WiFi password changing")}</li>
            <li>{self.tr("Email and SMS alerts")}</li>
            <li>{self.tr("Multi-language support")}</li>
            <li>{self.tr("Light/Dark theme")}</li>
        </ul>
        <p>{self.tr("Developed with Python and PyQt5")}</p>
        """
        
        QMessageBox.about(self, self.tr("About"), about_text)
    
    def check_dependencies(self):
        missing = []
        
        try:
            import PyQt5
        except ImportError:
            missing.append("PyQt5")
        
        try:
            import scapy
        except ImportError:
            missing.append("scapy")
        
        try:
            import requests
        except ImportError:
            missing.append("requests")
        
        try:
            import phonenumbers
        except ImportError:
            missing.append("phonenumbers")
        
        if missing:
            msg = self.tr("The following dependencies are missing:\n\n") + "\n".join(missing)
            msg += "\n\n" + self.tr("Please install them using:\npip install " + " ".join(missing))
            QMessageBox.critical(self, self.tr("Missing Dependencies"), msg)
    
    def closeEvent(self, event):
        if self.running:
            reply = QMessageBox.question(
                self,
                self.tr("Confirm Exit"),
                self.tr("Protection is still active. Are you sure you want to exit?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.stop_protection()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # إنشاء مجلدات التطبيق إذا لم تكن موجودة
    if not os.path.exists("translations"):
        os.makedirs("translations")
    
    if not os.path.exists("icons"):
        os.makedirs("icons")
    
    # إنشاء ملفات الترجمة إذا لم تكن موجودة
    if not os.path.exists("translations/en.json"):
        with open("translations/en.json", "w", encoding='utf-8') as f:
            json.dump({}, f)
    
    if not os.path.exists("translations/ar.json"):
        with open("translations/ar.json", "w", encoding='utf-8') as f:
            json.dump({}, f)
    
    window = WiFiProtectorApp()
    window.show()
    sys.exit(app.exec_())