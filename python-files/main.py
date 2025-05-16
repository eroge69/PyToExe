# main.py
import sys
from PyQt5.QtWidgets import QApplication
from login import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Принудительный стиль Fusion
    app.setStyle("Fusion")

    # Если есть .qss файл — применить его
    try:
        with open("resources/style.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass  # Можно без ошибки, если файла нет

    window = LoginWindow()
    window.show()


    sys.exit(app.exec_())