import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QProgressBar, QPushButton, QMenuBar, QAction, 
                             QFileDialog, QMessageBox, QTabWidget, QGroupBox, QComboBox,
                             QListWidget, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont

class MTKFlashTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MTK Flash Tool - MT6261/MT6260/MT630")
        self.setGeometry(100, 100, 900, 700)
        
        # Apply Fusion style with custom enhancements
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #374151;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                text-align: center;
                height: 24px;
                background: white;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
            QTableWidget {
                border: 1px solid #d1d5db;
                background-color: white;
            }
            QListWidget {
                border: 1px solid #d1d5db;
                background-color: white;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                border: 1px solid #d1d5db;
                background-color: #f9fafb;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
            QPushButton:disabled {
                background-color: #f3f4f6;
                color: #9ca3af;
            }
        """)
        
        self.init_ui()
        self.create_menu_bar()
        
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Flash Tab
        flash_tab = QWidget()
        tabs.addTab(flash_tab, "Flash Tool")
        self.setup_flash_tab(flash_tab)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def setup_flash_tab(self, tab):
        layout = QVBoxLayout(tab)
        
        # Device selection
        device_group = QGroupBox("Device Configuration")
        device_layout = QHBoxLayout()
        
        device_layout.addWidget(QLabel("Device Type:"))
        self.device_combo = QComboBox()
        self.device_combo.addItems(["MT6261", "MT6260", "MT630"])
        device_layout.addWidget(self.device_combo)
        
        device_layout.addWidget(QLabel("Memory Type:"))
        self.mem_combo = QComboBox()
        self.mem_combo.addItems(["NOR", "eMMC"])
        device_layout.addWidget(self.mem_combo)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # Download Agent
        da_group = QGroupBox("Download Agent")
        da_layout = QHBoxLayout()
        
        self.da_path = QLabel("MTK_AllInOne_DA.bin")
        self.da_path.setStyleSheet("border: 1px solid #d1d5db; padding: 5px; background: white;")
        da_layout.addWidget(self.da_path, stretch=1)
        
        browse_da_btn = QPushButton("Browse...")
        browse_da_btn.clicked.connect(self.select_da_file)
        da_layout.addWidget(browse_da_btn)
        
        da_group.setLayout(da_layout)
        layout.addWidget(da_group)
        
        # Scatter file selection
        scatter_group = QGroupBox("Scatter File Configuration")
        scatter_layout = QHBoxLayout()
        
        self.scatter_path = QLabel("No scatter file selected")
        self.scatter_path.setStyleSheet("border: 1px solid #d1d5db; padding: 5px; background: white;")
        scatter_layout.addWidget(self.scatter_path, stretch=1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.select_scatter_file)
        scatter_layout.addWidget(browse_btn)
        
        scatter_group.setLayout(scatter_layout)
        layout.addWidget(scatter_group)
        
        # Region table
        region_group = QGroupBox("Memory Regions")
        region_layout = QVBoxLayout()
        
        self.region_table = QTableWidget()
        self.region_table.setColumnCount(5)
        self.region_table.setHorizontalHeaderLabels(["Name", "Region Address", "Begin Address", "End Address", "Location"])
        self.region_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.region_table.setEditTriggers(QTableWidget.NoEditTriggers)
        region_layout.addWidget(self.region_table)
        
        region_group.setLayout(region_layout)
        layout.addWidget(region_group)
        
        # Operation list
        op_group = QGroupBox("Operations")
        op_layout = QVBoxLayout()
        
        self.op_list = QListWidget()
        self.op_list.addItems(["Download", "Readback"])
        self.op_list.setCurrentRow(0)
        op_layout.addWidget(self.op_list)
        
        op_group.setLayout(op_layout)
        layout.addWidget(op_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Idle")
        layout.addWidget(self.progress_bar)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("background-color: #10b981; color: white; font-weight: bold;")
        self.start_btn.clicked.connect(self.start_operation)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_operation)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_scatter = QAction("Open Scatter", self)
        open_scatter.triggered.connect(self.select_scatter_file)
        file_menu.addAction(open_scatter)
        
        open_da = QAction("Open Download Agent", self)
        open_da.triggered.connect(self.select_da_file)
        file_menu.addAction(open_da)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        detect_action = QAction("Detect Device", self)
        detect_action.triggered.connect(self.detect_device)
        tools_menu.addAction(detect_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def select_scatter_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Scatter File", "", "Config Files (*.cfg)")
        if file_name:
            self.scatter_path.setText(file_name)
            self.parse_scatter_file(file_name)
            
    def select_da_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Download Agent", "", "Bin Files (*.bin)")
        if file_name:
            self.da_path.setText(file_name)
            
    def parse_scatter_file(self, file_path):
        try:
            # Simulate parsing a scatter file
            regions = [
                ["ARM_BL", "0x70006600", "0x70006600", "0x700087E3", "boot_region"],
                ["ARM_EXIT_BL", "0X10003400", "0X10003400", "0X1000BC8F", "boot_region"],
                ["PRIMARY_MAUI", "0X10010000", "0X10010000", "0X1014FB23", "main_region"],
                ["VIVA", "0X1014FF24", "0X1014FF24", "0X1045B167", "main_region"],
                ["OTP", "0x00000000", "0x00000000", "0x00000FFF", "otp_region"]
            ]
            
            self.region_table.setRowCount(len(regions))
            for row, region in enumerate(regions):
                for col, data in enumerate(region):
                    item = QTableWidgetItem(data)
                    self.region_table.setItem(row, col, item)
                    
            self.statusBar().showMessage(f"Loaded scatter file: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse scatter file:\n{str(e)}")
            
    def detect_device(self):
        self.statusBar().showMessage("Detecting device...")
        QTimer.singleShot(2000, lambda: self.statusBar().showMessage("Device detected: MT6261"))
        
    def start_operation(self):
        if self.scatter_path.text() == "No scatter file selected":
            QMessageBox.warning(self, "Error", "Please select a scatter file first!")
            return
            
        operation = self.op_list.currentItem().text()
        device = self.device_combo.currentText()
        mem_type = self.mem_combo.currentText()
        
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(f"Starting {operation}...")
        self.statusBar().showMessage(f"{operation} {device} ({mem_type}) started")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Simulate operation
        self.op_timer = QTimer(self)
        self.op_timer.timeout.connect(lambda: self.update_progress(operation))
        self.op_timer.start(100)
        
    def update_progress(self, operation):
        current = self.progress_bar.value()
        if current >= 100:
            self.op_timer.stop()
            self.progress_bar.setFormat(f"{operation} completed!")
            self.statusBar().showMessage(f"{operation} completed successfully")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            return
            
        increment = min(2, 100 - current)
        self.progress_bar.setValue(current + increment)
        self.progress_bar.setFormat(f"{operation}... {current + increment}%")
        
    def stop_operation(self):
        self.op_timer.stop()
        self.progress_bar.setFormat("Operation stopped")
        self.statusBar().showMessage("Operation stopped by user")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def show_about(self):
        about_text = """
        <b>MTK Flash Tool</b><br><br>
        Version 1.0<br>
        Supports MT6261, MT6260, MT630<br>
        Download/Readback operations<br>
        NOR/eMMC memory support<br><br>
        © 2023 MTK Tools
        """
        QMessageBox.about(self, "About", about_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set palette for consistent look
    palette = app.palette()
    palette.setColor(palette.Window, Qt.white)
    palette.setColor(palette.WindowText, Qt.black)
    app.setPalette(palette)
    
    window = MTKFlashTool()
    window.show()
    sys.exit(app.exec_())