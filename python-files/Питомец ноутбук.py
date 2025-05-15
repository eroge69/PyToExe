import tkinter as tk
import random
from tkinter import messagebox

class LaptopGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Виртуальный ноутбук")
        self.root.geometry("1280x720")

        self.battery = 100
        self.frames_left = ["_\\", "_|", "_/"]  # Анимация при движении влево
        self.frames_right = ["/_", "|_", "\\_"]  # Анимация при движении вправо
        self.current_frame = 0
        self.x, self.y = 100, 150
        self.dx, self.dy = 7, 7  # Скорость движения
        self.moving_right = True  # Начальное направление движения

        self.canvas = tk.Canvas(root, width=1280, height=600)
        self.canvas.pack()

        self.label_battery = tk.Label(root, text=f"Заряд: {self.battery}%", font=("Arial", 14))
        self.label_battery.pack()

        self.button_charge = tk.Button(root, text="Зарядить", command=self.charge_battery)
        self.button_charge.pack(pady=10)

        self.update_animation()
        self.move_laptop()
        self.decrease_battery()

    def update_animation(self):
        if random.random() < 0.3:  # 30% шанс, что ноутбук просто стоит (_|)
            self.current_frame = 1
        else:
            self.current_frame = (self.current_frame + 1) % 3

        self.canvas.delete("all")
        frame_list = self.frames_right if self.moving_right else self.frames_left
        self.canvas.create_text(self.x, self.y, text=frame_list[self.current_frame], font=("Courier", 30), fill="black")
        self.root.after(500, self.update_animation)

    def move_laptop(self):
        if random.random() < 0.3:  # 30% шанс, что ноутбук временно стоит на месте
            self.root.after(50, self.move_laptop)
            return

        self.x += self.dx
        self.y += self.dy

        # Проверка границ окна
        if self.x >= 1200 or self.x <= 50:
            self.dx *= -1
            self.moving_right = self.dx > 0  # Меняем направление анимации

        if self.y >= 550 or self.y <= 50:
            self.dy *= -1

        self.canvas.delete("all")
        frame_list = self.frames_right if self.moving_right else self.frames_left
        self.canvas.create_text(self.x, self.y, text=frame_list[self.current_frame], font=("Courier", 30), fill="black")
        self.root.after(50, self.move_laptop)

    def decrease_battery(self):
        if self.battery > 0:
            self.battery -= 1
            self.label_battery.config(text=f"Заряд: {self.battery}%")

            if self.battery == 10:  # Показываем уведомление при низком заряде
                messagebox.showwarning("Внимание!", "Низкий заряд батареи!")

        self.root.after(1000, self.decrease_battery)

    def charge_battery(self):
        self.battery = 100
        self.label_battery.config(text=f"Заряд: {self.battery}%")

# Запуск приложения
root = tk.Tk()
app = LaptopGUI(root)
root.mainloop()
