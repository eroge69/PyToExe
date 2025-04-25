
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

DATABASE_FILE = 'clients.json'

# Загрузка базы
def load_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    return []

# Сохранение базы
def save_database(clients):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(clients, f, indent=4)

# Добавление клиента
def add_client():
    name = name_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()
    
    if not name or not email or not phone:
        messagebox.showwarning("Ошибка", "Все поля должны быть заполнены")
        return

    clients.append({'name': name, 'email': email, 'phone': phone})
    save_database(clients)
    update_client_list()
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)

# Обновление списка клиентов в интерфейсе
def update_client_list():
    listbox.delete(0, tk.END)
    for client in clients:
        listbox.insert(tk.END, f"{client['name']} | {client['email']} | {client['phone']}")

# Поиск клиента
def search_client():
    query = simpledialog.askstring("Поиск клиента", "Введите имя:")
    if not query:
        return
    listbox.delete(0, tk.END)
    found = [c for c in clients if query.lower() in c['name'].lower()]
    if not found:
        messagebox.showinfo("Результат", "Клиенты не найдены.")
    else:
        for client in found:
            listbox.insert(tk.END, f"{client['name']} | {client['email']} | {client['phone']}")

# Интерфейс
clients = load_database()

root = tk.Tk()
root.title("Клиентская база")

# Вводные поля
tk.Label(root, text="Имя:").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="Email:").grid(row=1, column=0)
email_entry = tk.Entry(root)
email_entry.grid(row=1, column=1)

tk.Label(root, text="Телефон:").grid(row=2, column=0)
phone_entry = tk.Entry(root)
phone_entry.grid(row=2, column=1)

# Кнопки
tk.Button(root, text="Добавить клиента", command=add_client).grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(root, text="Поиск клиента", command=search_client).grid(row=4, column=0, columnspan=2, pady=5)

# Список клиентов
listbox = tk.Listbox(root, width=50)
listbox.grid(row=5, column=0, columnspan=2, pady=10)
update_client_list()

root.mainloop()
