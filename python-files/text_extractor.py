import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QScrollArea, QTextEdit, QMessageBox)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QImage
from PyQt6.QtCore import Qt, QRect, QPoint
import pytesseract
from PIL import Image
import numpy as np

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.image = None
        self.drawing = False
        self.last_point = None
        self.selection_rect = QRect()
        self.selection_start = QPoint()
        self.selection_end = QPoint()
        self.setMouseTracking(True)
        
    def set_image(self, image_path):
        self.image = QPixmap(image_path)
        self.update()
        
    def paintEvent(self, event):
        if self.image:
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.image)
            
            # Draw selection rectangle
            if not self.selection_rect.isNull():
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.drawRect(self.selection_rect)
                
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.selection_start = event.pos()
            self.selection_end = event.pos()
            self.selection_rect = QRect()
            
    def mouseMoveEvent(self, event):
        if self.drawing:
            self.selection_end = event.pos()
            self.selection_rect = QRect(self.selection_start, self.selection_end).normalized()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.selection_rect = QRect(self.selection_start, self.selection_end).normalized()
            self.update()
            
    def get_selection(self):
        if not self.selection_rect.isNull() and self.image:
            return self.selection_rect
        return None

class TextExtractorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Extractor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel for image viewer
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Image viewer
        self.image_viewer = ImageViewer()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_viewer)
        scroll_area.setWidgetResizable(True)
        left_layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open Image")
        self.extract_button = QPushButton("Extract Text")
        self.clear_button = QPushButton("Clear Selection")
        
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.extract_button)
        button_layout.addWidget(self.clear_button)
        left_layout.addLayout(button_layout)
        
        # Right panel for extracted text
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        right_layout.addWidget(QLabel("Extracted Text:"))
        right_layout.addWidget(self.text_output)
        
        # Add panels to main layout
        layout.addWidget(left_panel, 2)
        layout.addWidget(right_panel, 1)
        
        # Connect signals
        self.open_button.clicked.connect(self.open_image)
        self.extract_button.clicked.connect(self.extract_text)
        self.clear_button.clicked.connect(self.clear_selection)
        
        self.current_image_path = None
        
    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_name:
            self.current_image_path = file_name
            self.image_viewer.set_image(file_name)
            self.text_output.clear()
            
    def extract_text(self):
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please open an image first!")
            return
            
        selection = self.image_viewer.get_selection()
        if not selection:
            QMessageBox.warning(self, "Warning", "Please select an area first!")
            return
            
        try:
            # Convert QPixmap to PIL Image
            image = Image.open(self.current_image_path)
            # Crop the selected area
            cropped = image.crop((
                selection.x(),
                selection.y(),
                selection.x() + selection.width(),
                selection.y() + selection.height()
            ))
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(cropped)
            self.text_output.setText(text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error extracting text: {str(e)}")
            
    def clear_selection(self):
        self.image_viewer.selection_rect = QRect()
        self.image_viewer.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextExtractorApp()
    window.show()
    sys.exit(app.exec()) 