import time
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def calculate_price():
    width = width_entry.get()
    height = height_entry.get()

    if not width or not height:
        messagebox.showerror("Ошибка", "Пожалуйста, введите ширину и высоту.")
        return

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://pifagor-kupe.ru/dveri-kupe-na-zakaz/")
        
        time.sleep(5)  # Ждем загрузки страницы

        driver.find_element(By.NAME, "widthOpen").clear()
        driver.find_element(By.NAME, "widthOpen").send_keys(width)

        driver.find_element(By.NAME, "heightOpen").clear()
        driver.find_element(By.NAME, "heightOpen").send_keys(height)

        time.sleep(2)  # Ждем пересчета цены

        price_element = driver.find_element(By.CLASS_NAME, "final-price-block__price")
        price = price_element.text

        driver.quit()

        messagebox.showinfo("Результат", f"Стоимость двери: {price}")

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# Создаем окно
root = tk.Tk()
root.title("Расчет стоимости двери-купе")

# Ширина
tk.Label(root, text="Ширина проема (мм):").pack(pady=5)
width_entry = tk.Entry(root)
width_entry.pack()

# Высота
tk.Label(root, text="Высота проема (мм):").pack(pady=5)
height_entry = tk.Entry(root)
height_entry.pack()

# Кнопка расчета
tk.Button(root, text="Рассчитать стоимость", command=calculate_price).pack(pady=10)

root.geometry("300x200")
root.mainloop()