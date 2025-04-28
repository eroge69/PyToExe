import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                            QGridLayout, QPushButton, QMessageBox, 
                            QVBoxLayout, QLabel, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

class TicTacToe(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Крестики - нолики")
        self.setFixedSize(500, 700)
        
        self.set_dark_palette()
        self.size = 5
        self.current_player = 'X'
        self.board = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        
        self.setup_ui()
        
    def set_dark_palette(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(15, 15, 15))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        self.setPalette(dark_palette)
        
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
    
        self.title_label = QLabel("Ход игрока: X")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Comic Sans MS", 20, QFont.Weight.Bold))
        layout.addWidget(self.title_label)

        new_game_btn = QPushButton("Новая игра")
        new_game_btn.setFont(QFont("Comic Sans MS", 14))
        new_game_btn.setFixedHeight(40)
        new_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #3D3D3D;
                color: white;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4D4D4D;
            }
        """)
        new_game_btn.clicked.connect(self.new_game)
        layout.addWidget(new_game_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(15, 15, 15, 25)
        
        # Игровое поле
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setContentsMargins(20, 20, 20, 20)
        self.buttons = []
        
        button_style = """
            QPushButton {{
                background-color: #2D2D2D;
                border: 2px solid #3D3D3D;
                border-radius: 15px;
                color: {color};
                font-size: 28px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #3D3D3D;
            }}
        """
        
        for row in range(self.size):
            button_row = []
            for col in range(self.size):
                btn = QPushButton()
                btn.setFixedSize(80, 80)
                btn.setStyleSheet(button_style.format(color="transparent"))
                btn.clicked.connect(lambda _, r=row, c=col: self.make_move(r, c))
                button_row.append(btn)
                grid.addWidget(btn, row, col)
            self.buttons.append(button_row)
        
        layout.addLayout(grid)
        
        
    def make_move(self, row, col):
        if self.board[row][col] != ' ' or self.check_winner():
            return
            
        self.board[row][col] = self.current_player
        self.buttons[row][col].setText(self.current_player)
        
        color = "#71ff54" if self.current_player == 'X' else "#ff54eb"
        self.buttons[row][col].setStyleSheet(f"""
            QPushButton {{
                background-color: #5f5f5f;
                border: 2px solid #3D3D3D;
                border-radius: 15px;
                color: {color};
                font-size: 52px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: #3D3D3D;
            }}
        """)
        
        if self.check_winner():
            self.show_winner()
            return
            
        if self.is_full():
            self.show_draw()
            return
            
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self.title_label.setText(f"Ход игрока: {self.current_player}")
    
    def check_winner(self):
        for i in range(self.size):
            for j in range(self.size - 4):
                if all(self.board[i][j + k] == self.current_player for k in range(5)):
                    return True
                if all(self.board[j + k][i] == self.current_player for k in range(5)):
                    return True
        
        for i in range(self.size - 4):
            for j in range(self.size - 4):
                if all(self.board[i + k][j + k] == self.current_player for k in range(5)):
                    return True
                if all(self.board[i + 4 - k][j + k] == self.current_player for k in range(5)):
                    return True
        return False
    
    def is_full(self):
        return all(cell != ' ' for row in self.board for cell in row)
    
    def show_winner(self):
        for row in self.buttons:
            for btn in row:
                btn.setEnabled(False)
        QMessageBox.information(self, "Победа!", 
            f"Игрок играющий за ( {self.current_player} ) выиграл!")
        self.new_game()
    
    def show_draw(self):
        QMessageBox.information(self, "Ничья", "Игра закончилась в ничью!")
        self.new_game()
    
    def new_game(self):
        self.current_player = 'X'
        self.board = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        self.title_label.setText(f"Ход игрока: {self.current_player}")
        for row in self.buttons:
            for btn in row:
                btn.setText(' ')
                btn.setEnabled(True)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2D2D2D;
                        border: 2px solid #3D3D3D;
                        border-radius: 15px;
                        color: transparent;
                        font-size: 28px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #3D3D3D;
                    }
                """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicTacToe()
    window.show()
    sys.exit(app.exec())