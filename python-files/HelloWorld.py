import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import serial
import threading
import json
import time
from dataclasses import dataclass
import numpy as np
from scipy import signal  # Для анализа частот

@dataclass
class HeadsetInfo:
    name: str = "Неизвестно"
    battery: int = 0
    frequency: float = 0.0
    supported_features: list = None
    firmware: str = "0.0"

class WirelessHeadsetController:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced 2.4GHz Headset Controller")
        self.root.geometry("900x650")
        
        self.headsets = []
        self.current_headset = None
        self.serial_conn = None
        
        self.create_ui()
        self.scan_devices()
    
    def create_ui(self):
        # Главный контейнер
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Панель устройств
        self.device_frame = ttk.LabelFrame(self.main_frame, text="Обнаруженные устройства")
        self.device_frame.pack(fill=tk.X, pady=5)
        
        self.device_list = ttk.Treeview(self.device_frame, columns=("name", "battery", "freq"), show="headings", height=3)
        self.device_list.heading("name", text="Устройство")
        self.device_list.heading("battery", text="Заряд")
        self.device_list.heading("freq", text="Частота (GHz)")
        self.device_list.pack(fill=tk.X)
        
        ttk.Button(self.device_frame, text="Сканировать", command=self.scan_devices).pack(pady=5)
        
        # Информация об устройстве
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Информация об устройстве")
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = tk.Text(self.info_frame, height=8, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X)
        
        # Управление
        self.control_notebook = ttk.Notebook(self.main_frame)
        
        # Вкладка громкости
        self.volume_tab = ttk.Frame(self.control_notebook)
        self.create_volume_tab()
        self.control_notebook.add(self.volume_tab, text="Громкость")
        
        # Вкладка эквалайзера
        self.eq_tab = ttk.Frame(self.control_notebook)
        self.create_eq_tab()
        self.control_notebook.add(self.eq_tab, text="Эквалайзер")
        
        # Вкладка шумоподавления
        self.anc_tab = ttk.Frame(self.control_notebook)
        self.create_anc_tab()
        self.control_notebook.add(self.anc_tab, text="Шумоподавление")
        
        self.control_notebook.pack(fill=tk.BOTH, expand=True)
    
    def create_volume_tab(self):
        ttk.Label(self.volume_tab, text="Громкость:").pack(pady=5)
        self.volume_slider = ttk.Scale(self.volume_tab, from_=0, to=100, command=self.set_volume)
        self.volume_slider.set(50)
        self.volume_slider.pack(fill=tk.X, padx=20, pady=5)
        
        self.mic_mute_btn = ttk.Button(self.volume_tab, text="Выключить микрофон", command=self.toggle_mic)
        self.mic_mute_btn.pack(pady=10)
    
    def create_eq_tab(self):
        eq_presets = ["Плоский", "Поп", "Рок", "Джаз", "Классика", "Пользовательский"]
        self.eq_var = tk.StringVar(value=eq_presets[0])
        
        ttk.OptionMenu(self.eq_tab, self.eq_var, *eq_presets, command=self.set_eq).pack(pady=10)
        
        # График эквалайзера
        self.eq_canvas = tk.Canvas(self.eq_tab, height=150, bg="white")
        self.eq_canvas.pack(fill=tk.X, padx=10, pady=10)
        self.draw_eq_curve()
    
    def create_anc_tab(self):
        self.anc_var = tk.IntVar(value=1)
        
        ttk.Radiobutton(self.anc_tab, text="Включено", variable=self.anc_var, value=1, 
                       command=lambda: self.set_anc(True)).pack(pady=5)
        ttk.Radiobutton(self.anc_tab, text="Выключено", variable=self.anc_var, value=0,
                       command=lambda: self.set_anc(False)).pack(pady=5)
        
        ttk.Label(self.anc_tab, text="Уровень шумоподавления:").pack(pady=5)
        self.anc_level = ttk.Scale(self.anc_tab, from_=0, to=100, command=self.set_anc_level)
        self.anc_level.set(50)
        self.anc_level.pack(fill=tk.X, padx=20, pady=5)
    
    def scan_devices(self):
        """Сканирование COM-портов и поиск устройств"""
        self.headsets.clear()
        self.device_list.delete(*self.device_list.get_children())
        
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if self.is_headset_port(port):
                try:
                    headset = self.detect_headset(port.device)
                    if headset:
                        self.headsets.append(headset)
                        self.device_list.insert("", "end", values=(
                            headset.name, 
                            f"{headset.battery}%",
                            f"{headset.frequency:.2f}"
                        ))
                except Exception as e:
                    print(f"Ошибка при сканировании {port.device}: {e}")
        
        if not self.headsets:
            messagebox.showwarning("Устройства не найдены", "Не обнаружено совместимых наушников")
    
    def is_headset_port(self, port):
        """Проверка, может ли порт быть наушниками"""
        # Здесь можно добавить проверку VID/PID или других атрибутов
        return True
    
    def detect_headset(self, port):
        """Определение модели наушников и их характеристик"""
        try:
            # Подключаемся к устройству
            with serial.Serial(port, 115200, timeout=1) as ser:
                # Отправляем команду идентификации
                ser.write(b'AT+ID?\r\n')
                response = ser.readline().decode().strip()
                
                if not response:
                    return None
                
                # Анализ ответа для определения модели
                if "HS-2024" in response:
                    # Пример для гипотетической модели HS-2024
                    freq = self.analyze_frequency(ser)
                    return HeadsetInfo(
                        name="HyperSound HS-2024",
                        battery=self.get_battery_level(ser),
                        frequency=freq,
                        supported_features=["volume", "eq", "anc", "mic"],
                        firmware="1.2.3"
                    )
                elif "AUDIO-X5" in response:
                    # Другая модель
                    freq = self.analyze_frequency(ser)
                    return HeadsetInfo(
                        name="AudioMaster X5",
                        battery=self.get_battery_level(ser),
                        frequency=freq,
                        supported_features=["volume", "eq"],
                        firmware="2.1.0"
                    )
        
        except Exception as e:
            print(f"Ошибка при определении устройства: {e}")
            return None
    
    def analyze_frequency(self, ser):
        """Анализ частоты радиоканала"""
        try:
            # Отправляем команду для получения данных о частоте
            ser.write(b'AT+FREQ?\r\n')
            freq_data = ser.readline().decode().strip()
            
            if freq_data:
                return float(freq_data.split(":")[1]) / 1000  # Convert to GHz
            
            # Если устройство не поддерживает команду, делаем частотный анализ
            ser.write(b'AT+RAW\r\n')
            time.sleep(0.1)
            raw_data = ser.read_all()
            
            if raw_data:
                # Простейший анализ FFT для определения доминирующей частоты
                fs = 1000  # Частота дискретизации
                f, Pxx = signal.periodogram(raw_data, fs)
                dominant_freq = f[np.argmax(Pxx)]
                return dominant_freq / 1000  # Convert to GHz
            
            return 2.4  # Значение по умолчанию
            
        except:
            return 2.4  # Значение по умолчанию
    
    def get_battery_level(self, ser):
        """Получение уровня заряда батареи"""
        try:
            ser.write(b'AT+BATT?\r\n')
            batt = ser.readline().decode().strip()
            return int(batt) if batt.isdigit() else 0
        except:
            return 0
    
    def set_volume(self, val):
        if not self.current_headset:
            return
            
        volume = int(float(val))
        # Здесь должна быть логика отправки команды на устройство
        print(f"Установка громкости: {volume}%")
    
    def toggle_mic(self):
        if not self.current_headset:
            return
            
        # Логика переключения микрофона
        print("Переключение микрофона")
    
    def set_eq(self, preset):
        if not self.current_headset:
            return
            
        print(f"Установка эквалайзера: {preset}")
        self.draw_eq_curve()
    
    def set_anc(self, enabled):
        if not self.current_headset:
            return
            
        print(f"Шумоподавление: {'вкл' if enabled else 'выкл'}")
    
    def set_anc_level(self, val):
        if not self.current_headset:
            return
            
        level = int(float(val))
        print(f"Уровень шумоподавления: {level}%")
    
    def draw_eq_curve(self):
        """Рисование кривой эквалайзера"""
        self.eq_canvas.delete("all")
        width = self.eq_canvas.winfo_width()
        height = self.eq_canvas.winfo_height()
        
        # Простейшая визуализация
        preset = self.eq_var.get()
        if preset == "Плоский":
            points = [50] * 10
        elif preset == "Поп":
            points = [60, 65, 70, 65, 60, 55, 50, 45, 40, 35]
        elif preset == "Рок":
            points = [70, 65, 60, 55, 50, 45, 40, 45, 50, 55]
        else:  # По умолчанию плоский
            points = [50] * 10
        
        # Рисуем кривую
        step = width / (len(points) - 1)
        coords = []
        for i, p in enumerate(points):
            x = i * step
            y = height - (p / 100 * height)
            coords.extend([x, y])
        
        self.eq_canvas.create_line(*coords, fill="blue", width=2)
        
        # Рисуем оси
        self.eq_canvas.create_line(0, height-1, width, height-1, fill="black")  # X ось
        self.eq_canvas.create_line(0, 0, 0, height, fill="black")  # Y ось
    
    def update_device_info(self):
        """Обновление информации об устройстве"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        if self.current_headset:
            info = f"""Модель: {self.current_headset.name}
Заряд батареи: {self.current_headset.battery}%
Рабочая частота: {self.current_headset.frequency:.2f} GHz
Прошивка: {self.current_headset.firmware}
Поддерживаемые функции: {', '.join(self.current_headset.supported_features)}"""
            
            self.info_text.insert(tk.END, info)
        
        self.info_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = WirelessHeadsetController(root)
    root.mainloop()