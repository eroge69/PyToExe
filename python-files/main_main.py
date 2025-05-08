import sys
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QFileDialog, QLabel
)
from PyQt6.QtGui import QFont

def max_min_composition(R1, R2):
    return np.max(np.minimum(R1[:, :, np.newaxis], R2), axis=1)

def max_prod_composition(R1, R2):
    return np.max(R1[:, :, np.newaxis] * R2, axis=1)

class MatrixApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Композиция матриц (max-min и max-prod)")
        self.resize(1200, 800)

        # Widgets
        self.text_r1 = QTextEdit()
        self.text_r2 = QTextEdit()
        self.result = QTextEdit()
        self.result.setFont(QFont("Courier", 10))
        self.result.setReadOnly(True)

        # Buttons
        load_r1 = QPushButton("Загрузить R1")
        load_r2 = QPushButton("Загрузить R2")
        save_result = QPushButton("Сохранить результат")
        compute_btn = QPushButton("Вычислить")

        load_r1.clicked.connect(self.load_r1)
        load_r2.clicked.connect(self.load_r2)
        save_result.clicked.connect(self.save_result)
        compute_btn.clicked.connect(self.compute)

        # Layout
        layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        r1_block = QVBoxLayout()
        r1_block.addWidget(QLabel("Матрица R1 (5×10):"))
        r1_block.addWidget(self.text_r1)
        r1_block.addWidget(load_r1)

        r2_block = QVBoxLayout()
        r2_block.addWidget(QLabel("Матрица R2 (5×10):"))
        r2_block.addWidget(self.text_r2)
        r2_block.addWidget(load_r2)

        input_layout.addLayout(r1_block)
        input_layout.addLayout(r2_block)

        layout.addLayout(input_layout)
        layout.addWidget(compute_btn)
        layout.addWidget(QLabel("Результаты:"))
        layout.addWidget(self.result)
        layout.addWidget(save_result)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def parse_matrix(self, text):
        lines = text.strip().splitlines()
        data = []
        for line in lines:
            row = [float(x.replace(",", ".")) for x in line.strip().split()]
            data.append(row)
        return np.array(data)

    def compute(self):
        try:
            R1 = self.parse_matrix(self.text_r1.toPlainText())
            R2 = self.parse_matrix(self.text_r2.toPlainText()).T  # транспонируем

            max_min = max_min_composition(R1, R2)
            max_prod = max_prod_composition(R1, R2)

            # Определение названий
            if hasattr(self, "df_r1") and hasattr(self, "df_r2"):
                professions = list(self.df_r1.index)
                candidates = list(self.df_r2.index)
            else:
                professions = [f"Профессия {i+1}" for i in range(R1.shape[0])]
                candidates = [f"Кандидат {j+1}" for j in range(R2.shape[1])]

            df_min = pd.DataFrame(max_min, index=professions, columns=candidates)
            df_prod = pd.DataFrame(max_prod, index=professions, columns=candidates)

            df_min.index.name = "Профессия"
            df_min.columns.name = "Кандидат"
            df_prod.index.name = "Профессия"
            df_prod.columns.name = "Кандидат"

            result_text = "Результат max-min:\n" + df_min.to_string() + "\n\n"
            result_text += "Результат max-prod:\n" + df_prod.to_string()
            self.result.setPlainText(result_text)

        except Exception as e:
            self.result.setPlainText(f"Ошибка: {e}")

    def load_r1(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Загрузить CSV R1", "", "CSV Files (*.csv)")
        if fname:
            df = pd.read_csv(fname, index_col=0, header=None)
            df.columns = [f"Критерий {i+1}" for i in range(df.shape[1])]
            self.df_r1 = df  # сохранить DataFrame с подписями
            self.text_r1.setPlainText('\n'.join(' '.join(map(str, row)) for row in df.values))

    def load_r2(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Загрузить CSV R2", "", "CSV Files (*.csv)")
        if fname:
            df = pd.read_csv(fname, index_col=0, header=None)
            df.columns = [f"Критерий {i+1}" for i in range(df.shape[1])]
            self.df_r2 = df  # сохранить DataFrame с подписями
            self.text_r2.setPlainText('\n'.join(' '.join(map(str, row)) for row in df.values))


    def save_result(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Сохранить результат", "", "Text Files (*.txt)")
        if fname:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(self.result.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MatrixApp()
    window.show()
    sys.exit(app.exec())
