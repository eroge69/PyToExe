import tkinter as tk
from tkinter import messagebox
import requests  # Для отправки HTTP-запросов

def send_mac_command():
    mac_input = entry_mac.get().strip()  # Получаем введённый MAC
    
    # Проверяем корректность формата (00-00-00-00-00-00)
    if len(mac_input) != 17 or mac_input.count("-") != 5:
        messagebox.showerror("Ошибка", "Некорректный формат MAC! Используйте 00-00-00-00-00-00")
        return
    
    # Заменяем дефисы на двоеточия
    mac_formatted = mac_input.replace("-", ":")
    
    # Формируем URL
    url = f"http://192.168.0.160/sw.cgi?spar={mac_formatted}"
    
    try:
        # Отправляем GET-запрос
        response = requests.get(url, timeout=5)
        
        # Проверяем статус ответа
        if response.status_code == 200:
            messagebox.showinfo("Успех", f"Запрос отправлен!\nURL: {url}")
        else:
            messagebox.showerror("Ошибка", f"Сервер вернул код {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка", f"Не удалось отправить запрос: {e}")

# Создаём графическое окно
root = tk.Tk()
root.title("MAC-адрес → Веб-запрос")
root.geometry("400x150")

# Поле ввода MAC
label = tk.Label(root, text="Введите MAC-адрес (00-00-00-00-00-00):")
label.pack(pady=10)

entry_mac = tk.Entry(root, width=20, font=("Arial", 12))
entry_mac.pack(pady=5)

# Кнопка отправки
button_send = tk.Button(root, text="Отправить", command=send_mac_command)
button_send.pack(pady=10)

root.mainloop()