
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QVBoxLayout

# EGR OFF adres listesi (C34'ten gelen)
addresses = [0x1C5EC9, 0x1C5ECA, 0x1C5ECB, 0x1C5ECC, 0x1C5ECD]

class EGRTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("by SistemOtoElektronik - C34 EGR Tool")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.check_button = QPushButton("EGR Durumunu Kontrol Et")
        self.check_button.clicked.connect(self.check_egr)
        layout.addWidget(self.check_button)

        self.patch_button = QPushButton("EGR OFF Yap")
        self.patch_button.clicked.connect(self.patch_egr)
        layout.addWidget(self.patch_button)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "BIN Dosyası Seç", "", "BIN Files (*.bin)")
        return file_path if file_path else None

    def check_egr(self):
        path = self.select_file()
        if not path:
            return
        with open(path, "rb") as f:
            data = bytearray(f.read())
        for addr in addresses:
            if data[addr] != 0x00:
                QMessageBox.information(self, "Sonuç", "EGR AÇIK!")
                return
        QMessageBox.information(self, "Sonuç", "EGR OFF yapılmış.")

    def patch_egr(self):
        path = self.select_file()
        if not path:
            return
        with open(path, "rb") as f:
            data = bytearray(f.read())
        for addr in addresses:
            data[addr] = 0x00
        new_path = path.replace(".bin", "_EGR_OFF.bin")
        with open(new_path, "wb") as f:
            f.write(data)
        QMessageBox.information(self, "Sonuç", f"EGR OFF tamamlandı:\n{new_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EGRTool()
    window.show()
    sys.exit(app.exec_())
