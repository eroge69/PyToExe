import tkinter as tk
from tkinter import messagebox
import numpy as np
import pandas as pd


class EntropyCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор энтропии")
        self.root.configure(bg="#f0f0f0")

        self.matrix_size = 2
        self.entry_widgets = []
        self.generated_matrix = None

        # Фрейм для выбора размера матрицы
        self.size_frame = tk.Frame(root, bg="#f0f0f0")
        self.size_frame.pack(pady=10)

        tk.Label(self.size_frame, text="Размер матрицы:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.size_var = tk.IntVar(value=2)
        self.size_var.trace('w', self.update_matrix_input)

        for size in [2, 3, 4]:
            rb = tk.Radiobutton(self.size_frame, text=f"{size}x{size}", variable=self.size_var,
                                value=size, bg="#f0f0f0", indicatoron=0, width=5)
            rb.pack(side=tk.LEFT, padx=5)

        # Фрейм для выбора режима ввода
        self.mode_frame = tk.Frame(root, bg="#f0f0f0")
        self.mode_frame.pack(pady=5)

        self.mode_var = tk.StringVar(value="manual")
        manual_rb = tk.Radiobutton(self.mode_frame, text="Ручной ввод", variable=self.mode_var,
                                   value="manual", bg="#f0f0f0", indicatoron=0, width=12)
        manual_rb.pack(side=tk.LEFT, padx=5)

        generate_rb = tk.Radiobutton(self.mode_frame, text="Сгенерировать", variable=self.mode_var,
                                     value="generate", bg="#f0f0f0", indicatoron=0, width=12)
        generate_rb.pack(side=tk.LEFT, padx=5)

        # Панель кнопок
        btn_frame = tk.Frame(root, bg="#f0f0f0")
        btn_frame.pack(pady=5)

        self.generate_btn = tk.Button(btn_frame, text="Генерация", command=self.generate_matrix,
                                      bg="#a9d5e3", activebackground="#8ec3d0", width=15)
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(btn_frame, text="Очистить", command=self.clear_entries,
                                   bg="#f8d7da", activebackground="#f1aeb5", width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Фрейм для ввода матрицы
        self.matrix_frame = tk.Frame(root, bg="#f0f0f0")
        self.matrix_frame.pack(pady=10)

        # Кнопка расчета
        self.calculate_btn = tk.Button(root, text="Рассчитать энтропию", command=self.calculate,
                                       bg="#c3e6cb", activebackground="#a9d8b6", width=20)
        self.calculate_btn.pack(pady=10)

        # Текстовое поле для вывода
        self.result_text = tk.Text(root, height=20, width=60, bg="white", relief=tk.SUNKEN)
        self.result_text.pack(pady=10)

        # Инициализация матрицы
        self.create_matrix_input(self.matrix_size)

    def create_matrix_input(self, size):
        """Создает поля ввода с улучшенным дизайном"""
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        self.entry_widgets = []

        for i in range(size):
            row = []
            for j in range(size):
                entry = tk.Entry(self.matrix_frame, width=6, bg="white", relief=tk.GROOVE,
                                 highlightbackground="#ced4da", highlightthickness=1)
                entry.grid(row=i, column=j, padx=2, pady=2)
                row.append(entry)
            self.entry_widgets.append(row)

    def update_matrix_input(self, *args):
        new_size = self.size_var.get()
        if new_size != self.matrix_size:
            self.matrix_size = new_size
            self.create_matrix_input(new_size)
            self.generated_matrix = None

    def generate_matrix(self):
        if self.mode_var.get() != "generate":
            return

        n = self.matrix_size
        matrix = np.random.rand(n, n)
        matrix = matrix / matrix.sum()

        self.generated_matrix = matrix
        self.fill_matrix_entries(matrix)


    def fill_matrix_entries(self, matrix):
        for i in range(self.matrix_size):
            for j in range(self.matrix_size):
                value = matrix[i][j]
                # Форматируем с запятой для отображения
                display_value = f"{value:.4f}".replace('.', ',')
                self.entry_widgets[i][j].delete(0, tk.END)
                self.entry_widgets[i][j].insert(0, display_value)

    def clear_entries(self):
        for row in self.entry_widgets:
            for entry in row:
                entry.delete(0, tk.END)
        self.generated_matrix = None

    def get_input_matrix(self):
        try:
            matrix = []
            for row in self.entry_widgets:
                matrix_row = []
                for entry in row:
                    value_str = entry.get().strip().replace(',', '.')  # Замена запятых на точки
                    if not value_str:
                        raise ValueError("Пустое поле ввода")
                    value = float(value_str)
                    if not (0 <= value <= 1):
                        raise ValueError("Значения должны быть в диапазоне [0,1]")
                    matrix_row.append(value)
                matrix.append(matrix_row)

            matrix = np.array(matrix)
            total = matrix.sum()
            if not np.isclose(total, 1.0, atol=0.0001):
                raise ValueError(f"Сумма элементов должна быть 1 (текущая: {total:.4f})")

            return matrix
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return None

    def calculate(self):
        if self.mode_var.get() == "generate":
            if self.generated_matrix is None:
                messagebox.showerror("Ошибка", "Сначала сгенерируйте матрицу")
                return
            matrix = self.generated_matrix
        else:
            matrix = self.get_input_matrix()
            if matrix is None:
                return

        results = calculate_metrics(matrix)
        result_text = self.format_results(results)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text)

    def format_results(self, results):
        lines = [
            "РЕЗУЛЬТАТЫ РАСЧЕТОВ:",
            f"H(A) = {results['H_A']:.4f}",
            f"H(B) = {results['H_B']:.4f}",
            f"H(A|B) = {results['H_A_given_B']:.4f}",
            f"H(B|A) = {results['H_B_given_A']:.4f}",
            f"H(A,B) = {results['H_AB']:.4f}",
            f"I(A,B) = {results['I_AB']:.4f}",
            f"H(A)max = {results['H_A_max']:.4f}",
            f"H(B)max = {results['H_B_max']:.4f}",
            "\nМатрица p(b|a):",
            str(results['p_b_given_a'].round(4)),
            "\nМатрица p(a|b):",
            str(results['p_a_given_b'].round(4))
        ]
        return "\n".join(lines)


def calculate_metrics(matrix):
    p_a = matrix.sum(axis=1)
    p_b = matrix.sum(axis=0)

    with np.errstate(divide='ignore', invalid='ignore'):
        p_b_given_a = np.nan_to_num(matrix / p_a[:, np.newaxis], posinf=0)
        p_a_given_b = np.nan_to_num(matrix / p_b, posinf=0)

    def entropy(prob):
        prob = prob[prob > 0]
        return -(prob * np.log2(prob)).sum() if len(prob) > 0 else 0

    H_A = entropy(p_a)
    H_B = entropy(p_b)
    H_A_max = np.log2(len(p_a[p_a > 0])) if any(p_a > 0) else 0
    H_B_max = np.log2(len(p_b[p_b > 0])) if any(p_b > 0) else 0

    H_B_given_A = (p_a * np.array([entropy(row) for row in p_b_given_a])).sum()
    H_A_given_B = (p_b * np.array([entropy(col) for col in p_a_given_b.T])).sum()
    H_AB = H_A + H_B_given_A
    I_AB = H_A - H_A_given_B

    return {
        "p_a": p_a,
        "p_b": p_b,
        "p_b_given_a": p_b_given_a,
        "p_a_given_b": p_a_given_b,
        "H_A": H_A,
        "H_B": H_B,
        "H_A_max": H_A_max,
        "H_B_max": H_B_max,
        "H_B_given_A": H_B_given_A,
        "H_A_given_B": H_A_given_B,
        "H_AB": H_AB,
        "I_AB": I_AB
    }


if __name__ == "__main__":
    root = tk.Tk()
    app = EntropyCalculatorApp(root)
    root.mainloop()
