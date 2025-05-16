import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                                 QFileDialog, QVBoxLayout, QWidget, QHBoxLayout,
                                 QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                                 QGraphicsEllipseItem, QGraphicsSimpleTextItem, QGraphicsItem,
                                 QSlider, QLineEdit)
from PySide6.QtGui import QPixmap, QPen, QColor
from PySide6.QtCore import Qt, QPointF
import ezdxf
import os
import cv2
import numpy as np

class PointItem(QGraphicsEllipseItem):
    def __init__(self, x, y, index, radius=4):
        super().__init__(-radius, -radius, radius*2, radius*2)
        self.setBrush(QColor("red"))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPos(x, y)

        self.label = QGraphicsSimpleTextItem(str(index), self)
        self.label.setPos(-radius, -radius - 10)

class PatternEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartPattern AI - Offline Editor")
        self.setGeometry(100, 100, 1000, 700)

        self.image_label = QLabel("No Image Loaded")
        self.image_label.setAlignment(Qt.AlignCenter)

        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.pixmap_item = None

        self.load_btn = QPushButton("Open Image")
        self.load_btn.clicked.connect(self.open_image)

        self.add_point_btn = QPushButton("Add Point")
        self.add_point_btn.clicked.connect(self.enable_add_point)

        self.delete_point_btn = QPushButton("Delete Selected Point(s)")
        self.delete_point_btn.clicked.connect(self.delete_selected_point)

        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_action)

        self.detect_edges_btn = QPushButton("Auto Detect Contour")
        self.detect_edges_btn.clicked.connect(self.auto_detect_contour)

        self.export_dxf_btn = QPushButton("Export DXF")
        self.export_dxf_btn.clicked.connect(self.export_dxf)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Part name (e.g. Sleeve)")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(50)
        self.slider.setValue(10)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.add_point_btn)
        btn_layout.addWidget(self.delete_point_btn)
        btn_layout.addWidget(self.undo_btn)
        btn_layout.addWidget(self.detect_edges_btn)
        btn_layout.addWidget(self.export_dxf_btn)

        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Point Density:"))
        control_layout.addWidget(self.slider)
        control_layout.addWidget(QLabel("Part Name:"))
        control_layout.addWidget(self.name_input)

        layout = QVBoxLayout()
        layout.addWidget(self.graphics_view)
        layout.addLayout(control_layout)
        layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.points = []
        self.history = []
        self.adding_point = False
        self.image_path = None

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.image_path = path
            pixmap = QPixmap(path)
            self.scene.clear()
            self.points.clear()
            self.history.clear()
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmap_item)
            self.graphics_view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def enable_add_point(self):
        self.adding_point = True
        self.graphics_view.viewport().setCursor(Qt.CrossCursor)
        self.graphics_view.mousePressEvent = self.add_point

    def add_point(self, event):
        if self.adding_point and event.button() == Qt.LeftButton:
            pos = self.graphics_view.mapToScene(event.pos())
            index = len(self.points) + 1
            point = PointItem(pos.x(), pos.y(), index)
            self.scene.addItem(point)
            self.points.append(point)
            self.history.append(("add", point))

    def delete_selected_point(self):
        selected = [p for p in self.points if p.isSelected()]
        for point in selected:
            self.scene.removeItem(point)
            self.points.remove(point)
            self.history.append(("delete", point))

    def undo_action(self):
        if not self.history:
            return
        action, point = self.history.pop()
        if action == "add":
            self.scene.removeItem(point)
            if point in self.points:
                self.points.remove(point)
        elif action == "delete":
            self.scene.addItem(point)
            self.points.append(point)

    def auto_detect_contour(self):
        if not self.image_path:
            return
        image = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        _, thresh = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        self.points.clear()
        max_points = self.slider.value()

        if contours:
            contour = contours[0]  # largest
            sampled = contour[::max(1, len(contour)//max_points)]
            for pt in sampled:
                x, y = pt[0]
                point = PointItem(x, y, len(self.points) + 1)
                self.scene.addItem(point)
                self.points.append(point)
                self.history.append(("add", point))

    def export_dxf(self):
        doc = ezdxf.new()
        msp = doc.modelspace()
        part_name = self.name_input.text().strip() or "Pattern"

        if len(self.points) > 1:
            coords = [(p.scenePos().x(), -p.scenePos().y()) for p in self.points]
            coords.append(coords[0])  # Close path
            msp.add_lwpolyline(coords, close=True)
            msp.add_text(part_name, dxfattribs={"height": 10}).set_pos(coords[0])

        filename, _ = QFileDialog.getSaveFileName(self, "Save DXF", f"{part_name}.dxf", "DXF Files (*.dxf)")
        if filename:
            doc.saveas(filename)
            print(f"DXF saved to: {filename}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PatternEditor()
    window.show()
    sys.exit(app.exec())
