
import tkinter as tk
from tkinter import messagebox
import datetime

def calculate():
    try:
        price1 = float(entry_price1.get().replace(',', '.'))
        price2 = float(entry_price2.get().replace(',', '.'))
        bars = int(entry_bars.get())

        trend = "ВВЕРХ" if price2 > price1 else "ВНИЗ"
        delta = abs(price2 - price1)
        step = delta / bars

        directions = [0.125, 0.25, 0.333, 0.5, 1, 1.5, 2, 3, 4, 8]
        result_lines = []
        for d in directions:
            move = step * d * bars
            if trend == "ВВЕРХ":
                target = price1 + move
            else:
                target = price1 - move
            result_lines.append(f"{d}x1: от {price1:.3f} к {target:.3f}")

        result_text = (
            f"Тренд : {trend}\n"
            f"Начальная цена: {price1}\n"
            f"Конечная цена: {price2}\n"
            f"Баров между точками: {bars}\n"
            f"Изменение цены на 1 бар: {step:.6f}\n\n"
            f"Координаты веера Ганна:\n" + "\n".join(result_lines)
        )
        output.delete(1.0, tk.END)
        output.insert(tk.END, result_text)

        # Save to txt file
        with open("gann_fan_result.txt", "w", encoding="utf-8") as f:
            f.write(result_text)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Неверный ввод: {e}")

root = tk.Tk()
root.title("Gann Fan Builder Portable")

tk.Label(root, text="Цена 1 (High/Low):").grid(row=0, column=0, sticky="w")
tk.Label(root, text="Цена 2 (High/Low):").grid(row=1, column=0, sticky="w")
tk.Label(root, text="Количество баров:").grid(row=2, column=0, sticky="w")

entry_price1 = tk.Entry(root)
entry_price2 = tk.Entry(root)
entry_bars = tk.Entry(root)

entry_price1.grid(row=0, column=1)
entry_price2.grid(row=1, column=1)
entry_bars.grid(row=2, column=1)

tk.Button(root, text="Рассчитать", command=calculate).grid(row=3, columnspan=2, pady=5)

output = tk.Text(root, height=15, width=50)
output.grid(row=4, columnspan=2)

root.mainloop()
