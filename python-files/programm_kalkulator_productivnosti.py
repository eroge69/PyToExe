import tkinter as tk
from tkinter import PhotoImage
import datetime


class ProductivityCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Калькулятор производительности")
        self.geometry("400x450")
        self.configure(bg="#E6E6FA")  # Светло-фиолетовый цвет

        # Установите иконку (укажите путь к вашей иконке .ico)
        self.icon= PhotoImage(file="C:/Users/student/PycharmProjects/AIOGRAM/png.png")  # Замените 'path_to_your_icon.ico' на путь к вашей иконке
        self.iconphoto(True,self.icon)
        self.activities = {
            'Подготовка': tk.StringVar(),
            'Отдых': tk.StringVar(),
            'Учеба': tk.StringVar(),
            'Спорт': tk.StringVar(),
            'Развлечения': tk.StringVar(),
            'Другие активности': tk.StringVar()
        }

        self.create_widgets()

    def create_widgets(self):
        header = tk.Label(self, text="Введите время на активности", bg="#E6E6FA", font=("Helvetica", 16, "bold"))
        header.pack(pady=10)

        frame = tk.Frame(self, bg="#E6E6FA")
        frame.pack(pady=10)

        # Создаем поля ввода для каждой активности
        for i, activity in enumerate(self.activities):
            label = tk.Label(frame, text=activity, bg="#E6E6FA", font=("Helvetica", 12))
            label.grid(row=i, column=0, padx=10, pady=5)

            entry = tk.Entry(frame, textvariable=self.activities[activity], width=10, font=("Helvetica", 12))
            entry.grid(row=i, column=1, padx=10, pady=5)

        submit_button = tk.Button(self, text="Подсчитать продуктивность", command=self.calculate_productivity,
                                  bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"))
        submit_button.pack(pady=20)

    def calculate_productivity(self):
        total_time = datetime.timedelta()
        time_for_work = datetime.timedelta()

        for activity, time_str in self.activities.items():
            try:
                hours, minutes = map(int, time_str.get().split(':'))
                activity_time = datetime.timedelta(hours=hours, minutes=minutes)

                total_time += activity_time
                if activity == 'Подготовка':
                    time_for_work = activity_time

            except ValueError:
                messagebox.showerror("Ошибка",
                                     f"Неверный формат времени для {activity}. Пожалуйста, введите в формате HH:MM.")
                return

        productivity_ratio = (time_for_work / total_time) * 100 if total_time > datetime.timedelta(0) else 0

        results = f"\nВаше время, затраченное на активности:\n"
        for activity in self.activities.keys():
            results += f"{activity}: {self.activities[activity].get()}\n"

        results += f"\nОбщее время: {total_time}\n"
        results += f"Ваш коэффициент производительности: {productivity_ratio:.2f}%\n"

        if productivity_ratio < 50:
            results += "😟 Рекомендуем улучшить вашу продуктивность в подготовке."
        elif productivity_ratio < 75:
            results += "😐 Вы на правильном пути, но есть возможности для улучшения."
        else:
            results += "😁 Отличная работа! Вы хорошо используете свое время."

        messagebox.showinfo("Результаты", results)


if __name__ == "__main__":
    app = ProductivityCalculator()
    app.mainloop()