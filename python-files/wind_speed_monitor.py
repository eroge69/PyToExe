import sys
import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QMessageBox
)
from PyQt5.QtCore import QTimer

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import numpy as np

# Beaufort scale (in mph)
BEAUFORT_SCALE = [
    (0, 1, "Calm"),
    (1, 3, "Light Air"),
    (4, 7, "Light Breeze"),
    (8, 12, "Gentle Breeze"),
    (13, 18, "Moderate Breeze"),
    (19, 24, "Fresh Breeze"),
    (25, 31, "Strong Breeze"),
    (32, 38, "Near Gale"),
    (39, 46, "Gale"),
    (47, 54, "Severe Gale"),
    (55, 63, "Storm"),
    (64, 72, "Violent Storm"),
    (73, 200, "Hurricane"),
]

class SerialReader(threading.Thread):
    def __init__(self, port, baudrate=115200):
        super().__init__()
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.running = True
        self.latest_wind_speed = None

    def run(self):
        while self.running:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    try:
                        # Expect line like: "Wind Speed: 8.04 mph"
                        # Extract number from line
                        parts = line.split()
                        for p in parts:
                            try:
                                val = float(p)
                                self.latest_wind_speed = val
                                break
                            except:
                                continue
                    except:
                        pass
            except Exception as e:
                print("Serial read error:", e)

    def stop(self):
        self.running = False
        self.ser.close()

class WindSpeedApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anemometer Wind Speed Monitor")

        self.layout = QVBoxLayout()

        self.port_label = QLabel("Select Serial Port:")
        self.layout.addWidget(self.port_label)

        self.port_combo = QComboBox()
        self.layout.addWidget(self.port_combo)

        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.layout.addWidget(self.refresh_button)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_serial)
        self.layout.addWidget(self.connect_button)

        self.status_label = QLabel("Status: Disconnected")
        self.layout.addWidget(self.status_label)

        self.current_speed_label = QLabel("Current Wind Speed: -- mph")
        self.current_speed_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.layout.addWidget(self.current_speed_label)

        # Matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Wind Speed (mph)")
        self.ax.grid(True)

        self.line, = self.ax.plot([], [], label="Wind Speed (mph)")
        self.ax.legend()

        self.times = []
        self.speeds = []

        self.serial_thread = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)

        self.setLayout(self.layout)

        self.refresh_ports()

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def connect_serial(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread = None
            self.connect_button.setText("Connect")
            self.status_label.setText("Status: Disconnected")
            self.timer.stop()
            return

        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "Warning", "No serial port selected")
            return
        try:
            self.serial_thread = SerialReader(port)
            self.serial_thread.start()
            self.connect_button.setText("Disconnect")
            self.status_label.setText(f"Status: Connected to {port}")
            self.times = []
            self.speeds = []
            self.timer.start(500)  # update plot every 500 ms
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open serial port:\n{e}")

    def update_plot(self):
        if self.serial_thread and self.serial_thread.latest_wind_speed is not None:
            now = datetime.now()
            self.times.append(now)
            self.speeds.append(self.serial_thread.latest_wind_speed)

            # Keep last 5 minutes of data (adjust as needed)
            cutoff = now.timestamp() - 300
            while self.times and self.times[0].timestamp() < cutoff:
                self.times.pop(0)
                self.speeds.pop(0)

            self.line.set_data(self.times, self.speeds)
            self.ax.relim()
            self.ax.autoscale_view()

            # Format X axis as time
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

            # Draw Beaufort scale as horizontal colored bands
            self.ax.collections.clear()  # remove old bands

            colors = [
                "#e0f7fa", "#b2ebf2", "#80deea", "#4dd0e1",
                "#26c6da", "#00bcd4", "#00acc1", "#0097a7",
                "#00838f", "#006064", "#004d40", "#00332c"
            ]
            for i, (low, high, label) in enumerate(BEAUFORT_SCALE):
                self.ax.axhspan(low, high, color=colors[i % len(colors)], alpha=0.15)
                self.ax.text(self.times[0], (low + high) / 2, label, fontsize=8, va='center')

            self.current_speed_label.setText(f"Current Wind Speed: {self.serial_thread.latest_wind_speed:.2f} mph")

            self.canvas.draw()

    def closeEvent(self, event):
        if self.serial_thread:
            self.serial_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WindSpeedApp()
    window.show()
    sys.exit(app.exec_())
