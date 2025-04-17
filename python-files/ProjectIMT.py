import tkinter as tk
from tkinter import messagebox

def calculate_bmi():
    def on_calculate():
        try:
            name = name_entry.get()
            age = int(age_entry.get())
            weight = float(weight_entry.get())
            height = float(height_entry.get())
            bmi = weight / (height ** 2)

            if bmi < 18.5:
                category = "Недостаточный вес"
                advice = "Ты лёгкий как пушинка! Может пора на обед? 🍕"
            elif 18.5 <= bmi < 25:
                category = "Нормальный вес"
                advice = "Ты как раз как надо! Продолжай в том же духе! 💪"
            elif 25 <= bmi < 30:
                category = "Избыточный вес"
                advice = "Немного тяжеловат, но ничего — меньше пончиков, больше танцев! 🕺🍩"
            else:
                category = "Ожирение"
                advice = "В тебе много личности! Попробуй заменить чипсы на морковку. 🥕😉"

            result = f"Имя: {name}\nВозраст: {age} лет\nВаш ИМТ: {bmi:.2f}\nКатегория: {category}\nСовет: {advice}"
            messagebox.showinfo("Результаты расчета ИМТ", result)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения.")


    root = tk.Tk()
    root.title("Калькулятор ИМТ")
    root.geometry("500x350")  # Размер окна



    root.iconphoto(False, tk.PhotoImage(file="ИМТ.png"))  # Замените "icon.png" на имя вашего файла


    root.configure(bg="#7FFFD4")

    # Шрифты
    font_label = ('Helvetica', 12, 'bold')
    font_entry = ('Helvetica', 12)
    font_button = ('Helvetica', 14, 'bold')


    tk.Label(root, text="Имя:", font=font_label, bg="#7FFFD4").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    name_entry = tk.Entry(root, width=30, font=font_entry)
    name_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Возраст:", font=font_label, bg="#7FFFD4").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    age_entry = tk.Entry(root, width=30, font=font_entry)
    age_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="Вес (кг):", font=font_label, bg="#7FFFD4").grid(row=2, column=0, padx=10, pady=10, sticky='e')
    weight_entry = tk.Entry(root, width=30, font=font_entry)
    weight_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(root, text="Рост (м):", font=font_label, bg="#7FFFD4").grid(row=3, column=0, padx=10, pady=10, sticky='e')
    height_entry = tk.Entry(root, width=30, font=font_entry)
    height_entry.grid(row=3, column=1, padx=10, pady=10)


    calculate_button = tk.Button(root, text="Рассчитать ИМТ", font=font_button, command=on_calculate, bg="#4CAF50", fg="white", relief="flat", padx=10, pady=10)
    calculate_button.grid(row=4, column=0, columnspan=2, pady=20)


    calculate_button.config(borderwidth=3, relief="raised", bd=3)

    root.mainloop()

calculate_bmi()