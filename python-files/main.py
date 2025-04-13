import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
import threading
import time

# Флаг для остановки поиска устройств
is_scanning = False

# Функция для обновления списка доступных COM-портов
def update_ports():
    available_ports = serial.tools.list_ports.comports()
    com_combobox['values'] = [port.device for port in available_ports]

# Функция для поиска устройств Modbus RTU
def start_device_search():
    global is_scanning
    is_scanning = True

    # Очистим предыдущие результаты
    devices_found_listbox.delete(0, tk.END)
    logs_listbox.delete(0, tk.END)

    # Получаем выбранный COM-порт
    selected_port = com_combobox.get()
    if not selected_port:
        messagebox.showerror("Ошибка", "Выберите COM порт для сканирования")
        return

    # Обнуляем и запускаем прогрессбар
    progress_bar['value'] = 0
    progress_bar['maximum'] = 247  # Установка максимального значения прогрессбара

    # Запускаем поиск устройств в отдельном потоке
    threading.Thread(target=scan_devices, args=(selected_port,)).start()

# Функция для сканирования Modbus устройств
def scan_devices(port):
    global is_scanning
    modbus_client = ModbusSerialClient(port=port, baudrate=9600, timeout=1)
    modbus_client.connect()

    for device_id in range(1, 248):  # Установка диапазона ID от 1 до 247
        if not is_scanning:
            break

        # Выполняем запрос чтения
        response = modbus_client.read_holding_registers(0, 1, slave=device_id)
        
        # Проверяем результат запроса
        if response.isError():  
            # Добавляем сообщение об ошибке в логи
            root.after(0, logs_listbox.insert, tk.END, f"[{time.strftime('%H:%M:%S')}] Ошибка при обращении к устройству ID {device_id}.")
        else:
            # Добавляем найденное устройство в список и лог
            root.after(0, devices_found_listbox.insert, tk.END, f"Устройство найдено: ID = {device_id}")
            root.after(0, logs_listbox.insert, tk.END, f"[{time.strftime('%H:%M:%S')}] Устройство найдено на ID {device_id}")

        # Обновляем прогрессбар
        root.after(0, progress_bar.step)  # Увеличиваем прогрессбар на размер одного шага

    modbus_client.close()  
    messagebox.showinfo("Поиск завершен", "Поиск устройств завершен.")
    is_scanning = False

# Функция для остановки сканирования
def stop_scanning():
    global is_scanning
    is_scanning = False
    logs_listbox.insert(tk.END, "Поиск остановлен.")
    progress_bar.stop()

# Создаем главное окно
root = tk.Tk()
root.title('RS485 Scanner')

# Задаем ширину и высоту окна
width = 685
height = 410

# Устанавливаем размеры окна
root.geometry(f"{width}x{height}")

# Центрируем окно на экране
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = int((screen_width - width) / 2)
y_coordinate = int((screen_height - height) / 2)

# Перемещаем окно в центр экрана
root.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

# Разрешаем изменение размеров окна
root.minsize(400, 300)  # Минимальные размеры окна

# Фрейм для поиска устройств
search_frame = tk.LabelFrame(root, text='Поиск устройств')
search_frame.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')

# Фрейм для выбора COM порта
com_port_frame = tk.LabelFrame(search_frame, text='Выбор COM порта')
com_port_frame.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')

com_label = tk.Label(com_port_frame, text='COM Порт:')
com_label.grid(row=0, column=0, padx=5, pady=5)

com_combobox = ttk.Combobox(com_port_frame, values=[])
com_combobox.grid(row=0, column=1, padx=5, pady=5)

refresh_button = tk.Button(com_port_frame, text='Обновить', command=update_ports)
refresh_button.grid(row=0, column=2, padx=5, pady=5)

# Фрейм кнопок поиска
search_button_frame = tk.LabelFrame(search_frame, text='Запуск/Останов поиска')
search_button_frame.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')

start_search_button = tk.Button(search_button_frame, text='Начать поиск', command=start_device_search)
start_search_button.grid(row=0, column=0, padx=5, pady=5)

stop_search_button = tk.Button(search_button_frame, text='Остановить поиск', command=stop_scanning)
stop_search_button.grid(row=0, column=1, padx=5, pady=5)

# Горизонтальный Progressbar
progress_bar = ttk.Progressbar(search_button_frame, orient='horizontal', length=400, mode='determinate')
progress_bar.grid(row=0, column=3, padx=10, pady=5)

# Фрейм для найденных устройств
found_devices_frame = tk.LabelFrame(search_frame, text='Найденные устройства')
found_devices_frame.grid(row=3, column=0, padx=10, pady=5, columnspan=2, sticky='ew')

# Список найденных устройств
devices_found_listbox = tk.Listbox(found_devices_frame)
devices_found_listbox.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
devices_found_listbox.config(width=100, height=5)

# Фрейм для логов
logs_frame = tk.LabelFrame(search_frame, text='Лог')
logs_frame.grid(row=4, column=0, padx=10, pady=5, columnspan=2, sticky='ew')

# Список логов
logs_listbox = tk.Listbox(logs_frame)
logs_listbox.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
logs_listbox.config(width=100, height=5)

# Обновляем порты при запуске приложения
update_ports()

# Запускаем главный цикл приложения
root.mainloop()