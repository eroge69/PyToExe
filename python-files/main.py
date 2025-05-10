import tkinter as tk
from tkinter import ttk
import ctypes, platform, time, threading, socket, uuid, subprocess, re
from datetime import datetime
import psutil
import json
import os
import logging
import shutil
import random
import webbrowser
from time import sleep
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup for logging
class DatabaseLogger:
    def __init__(self, db_name="system_performance.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS performance (
                                timestamp TEXT,
                                cpu_usage REAL,
                                ram_usage REAL,
                                disk_usage REAL,
                                ip TEXT,
                                mac TEXT)''')
        self.conn.commit()

    def insert_data(self, cpu_usage, ram_usage, disk_usage, ip, mac):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''INSERT INTO performance (timestamp, cpu_usage, ram_usage, disk_usage, ip, mac)
                               VALUES (?, ?, ?, ?, ?, ?)''', 
                            (timestamp, cpu_usage, ram_usage, disk_usage, ip, mac))
        self.conn.commit()

    def close(self):
        self.conn.close()

class SystemInfo:
    @staticmethod
    def uptime():
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        delta = datetime.now() - boot_time
        uptime_str = f"{delta.days}d {delta.seconds//3600}h {(delta.seconds%3600)//60}m"
        logging.info(f"Uptime: {uptime_str}")
        return uptime_str

    @staticmethod
    def cpu():
        cpu_usage = psutil.cpu_percent(interval=0.5)
        logging.debug(f"CPU Usage: {cpu_usage}%")
        return cpu_usage

    @staticmethod
    def ram():
        ram_usage = psutil.virtual_memory().percent
        logging.debug(f"RAM Usage: {ram_usage}%")
        return ram_usage

    @staticmethod
    def disk_usage():
        disk = psutil.disk_usage('/')
        disk_info = f"Total: {disk.total // (1024 ** 3)} GB, Used: {disk.used // (1024 ** 3)} GB, Free: {disk.free // (1024 ** 3)} GB"
        logging.info(f"Disk Usage: {disk_info}")
        return disk_info

    @staticmethod
    def user():
        try:
            user_name = platform.node()
            os_info = platform.system() + " " + platform.release()
            logging.debug(f"User: {user_name}, OS Info: {os_info}")
            return user_name, os_info
        except Exception as e:
            logging.error(f"Error fetching user info: {e}")
            return "Unknown", "Unknown"

    @staticmethod
    def ip():
        try:
            ip_address = socket.gethostbyname(socket.gethostname())
            logging.debug(f"IP Address: {ip_address}")
            return ip_address
        except:
            logging.warning("IP address not found.")
            return "No IP"

    @staticmethod
    def mac():
        try:
            mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
            logging.debug(f"MAC Address: {mac_address}")
            return mac_address
        except:
            logging.warning("MAC address not found.")
            return "No MAC"

    @staticmethod
    def wifi():
        try:
            output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode("utf-8")
            match = re.search(r"SSID\s+:\s(.+)", output)
            if match:
                wifi_name = match.group(1)
                logging.debug(f"Connected WiFi: {wifi_name}")
                return wifi_name
            else:
                logging.warning("No WiFi connection found.")
                return "No WiFi"
        except subprocess.CalledProcessError:
            logging.error("Error accessing WiFi information.")
            return "No WiFi"

class PerformanceMonitor:
    def __init__(self, db_logger):
        self.db_logger = db_logger
        self.cpu_usage_history = []
        self.ram_usage_history = []
        self.disk_usage_history = []

    def collect_performance_data(self):
        while True:
            cpu_usage = SystemInfo.cpu()
            ram_usage = SystemInfo.ram()
            disk_usage = SystemInfo.disk_usage()
            ip_address = SystemInfo.ip()
            mac_address = SystemInfo.mac()

            self.db_logger.insert_data(cpu_usage, ram_usage, disk_usage, ip_address, mac_address)

            self.cpu_usage_history.append(cpu_usage)
            self.ram_usage_history.append(ram_usage)
            self.disk_usage_history.append(disk_usage)

            sleep(60)  # Pause for a minute before collecting the next data point

    def analyze_data(self):
        cpu_avg = sum(self.cpu_usage_history) / len(self.cpu_usage_history)
        ram_avg = sum(self.ram_usage_history) / len(self.ram_usage_history)
        disk_avg = sum([int(disk.split(":")[1].strip()) for disk in self.disk_usage_history]) / len(self.disk_usage_history)

        logging.info(f"Average CPU Usage: {cpu_avg}%")
        logging.info(f"Average RAM Usage: {ram_avg}%")
        logging.info(f"Average Disk Usage: {disk_avg}GB")

class NetworkAnalyzer:
    @staticmethod
    def ping_test(target="8.8.8.8"):
        try:
            response = subprocess.run(["ping", "-c", "4", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if response.returncode == 0:
                logging.info(f"Ping successful to {target}")
            else:
                logging.warning(f"Ping failed to {target}")
        except Exception as e:
            logging.error(f"Error during ping test: {e}")

    @staticmethod
    def traceroute(target="8.8.8.8"):
        try:
            response = subprocess.run(["traceroute", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if response.returncode == 0:
                logging.info(f"Traceroute successful to {target}")
            else:
                logging.warning(f"Traceroute failed to {target}")
        except Exception as e:
            logging.error(f"Error during traceroute test: {e}")

    @staticmethod
    def bandwidth_test():
        try:
            download_speed = random.randint(50, 200)  # Simulated download speed in Mbps
            upload_speed = random.randint(10, 50)  # Simulated upload speed in Mbps
            logging.info(f"Simulated Download Speed: {download_speed} Mbps")
            logging.info(f"Simulated Upload Speed: {upload_speed} Mbps")
        except Exception as e:
            logging.error(f"Error during bandwidth test: {e}")

# Graphical User Interface
class PerformanceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Performance Monitor")
        self.root.geometry("1000x700")

        self.db_logger = DatabaseLogger()
        self.monitor = PerformanceMonitor(self.db_logger)

        self.create_ui()

    def create_ui(self):
        self.label_cpu = tk.Label(self.root, text="CPU Usage: 0%", font=("Helvetica", 14))
        self.label_cpu.pack(pady=10)

        self.label_ram = tk.Label(self.root, text="RAM Usage: 0%", font=("Helvetica", 14))
        self.label_ram.pack(pady=10)

        self.label_disk = tk.Label(self.root, text="Disk Usage: 0 GB", font=("Helvetica", 14))
        self.label_disk.pack(pady=10)

        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.ax.set_title("Performance Over Time")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Usage (%)")
        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.get_tk_widget().pack(pady=20)

        self.update_ui()

    def update_ui(self):
        cpu_usage = SystemInfo.cpu()
        ram_usage = SystemInfo.ram()
        disk_usage = SystemInfo.disk_usage()

        self.label_cpu.config(text=f"CPU Usage: {cpu_usage}%")
        self.label_ram.config(text=f"RAM Usage: {ram_usage}%")
        self.label_disk.config(text=f"Disk Usage: {disk_usage}")

        # Update Graph
        self.ax.clear()
        self.ax.plot(self.monitor.cpu_usage_history, label="CPU Usage")
        self.ax.plot(self.monitor.ram_usage_history, label="RAM Usage")
        self.ax.legend()
        self.canvas.draw()

        self.root.after(1000, self.update_ui)

if __name__ == "__main__":
    # Database and system performance logger
    app = tk.Tk()
    monitor_app = PerformanceMonitorApp(app)

    threading.Thread(target=monitor_app.monitor.collect_performance_data, daemon=True).start()
    
    app.mainloop()
