import tkinter as tk
from tkinter import messagebox, ttk
import serial
import serial.tools.list_ports
import time

class HC05App:
    def __init__(self, master):
        self.master = master
        self.master.title("HC-05 Configurator")
        self.master.geometry("300x400")

        self.baudrate = None
        self.timeout = 1
        self.ser = None

        self.create_widgets()

    def create_widgets(self):
        # Заголовок
        self.label = tk.Label(self.master, text="Выбор режима HC-05", font=("Helvetica", 16))
        self.label.pack(pady=10)

        # Выбор COM порта
        self.port_label = tk.Label(self.master, text="Выберите COM порт:")
        self.port_label.pack(pady=5)

        self.port_combobox = ttk.Combobox(self.master, state="readonly", value=self.get_serial_ports())
        self.port_combobox.pack(pady=5)
        
        self.rate_label = tk.Label(self.master, text="Выберите скорость загрузки:")
        self.rate_label.pack(pady=5)
        
        self.rate_combobox = ttk.Combobox(self.master, state="readonly", value=["50", "75", "110", "134", "150", "300", "600", "1200", "2400", "4800", "9600", "14400", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.rate_combobox.pack(pady=5)

        # Кнопки для выбора режима
        self.master_button = ttk.Button(self.master, text="Master", command=self.set_master_mode)
        self.master_button.pack(pady=5)

        self.slave_button = ttk.Button(self.master, text="Slave", command=self.set_slave_mode)
        self.slave_button.pack(pady=5)

        # Статус
        self.status_label = tk.Label(self.master, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

        # Выход
        self.quit_button = ttk.Button(self.master, text="Выход", command=self.quit)
        self.quit_button.pack(pady=20)

    def get_serial_ports(self):
        """Получить список доступных COM портов"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports if ports else ["Нет доступных портов"]

    def connect_serial(self):
        self.port = self.port_combobox.get()
        self.baudrate = self.rate_combobox.get()
        if self.port == "Нет доступных портов":
            messagebox.showerror("Ошибка", "Нет доступных COM портов.")
            return

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # время для инициализации
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть последовательный порт: {e}")
            self.ser = None

    def send_at_command(self, command, response_timeout=2):
        if self.ser:
            self.ser.write((command + '\r\n').encode())
            time.sleep(response_timeout)
            response = self.ser.read_all().decode()
            return response
        else:
            messagebox.showerror("Ошибка", "Последовательный порт не открыт.")
            return None

    def set_mode(self, mode):
        if mode == 'master':
            response = self.send_at_command('AT+ROLE=1')
            return response
        elif mode == 'slave':
            response = self.send_at_command('AT+ROLE=0')
            return response
        return None

    def set_master_mode(self):
        self.connect_serial()
        result = self.set_mode('master')
        if result is not None:
            self.status_label.config(text="Модуль настроен как Master.")
        self.check_current_role()

    def set_slave_mode(self):
        self.connect_serial()
        result = self.set_mode('slave')
        if result is not None:
            self.status_label.config(text="Модуль настроен как Slave.")
        self.check_current_role()

    def check_current_role(self):
        if self.ser:
            current_role = self.send_at_command('AT+ROLE?')
            if current_role:
                current_role = current_role.strip()
                messagebox.showinfo("Текущий режим", f"Текущий режим: {current_role}")
            self.ser.close()

    def quit(self):
        if self.ser:
            self.ser.close()
        self.master.quit()

if __name__ == '__main__':
    root = tk.Tk()
    app = HC05App(root)
    root.mainloop()