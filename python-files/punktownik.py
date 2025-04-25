import sys
from PyQt5.QtWidgets import (
    QApplication, QLabel, QPushButton, QFileDialog, QMainWindow,
    QGraphicsScene, QGraphicsView, QGraphicsPixmapItem,
    QGraphicsTextItem, QGraphicsItem, QGraphicsEllipseItem, QColorDialog,
    QGraphicsLineItem, QInputDialog, QVBoxLayout, QWidget, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPen, QColor, QFont, QTransform, QImage
from PyQt5.QtCore import Qt, QPointF, QRectF
from reportlab.pdfgen import canvas as pdf_canvas
from PIL import Image
import os

class Punktownik(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punktownik")
        self.setGeometry(100, 100, 1000, 700)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.points = []
        self.point_number = 1

        self.create_toolbar()
        self.bg_pixmap_item = None

    def create_toolbar(self):
        self.toolbar = self.addToolBar("Opcje")

        load_btn = QPushButton("Wczytaj obraz/PDF")
        load_btn.clicked.connect(self.load_background)
        self.toolbar.addWidget(load_btn)

        point_btn = QPushButton("Dodaj punkt")
        point_btn.clicked.connect(self.add_point)
        self.toolbar.addWidget(point_btn)

        text_btn = QPushButton("Dodaj tekst")
        text_btn.clicked.connect(self.add_text)
        self.toolbar.addWidget(text_btn)

        img_btn = QPushButton("Dodaj obrazek")
        img_btn.clicked.connect(self.add_image)
        self.toolbar.addWidget(img_btn)

        export_png_btn = QPushButton("Eksport do PNG")
        export_png_btn.clicked.connect(self.export_png)
        self.toolbar.addWidget(export_png_btn)

        export_pdf_btn = QPushButton("Eksport do PDF")
        export_pdf_btn.clicked.connect(self.export_pdf)
        self.toolbar.addWidget(export_pdf_btn)

    def load_background(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz obraz lub PDF", "", "Obrazy (*.png *.jpg *.jpeg);;PDF (*.pdf)")
        if not file_path:
            return

        if file_path.lower().endswith(".pdf"):
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(file_path)
                images[0].save("temp_bg.png", "PNG")
                file_path = "temp_bg.png"
            except ImportError:
                QMessageBox.warning(self, "Błąd", "Aby wczytać PDF, zainstaluj bibliotekę pdf2image:\npip install pdf2image")
                return

        pixmap = QPixmap(file_path)
        if self.bg_pixmap_item:
            self.scene.removeItem(self.bg_pixmap_item)
        self.bg_pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.bg_pixmap_item)

    def add_point(self):
        if not self.bg_pixmap_item:
            return
        pos = self.view.mapToScene(self.view.viewport().rect().center())
        number, ok = QInputDialog.getText(self, "Numer punktu", "Podaj numer:", text=str(self.point_number))
        if not ok:
            return

        # Strzałka
        arrow = QGraphicsLineItem(0, 0, 30, 0)
        arrow.setPen(QPen(Qt.red, 2))
        arrow.setFlag(QGraphicsItem.ItemIsMovable)
        arrow.setFlag(QGraphicsItem.ItemIsSelectable)
        arrow.setFlag(QGraphicsItem.ItemIsFocusable)
        arrow.setTransformOriginPoint(0, 0)
        arrow.setPos(pos)
        self.scene.addItem(arrow)

        # Tekst z numerem
        text = QGraphicsTextItem(number)
        text.setDefaultTextColor(Qt.white)
        font = QFont("Arial", 10)
        font.setBold(True)
        text.setFont(font)
        text.setPos(pos + QPointF(35, -10))
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsFocusable)
        self.scene.addItem(text)

        self.points.append((arrow, text))
        self.point_number += 1

    def add_text(self):
        if not self.bg_pixmap_item:
            return
        pos = self.view.mapToScene(self.view.viewport().rect().center())
        text, ok = QInputDialog.getText(self, "Dodaj tekst", "Wpisz tekst:")
        if not ok:
            return
        item = QGraphicsTextItem(text)
        item.setDefaultTextColor(Qt.black)
        font = QFont("Arial", 10)
        item.setFont(font)
        item.setPos(pos)
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(item)

    def add_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Dodaj obrazek", "", "Obrazy (*.png *.jpg *.jpeg)")
        if not file_path:
            return
        pixmap = QPixmap(file_path)
        item = QGraphicsPixmapItem(pixmap)
        item.setPos(self.view.mapToScene(self.view.viewport().rect().center()))
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(item)

    def export_png(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz jako PNG", "", "PNG (*.png)")
        if not file_path:
            return
        image = QImage(self.view.viewport().size(), QImage.Format_ARGB32)
        painter = QPainter(image)
        self.view.render(painter)
        painter.end()
        image.save(file_path)

    def export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz jako PDF", "", "PDF (*.pdf)")
        if not file_path:
            return
        image = QImage(self.view.viewport().size(), QImage.Format_ARGB32)
        painter = QPainter(image)
        self.view.render(painter)
        painter.end()
        image.save("temp_export.png")

        img = Image.open("temp_export.png")
        img = img.convert("RGB")
        img.save(file_path, "PDF", resolution=100.0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Punktownik()
    window.show()
    sys.exit(app.exec_())
