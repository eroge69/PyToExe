
import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt

# Первая и вторая функции по варианту
def f1(x, A):
    return - np.sqrt(2*A(-3*A + x)) # для x < 0

def f2(x, A):
    return A * cos(x + 3 * A)  # для x >= 0

# Главная функция согласно F(x, A) с выбором по k * A
def final_function(x, A, k):
    if x >= k * A:
        return f2(x, A)
    else:
        return f1(x, A)

# Табулирование
def tabulate_function(N, A, dX, k):
    X1 = -A
    X_values = np.array([X1 + i * dX for i in range(N)])
    Y_values = np.array([final_function(x, A, k) for x in X_values])
    return X_values, Y_values

# Очистка и фокусировка на неверных полях
def validate_fields():
    fields = {
        'A': entry_a,
        'N': entry_n,
        'dX': entry_dx,
        'k': entry_k
    }
    values = {}
    errors = []

    try:
        values['A'] = float(fields['A'].get())
        if values['A'] <= -0:
            raise ValueError("A должно быть больше 0")
    except:
        fields['A'].delete(0, tk.END)
        fields['A'].focus()
        errors.append("Введите корректное значение A (> 0)")

    try:
        values['N'] = int(fields['N'].get())
        if values['N'] <= 1:
            raise ValueError("N должно быть больше 1")
    except:
        fields['N'].delete(0, tk.END)
        if not errors:
            fields['N'].focus()
        errors.append("Введите целое значение N (> 1)")

    try:
        values['dX'] = float(fields['dX'].get())
        if values['dX'] <= 0:
            raise ValueError("dX должно быть положительным")
    except:
        fields['dX'].delete(0, tk.END)
        if not errors:
            fields['dX'].focus()
        errors.append("Введите корректное значение dX (> 0)")

    try:
        values['k'] = float(fields['k'].get())
        if values['k'] <= -3:
            raise ValueError("k должно быть больше -3")
    except:
        fields['k'].delete(0, tk.END)
        if not errors:
            fields['k'].focus()
        errors.append("Введите корректное значение k (> -3)")

    return values if not errors else errors

# Кнопка "Принять"
def on_submit():
    result = validate_fields()

    if isinstance(result, list):
        messagebox.showwarning("Некорректный ввод", "\n".join(result))
        return

    A, N, dX, k = result['A'], result['N'], result['dX'], result['k']

    X_values, Y_values = tabulate_function(N, A, dX, k)

    # Окно с таблицей всех точек
    top = tk.Toplevel()
    top.title("Все вычисленные точки")
    top.geometry("360x" + str(60 + 25 * len(X_values)))
    header = tk.Label(top, text="N     Значение аргумента     Значение функции", font=("Courier", 10))
    header.pack()
    for i, (x, y) in enumerate(zip(X_values, Y_values), 1):
        row = tk.Label(top, text=f"{i:<4}  {x:>10.4f}            {y:>10.4f}", font=("Courier", 11))
        row.pack()
    top.lift()
    top.attributes('-topmost', True)
    top.after_idle(top.attributes, '-topmost', False)

    # График и таблица в консоль
    print(f"{'N':<5}{'X':<10}{'Y':<10}")
    print("="*30)
    for i, (x, y) in enumerate(zip(X_values, Y_values), 1):
        print(f"{i:<5}{x:<10.4f}{y:<10.4f}")

    plt.figure(figsize=(10, 5))
    plt.plot(X_values, Y_values, marker='o', linestyle='-', color='teal')
    plt.title('График табулированной параметрической функции')
    plt.xlabel('Значение аргумента X')
    plt.ylabel('Значение функции Y')
    plt.grid(True)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.show()

# Кнопка "Отменить"
def on_cancel():
    entry_a.delete(0, tk.END)
    entry_n.delete(0, tk.END)
    entry_dx.delete(0, tk.END)
    entry_k.delete(0, tk.END)

# Интерфейс
root = tk.Tk()
root.title("Информационные технологии ")
root.geometry("420x300")
root.configure(bg='blue')

label_a = tk.Label(root, text="Введите параметр A (> 0):", bg='white')
label_a.pack()
entry_a = tk.Entry(root, width=20)
entry_a.pack()

label_n = tk.Label(root, text="Введите количество точек N (> 1):", bg='white')
label_n.pack()
entry_n = tk.Entry(root, width=20)
entry_n.pack()

label_dx = tk.Label(root, text="Введите шаг dX:", bg='white')
label_dx.pack()
entry_dx = tk.Entry(root, width=20)
entry_dx.pack()

label_k = tk.Label(root, text="Введите коэффициент выбора функции k (> -3):", bg='white')
label_k.pack()
entry_k = tk.Entry(root, width=20)
entry_k.pack()

btn_frame = tk.Frame(root, bg='white')
btn_frame.pack(pady=10)

btn_ok = tk.Button(btn_frame, text="✔ Принять", bg='lime', width=10, command=on_submit)
btn_ok.grid(row=0, column=0, padx=10)

btn_cancel = tk.Button(btn_frame, text="✘ Отменить", bg='red', fg='white', width=10, command=on_cancel)
btn_cancel.grid(row=0, column=1, padx=10)

root.mainloop()
