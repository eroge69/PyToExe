import tkinter as tk
from tkinter import messagebox, simpledialog
from pysnmp.hlapi import *

# Список для хранения IP-адресов принтеров
printer_ips = []

# Функция для добавления IP-адреса принтера
def add_printer_ip():
    ip = simpledialog.askstring("Добавить принтер", "Введите IP-адрес принтера:")
    if ip and ip not in printer_ips:
        printer_ips.append(ip)
        ip_listbox.insert(tk.END, ip)

# Функция для удаления IP-адреса принтера
def remove_printer_ip():
    selected_index = ip_listbox.curselection()
    if selected_index:
        ip = ip_listbox.get(selected_index[0])
        printer_ips.remove(ip)
        ip_listbox.delete(selected_index[0])

# Функция для опроса принтера через SNMP
def get_toner_level(ip):
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData('public'),  # Общедоступное сообщество (может отличаться для разных принтеров)
            UdpTransportTarget((ip, 161)),  # Порт SNMP
            ContextData(),
            ObjectType(ObjectIdentity('1.3.6.1.2.1.43.11.1.1.9.1.1'))  # OID для уровня черного тонера
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            return f"Ошибка: {errorIndication}"
        elif errorStatus:
            return f"Ошибка: {errorStatus.prettyPrint()}"
        else:
            for varBind in varBinds:
                toner_level = str(varBind).split('=')[-1].strip()
                return f"Уровень тонера: {toner_level}%"
    except Exception as e:
        return f"Не удалось получить данные: {str(e)}"

# Функция для опроса всех принтеров
def poll_printers():
    results = []
    for ip in printer_ips:
        result = get_toner_level(ip)
        results.append(f"Принтер {ip}: {result}")
    
    messagebox.showinfo("Результаты опроса", "\n".join(results))

# Создание GUI
root = tk.Tk()
root.title("Мониторинг принтеров")

# Список IP-адресов
ip_listbox = tk.Listbox(root, width=20, height=10)
ip_listbox.pack(side=tk.LEFT, padx=10, pady=10)

# Кнопки управления
button_frame = tk.Frame(root)
button_frame.pack(side=tk.RIGHT, padx=10, pady=10)

add_button = tk.Button(button_frame, text="Добавить принтер", command=add_printer_ip)
add_button.pack(fill=tk.X, pady=5)

remove_button = tk.Button(button_frame, text="Удалить принтер", command=remove_printer_ip)
remove_button.pack(fill=tk.X, pady=5)

poll_button = tk.Button(button_frame, text="Опросить принтеры", command=poll_pollers)
poll_button.pack(fill=tk.X, pady=5)

# Запуск приложения
root.mainloop()
