# Copyright (c)  (https://discord.gg/pQUFjaJ2EN)
# See the file 'LICENSE' for copying permission
# ----------------------------------------------------------------------------------------------------------------------------------------------------------|
# EN: 
#     - Do not touch or modify the code below. If there is an error, please contact the owner, but under no circumstances should you touch the code.
#     - Do not resell this tool, do not credit it to yours.
# FR: 
#     - Ne pas toucher ni modifier le code ci-dessous. En cas d'erreur, veuillez contacter le propriétaire, mais en aucun cas vous ne devez toucher au code.
#     - Ne revendez pas ce tool, ne le créditez pas au vôtre.

import sys
import os
import time
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton,
                             QStackedWidget, QMessageBox, QFrame, QTextEdit, QProgressBar)
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt

class CustomGUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zyre's Professional Roblox 2FA & PassBrute GUI")
        self.setFixedSize(1200, 700)

        self.accent_color = "#A855F7"  

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(15, 15, 23))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        sidebarLayout = QVBoxLayout()
        sidebarLayout.setContentsMargins(0, 0, 0, 0)

        self.twoFABtn = QPushButton("2FA Bypass")
        self.passBtn = QPushButton("PassBrute")

        for btn in [self.twoFABtn, self.passBtn]:
            btn.setFixedHeight(60)
            btn.setFont(QFont("Arial", 16, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)

        sidebarLayout.addWidget(self.twoFABtn)
        sidebarLayout.addWidget(self.passBtn)
        sidebarLayout.addStretch()

        sidebar = QFrame()
        sidebar.setLayout(sidebarLayout)
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("background-color: #0f0f17; padding: 10px; border-right: 2px solid #A855F7;")

        self.mainStack = QStackedWidget()

        
        twoFAPage = self.create_2fa_page()
        self.mainStack.addWidget(twoFAPage)

        
        passPage = self.create_pass_brute_page()
        self.mainStack.addWidget(passPage)

        mainLayout.addWidget(sidebar)
        mainLayout.addWidget(self.mainStack)

        self.setLayout(mainLayout)

        
        self.twoFABtn.clicked.connect(lambda: self.switch_page(0))
        self.passBtn.clicked.connect(lambda: self.switch_page(1))

        self.update_tab_styles(0)  

    def update_tab_styles(self, active_index):
        buttons = [self.twoFABtn, self.passBtn]
        for i, button in enumerate(buttons):
            if i == active_index:
                button.setStyleSheet(f"background-color: {self.accent_color}; color: white; border-radius: 10px; padding: 15px; font-size: 20px;")
            else:
                button.setStyleSheet("color: white; background-color: #2d2d3d; border-radius: 10px; padding: 15px; font-size: 20px;")

    def switch_page(self, index):
        self.mainStack.setCurrentIndex(index)
        self.update_tab_styles(index)

    def create_2fa_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        page.setStyleSheet("background-color: #1a1a2e;")

        self.use_proxies_2fa = QCheckBox("Use Proxies[Optional]")
        self.use_v2_2fa = QCheckBox("Use V2 Algorithm [BETA]")

        for checkbox in [self.use_proxies_2fa, self.use_v2_2fa]:
            checkbox.setStyleSheet("color: white; font-size: 28px; padding: 10px;")
            layout.addWidget(checkbox)

        self.start2FABtn = QPushButton("Start 2FA Bypass")
        self.start2FABtn.setStyleSheet("background-color: #A855F7; color: white; padding: 15px; font-size: 24px; border-radius: 10px;")
        self.start2FABtn.clicked.connect(self.run_2fa_bypass_script)
        layout.addWidget(self.start2FABtn)

        return page

    def run_2fa_bypass_script(self):
        script_folder = os.path.join(os.getcwd(), 'programs')
        script_name = '2fa_runV2.py' if self.use_v2_2fa.isChecked() else '2fa_run.py'
        script_path = os.path.join(script_folder, script_name)
        if os.path.exists(script_path):
            subprocess.Popen(['python', script_path])
        else:
            QMessageBox.warning(self, "Error", f"Script not found: {script_path}")

    def create_pass_brute_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        page.setStyleSheet("background-color: #1a1a2e;")

        self.use_proxies_pass = QCheckBox("Use Proxies[Optional]")
        self.use_v2_pass = QCheckBox("Use V2 Algorithm [BETA]")

        for checkbox in [self.use_proxies_pass, self.use_v2_pass]:
            checkbox.setStyleSheet("color: white; font-size: 28px; padding: 10px;")
            layout.addWidget(checkbox)

        self.startPassBtn = QPushButton("Start PassBrute")
        self.startPassBtn.setStyleSheet("background-color: #A855F7; color: white; padding: 15px; font-size: 24px; border-radius: 10px;")
        self.startPassBtn.clicked.connect(self.run_pass_brute_script)
        layout.addWidget(self.startPassBtn)

        return page

    def run_pass_brute_script(self):
        script_folder = os.path.join(os.getcwd(), 'programs')
        script_name = 'pass_runV2.py' if self.use_v2_pass.isChecked() else 'pass_run.py'
        script_path = os.path.join(script_folder, script_name)
        if os.path.exists(script_path):
            subprocess.Popen(['python', script_path])
        else:
            QMessageBox.warning(self, "Error", f"Script not found: {script_path}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = CustomGUI()
    gui.show()
    sys.exit(app.exec_())