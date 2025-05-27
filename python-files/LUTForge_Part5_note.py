import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

class LUTForge(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LUTForge - Color Grading AI")
        self.setGeometry(200, 200, 800, 600)

        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)

        self.filter_button = QPushButton("Apply Fake Color Grading")
        self.filter_button.clicked.connect(self.apply_filter)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.load_button)
        layout.addWidget(self.filter_button)
        self.setLayout(layout)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.image = cv2.imread(path)
            self.show_image(self.image)

    def apply_filter(self):
        if hasattr(self, 'image'):
            graded = cv2.convertScaleAbs(self.image, alpha=1.3, beta=20)
            self.show_image(graded)

    def show_image(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio
        ))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LUTForge()
    win.show()
    sys.exit(app.exec())
