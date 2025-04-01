import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        value = entry_spz.get()
        value = value.replace(',', '.')
        number = float(value)

        sum_val = number * 0.3
        sum1_val = number * 0.7
        sum3_val = (number * 0.7) / 9

        sum_rounded = round(sum_val, 2)
        sum1_rounded = round(sum1_val, 2)
        sum3_rounded = round(sum3_val, 2)

        result_text = (
            f"Сумма к оплате: {sum_rounded}\n"
            f"Сумма списания: {sum1_rounded}\n"
            f"Сумма списания с рассрочкой на 9 месяцев: {sum3_rounded}"
        )

        # Создаем новое окно для отображения результатов
        result_window = tk.Toplevel(root)
        result_window.title("Результат расчета")

        # Создаем текстовое поле для результатов
        text_widget = tk.Text(result_window, height=5, width=40)
        text_widget.insert(tk.END, result_text)
        text_widget.config(state=tk.DISABLED)  # Делаем поле только для чтения
        text_widget.pack()

    except ValueError:
        messagebox.showerror("Ошибка", "Введите число, пожалуйста.")
        entry_spz.delete(0, tk.END) #Очищает строку ввода

# Создаем основное окно
root = tk.Tk()
root.title("Расчет СПЗ")

# Создаем метку для поля ввода
label_spz = tk.Label(root, text="Введите СПЗ:")
label_spz.pack()

# Создаем поле ввода
entry_spz = tk.Entry(root)
entry_spz.pack()

# Создаем кнопку для запуска расчета
button_calculate = tk.Button(root, text="Рассчитать", command=calculate)
button_calculate.pack()

# Запускаем главный цикл обработки событий
root.mainloop()