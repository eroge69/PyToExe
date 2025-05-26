# 🔧 ADIM 1: GEREKLİ KÜTÜPHANELER
# Cursor terminal penceresinde:
# Aşağıdaki komutu çalıştır ve gerekli paketi yükle


# ✅ ADIM 2: PYQT5 ARAYÜZÜ – DOSYA SEÇ + HEX KARŞILAŞTIRMA

# Cursor'da yeni bir Python dosyası oluştur (örneğin: app.py)
# Aşağıdaki kodu dosyaya yapıştır:

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QTextEdit, QVBoxLayout, QFileDialog
)

class HexComparer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hex Karşılaştırıcı")
        self.setGeometry(100, 100, 700, 600)

        self.ori_path = ""
        self.mod_path = ""

        # UI
        self.ori_btn = QPushButton("Orijinal Dosya Seç")
        self.ori_btn.clicked.connect(self.load_ori)

        self.mod_btn = QPushButton("Modifiye Dosya Seç")
        self.mod_btn.clicked.connect(self.load_mod)

        self.compare_btn = QPushButton("Karşılaştır")
        self.compare_btn.clicked.connect(self.compare_files)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.ori_btn)
        layout.addWidget(self.mod_btn)
        layout.addWidget(self.compare_btn)
        layout.addWidget(QLabel("Karşılaştırma Raporu:"))
        layout.addWidget(self.result_box)
        self.setLayout(layout)

    def load_ori(self):
        path, _ = QFileDialog.getOpenFileName(self, "Orijinal Dosya Seç")
        if path:
            self.ori_path = path
            self.ori_btn.setText(f"Orijinal: {path.split('/')[-1]}")

    def load_mod(self):
        path, _ = QFileDialog.getOpenFileName(self, "Modifiye Dosya Seç")
        if path:
            self.mod_path = path
            self.mod_btn.setText(f"Modifiye: {path.split('/')[-1]}")

    def compare_files(self):
        if not self.ori_path or not self.mod_path:
            self.result_box.setText("Lütfen iki dosya da seçin.")
            return

        with open(self.ori_path, "rb") as f:
            ori = f.read()
        with open(self.mod_path, "rb") as f:
            mod = f.read()

        length = min(len(ori), len(mod))
        diff_bytes = []
        for i in range(length):
            if ori[i] != mod[i]:
                diff_bytes.append(i)

        diff_blocks = []
        block = []
        for i in diff_bytes:
            if not block or i == block[-1] + 1:
                block.append(i)
            else:
                diff_blocks.append(block)
                block = [i]
        if block:
            diff_blocks.append(block)

        report = []
        report.append("=== HEX KARŞILAŞTIRMA RAPORU ===\n")
        report.append(f"🔢 Toplam Farklı Byte Sayısı: {len(diff_bytes)}\n")
        report.append(f"🧩 Değişen Blok Sayısı: {len(diff_blocks)}\n")

        map_blocks = []
        switch_blocks = []

        for i, b in enumerate(diff_blocks):
            start = hex(b[0])
            end = hex(b[-1])
            size = len(b)
            block_info = f"📦 Blok {i+1}: {start} – {end} ({size} byte)"
            if size >= 32:
                map_blocks.append(block_info + "\n   → Map olabilir")
            else:
                switch_blocks.append(block_info + "\n   → Tekil değişim / switch olabilir")

        report.append("\n=== MAP OLABİLECEK BLOKLAR ===")
        if map_blocks:
            report.extend(map_blocks)
        else:
            report.append("Yok")

        report.append("\n=== TEKİL DEĞİŞİM / SWITCH OLABİLECEK BLOKLAR ===")
        if switch_blocks:
            report.extend(switch_blocks)
        else:
            report.append("Yok")

        
        self.result_box.setText("\n".join(report))


# �� Uygulamayı başlat
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HexComparer()
    window.show()
    sys.exit(app.exec_())