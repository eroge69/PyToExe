import os
import re
import cv2
import shutil
import numpy as np
import pdfplumber
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QProgressBar, QDialog, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from paddleocr import PaddleOCR

class PdfWorker(QThread):
    file_processed = pyqtSignal(str, list, str)
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()
    log_data = pyqtSignal(str)

    def __init__(self, folder_path, top_percentage=None):
        super().__init__()
        self.folder_path = folder_path
        self.top_percentage = top_percentage
        self.running = True
        self.ocr = PaddleOCR(use_angle_cls=True, lang="en")
        self.all_case_numbers = []  # Store all extracted case numbers

    def run(self):
        pdf_files = []
        for root, _, files in os.walk(self.folder_path):
            for f in files:
                if f.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, f))
        
        total = len(pdf_files)
        for i, pdf_path in enumerate(pdf_files):
            if not self.running:
                break
            self.process_file(pdf_path)
            self.progress_updated.emit(int((i+1)/total*100))
        
        # Emit all case numbers for logging
        self.log_data.emit("\n".join(self.all_case_numbers))
        self.finished.emit()

    def process_file(self, pdf_path):
        try:
            case_numbers = self.extract_case_numbers(pdf_path)
            self.all_case_numbers.extend(case_numbers)
            status = "success" if case_numbers else "warning"
            
            if case_numbers:
                filings_dir = os.path.join(os.path.dirname(pdf_path), "filings")
                os.makedirs(filings_dir, exist_ok=True)
                unique_case_numbers = list(dict.fromkeys(case_numbers))
                for num in unique_case_numbers:
                    safe_num = re.sub(r'[\\/*?:"<>|]', "_", num)
                    dest_path = os.path.join(filings_dir, f"{safe_num}.pdf")
                    if not os.path.exists(dest_path):
                        shutil.copy2(pdf_path, dest_path)
        except Exception as e:
            case_numbers = [str(e)]
            status = "error"
        
        self.file_processed.emit(pdf_path, case_numbers, status)

    def extract_case_numbers(self, pdf_path):
        case_numbers = []
        with pdfplumber.open(pdf_path) as pdf:
            # Read ALL pages for full processing, first page only for top section
            pages = pdf.pages if self.top_percentage is None else [pdf.pages[0]]
            
            for page in pages:
                # Text extraction
                text = page.extract_text() or ""
                found_numbers = re.findall(r"(?:WMS|ICR)[-/]\w+/\d+/\d+", text)
                case_numbers.extend(found_numbers)
                
                # OCR fallback if no text found
                if not found_numbers:
                    img = cv2.cvtColor(np.array(page.to_image(resolution=350).original), cv2.COLOR_RGB2BGR)
                    img = self.preprocess_image(img)
                    if self.top_percentage is not None:
                        img = img[:int(img.shape[0]*(self.top_percentage/100)), :]
                    results = self.ocr.ocr(img, cls=True)
                    text = " ".join(res[1][0] for line in results for res in line if res[1])
                    found_numbers = re.findall(r"(?:WMS|ICR)[-/]\w+/\d+/\d+", text)
                    case_numbers.extend(found_numbers)
        
        return list(dict.fromkeys(case_numbers))

    def preprocess_image(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        return cv2.filter2D(thresh, -1, kernel)

    def stop(self):
        self.running = False

class LogDialog(QDialog):
    def __init__(self, log_text):
        super().__init__()
        self.setWindowTitle("Extracted Case Numbers")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(log_text)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Wafaqi Mohtasib File Processor")
        self.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # Header with logo
        header = QHBoxLayout()
        self.logo = QLabel()
        if os.path.exists("logo.png"):
            self.logo.setPixmap(QPixmap("logo.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(self.logo)
        
        titles = QVBoxLayout()
        title = QLabel("WAFAQI MOHTASIB")
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("FILE RENAMER")
        subtitle.setFont(QFont('Arial', 14, QFont.Bold))
        subtitle.setAlignment(Qt.AlignCenter)
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch()
        layout.addLayout(header)

        # Separator line
        sep = QLabel()
        sep.setFrameShape(QLabel.HLine)
        sep.setStyleSheet("background-color: #003366; height: 2px;")
        layout.addWidget(sep)

        # Input section
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Source Folder:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select folder containing PDF files...")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_folder)
        input_layout.addWidget(self.path_input)
        input_layout.addWidget(browse_btn)
        layout.addLayout(input_layout)

        # Processing buttons
        btn_layout = QHBoxLayout()
        self.top_btn = QPushButton("Quick Process (Top Section)")
        self.full_btn = QPushButton("Complete Process (Full Document)")
        self.stop_btn = QPushButton("Stop")
        self.log_btn = QPushButton("Log")
        self.log_btn.setEnabled(False)
        
        self.top_btn.clicked.connect(lambda: self.start_processing(50))
        self.full_btn.clicked.connect(lambda: self.start_processing(None))
        self.stop_btn.clicked.connect(self.stop_processing)
        self.log_btn.clicked.connect(self.show_log)
        
        btn_layout.addWidget(self.top_btn)
        btn_layout.addWidget(self.full_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.log_btn)
        layout.addLayout(btn_layout)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)

        # Results table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["File Name", "Case Numbers", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(2, 100)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.table)

        # Footer
        footer = QLabel("Developed by: Ghulam Mujtaba (Director IT)")
        footer.setAlignment(Qt.AlignRight)
        layout.addWidget(footer)

        self.setLayout(layout)
        self.path_input.textChanged.connect(self.update_buttons)
        self.update_buttons()

        # Style sheet
        self.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:disabled { background-color: #aaa; }
            QTableWidget {
                font-size: 13px;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #003366;
                color: white;
                padding: 8px;
            }
        """)

    def browse_folder(self):
        if folder := QFileDialog.getExistingDirectory(self, "Select Folder"):
            self.path_input.setText(folder)

    def update_buttons(self):
        enabled = os.path.isdir(self.path_input.text())
        self.top_btn.setEnabled(enabled)
        self.full_btn.setEnabled(enabled)

    def start_processing(self, top_percentage):
        self.table.setRowCount(0)
        self.progress.setValue(0)
        self.top_btn.setEnabled(False)
        self.full_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_btn.setEnabled(False)
        
        self.worker = PdfWorker(self.path_input.text(), top_percentage)
        self.worker.file_processed.connect(self.update_table)
        self.worker.progress_updated.connect(self.progress.setValue)
        self.worker.finished.connect(self.processing_finished)
        self.worker.log_data.connect(self.set_log_data)
        self.worker.start()

    def stop_processing(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
        self.stop_btn.setEnabled(False)
        self.top_btn.setEnabled(True)
        self.full_btn.setEnabled(True)

    def set_log_data(self, log_text):
        self.log_text = log_text
        self.log_btn.setEnabled(True)

    def show_log(self):
        if hasattr(self, 'log_text'):
            log_dialog = LogDialog(self.log_text)
            log_dialog.exec_()

    def update_table(self, path, case_numbers, status):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        file_item = QTableWidgetItem(os.path.basename(path))
        file_item.setFlags(file_item.flags() & ~Qt.ItemIsEditable)
        
        nums_item = QTableWidgetItem(", ".join(case_numbers) if isinstance(case_numbers, list) else "")
        nums_item.setFlags(nums_item.flags() & ~Qt.ItemIsEditable)
        
        status_item = QTableWidgetItem()
        if status == "success":
            status_item.setText("Done")
            status_item.setBackground(Qt.green)
            status_item.setForeground(Qt.white)
        elif status == "warning":
            status_item.setText("No Cases")
            status_item.setBackground(Qt.yellow)
        else:
            status_item.setText("Error")
            status_item.setBackground(Qt.red)
            status_item.setForeground(Qt.white)
        status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
        
        self.table.setItem(row, 0, file_item)
        self.table.setItem(row, 1, nums_item)
        self.table.setItem(row, 2, status_item)
        self.table.scrollToBottom()

    def processing_finished(self):
        self.stop_btn.setEnabled(False)
        self.top_btn.setEnabled(True)
        self.full_btn.setEnabled(True)
        QMessageBox.information(self, "Complete", "All files processed successfully")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
