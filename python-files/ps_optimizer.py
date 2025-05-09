
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMainWindow, QListWidget, QTextEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import sys
import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PS Optimizer")
        self.setGeometry(100, 100, 800, 600)

        self.tweak_list = QListWidget()
        self.tweak_list.addItem("Fast Boot")
        self.tweak_list.addItem("RAM Optimizer")
        self.tweak_list.addItem("Explorer SpeedUp")
        self.tweak_list.currentItemChanged.connect(self.show_tweak_description)

        self.description = QTextEdit()
        self.description.setReadOnly(True)

        self.apply_button = QPushButton("Tweak anwenden")
        self.apply_button.clicked.connect(self.apply_tweak)

        layout = QVBoxLayout()
        layout.addWidget(self.tweak_list)
        layout.addWidget(self.description)
        layout.addWidget(self.apply_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_tweak_description(self, item):
        if not item:
            return
        name = item.text()
        desc = {
            "Fast Boot": "Deaktiviert unnötige Autostartprogramme.",
            "RAM Optimizer": "Leert den Standby-RAM für mehr freien Speicher.",
            "Explorer SpeedUp": "Entfernt Animationen im Explorer für schnelleren Zugriff."
        }
        self.description.setText(desc.get(name, ""))

    def apply_tweak(self):
        item = self.tweak_list.currentItem()
        if not item:
            return
        tweak = item.text()
        if tweak == "Fast Boot":
            subprocess.run("powershell -Command "Get-CimInstance Win32_StartupCommand | Remove-CimInstance"", shell=True)
        elif tweak == "RAM Optimizer":
            subprocess.run("powershell -Command "Clear-MemoryCache"", shell=True)
        elif tweak == "Explorer SpeedUp":
            subprocess.run("powershell -Command "Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'MenuShowDelay' -Value '0'"", shell=True)
        print(f"Tweak angewendet: {tweak}")

def show_splash_and_main():
    splash = QSplashScreen()
    splash.showMessage("Lade PS Optimizer...", alignment=0x84)
    splash.show()

    def start_main():
        window = MainWindow()
        window.show()
        splash.finish(window)

    QTimer.singleShot(2000, start_main)

app = QApplication(sys.argv)
show_splash_and_main()
sys.exit(app.exec_())
