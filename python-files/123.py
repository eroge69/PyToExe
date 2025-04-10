import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import math

def linspace(start, end, num):
    step = (end - start) / (num - 1)
    return [start + i * step for i in range(num)]

def plot_curve():
    equation = equation_entry.get().strip()
    coord_type = coord_var.get()

    if not equation:
        messagebox.showerror("Ошибка", "Введите уравнение!")
        return

    try:
        if coord_type == "polar":
            # Полярные координаты
            rho_expr = equation.split("=")[1].strip()
            theta = linspace(0, 4 * math.pi, 1000)
            rho = [eval(rho_expr, {"math": math, "theta": t}) for t in theta]
            x = [r * math.cos(t) for r, t in zip(rho, theta)]
            y = [r * math.sin(t) for r, t in zip(rho, theta)]
            plt.figure(figsize=(8, 8))
            plt.plot(x, y, label=f"ρ = {rho_expr}")
            plt.title("График в полярных координатах")
        elif coord_type == "cartesian":
            # Декартовы координаты
            y_expr = equation.split("=")[1].strip()
            x = linspace(-10, 10, 1000)
            y = [eval(y_expr, {"math": math, "x": xi}) for xi in x]
            plt.figure(figsize=(8, 6))
            plt.plot(x, y, label=f"y = {y_expr}")
            plt.title("График в декартовых координатах")
        else:
            messagebox.showerror("Ошибка", "Выберите тип координат!")
            return

        plt.xlabel("x")
        plt.ylabel("y")
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        plt.legend()
        plt.axis('equal')
        plt.show()

    except Exception as e:
        messagebox.showerror("Ошибка", f"Неверное уравнение: {e}")

# Создание графического интерфейса
root = tk.Tk()
root.title("Программа для рисования кривых и спиралей")

coord_label = tk.Label(root, text="Выберите тип координат:")
coord_label.pack(pady=5)

coord_var = tk.StringVar(value="cartesian")

cartesian_radio = tk.Radiobutton(root, text="Декартовы (y = ...)", variable=coord_var, value="cartesian")
polar_radio = tk.Radiobutton(root, text="Полярные (ρ = ...)", variable=coord_var, value="polar")
cartesian_radio.pack()
polar_radio.pack()

equation_label = tk.Label(root, text="Введите уравнение:")
equation_label.pack(pady=5)
equation_entry = tk.Entry(root, width=50)
equation_entry.pack()

plot_button = tk.Button(root, text="Построить график", command=plot_curve)
plot_button.pack(pady=10)

root.mainloop()
