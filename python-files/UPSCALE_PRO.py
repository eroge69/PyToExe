# Trigger build
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout,
    QHBoxLayout, QMessageBox, QProgressBar, QComboBox, QGroupBox, QListWidget,
    QLineEdit, QSizePolicy, QScrollArea, QCheckBox
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QImage, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QMimeData
from PIL import Image
import io
import cv2
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from gfpgan import GFPGANer
import torch

class UpscaleWorker(QThread):
    progress_updated = pyqtSignal(int)
    task_completed = pyqtSignal(str, str)  # input_path, output_path
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path, output_dir, scale_factor, device_type, output_format, enhance_faces):
        super().__init__()
        self.file_path = file_path
        self.output_dir = output_dir
        self.scale_factor = scale_factor
        self.device_type = device_type
        self.output_format = output_format
        self.enhance_faces = enhance_faces
        self.cancel_requested = False

        self.device = torch.device(self.device_type)

    def run(self):
        try:
            # Initialize upscaler
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=self.scale_factor)
            model_path = f'./models/RealESRGAN_x{self.scale_factor}.pth'
            
            if not os.path.exists(model_path):
                self.error_occurred.emit(f"Model file not found: {model_path}")
                return

            upsampler = RealESRGANer(
                scale=self.scale_factor,
                model_path=model_path,
                model=model,
                device=self.device
            )

            # Initialize face enhancer if needed
            face_enhancer = None
            if self.enhance_faces:
                face_model_path = './models/GFPGANv1.4.pth'
                if not os.path.exists(face_model_path):
                    self.error_occurred.emit(f"Face model file not found: {face_model_path}")
                    return
                
                face_enhancer = GFPGANer(
                    model_path=face_model_path,
                    upscale=self.scale_factor,
                    arch='clean',
                    channel_multiplier=2,
                    device=self.device
                )

            try:
                # Read image
                img = cv2.imread(str(self.file_path), cv2.IMREAD_UNCHANGED)
                if img is None:
                    raise ValueError("Failed to read image")
                
                # Check image size and warn if too large
                if img.nbytes > 100 * 1024 * 1024:  # 100MB
                    self.error_occurred.emit(f"Image too large: {os.path.basename(self.file_path)}")
                    return
                
                # Upscale image
                self.progress_updated.emit(20)
                
                if face_enhancer:
                    # First do face enhancement
                    _, _, output = face_enhancer.enhance(
                        img,
                        has_aligned=False,
                        only_center_face=False,
                        paste_back=True
                    )
                    self.progress_updated.emit(60)
                    
                    # Then do general upscaling
                    output, _ = upsampler.enhance(output)
                else:
                    # Just do general upscaling
                    output, _ = upsampler.enhance(img)
                
                self.progress_updated.emit(90)
                
                # Generate output path
                base_name = os.path.splitext(os.path.basename(self.file_path))[0]
                enhancement = "_face" if self.enhance_faces else ""
                output_path = os.path.join(self.output_dir, f"{base_name}_upscaled_x{self.scale_factor}{enhancement}.{self.output_format.lower()}")
                
                # Save image
                cv2.imwrite(output_path, output)
                
                # Emit progress
                self.progress_updated.emit(100)
                self.task_completed.emit(str(self.file_path), output_path)
            
            except Exception as e:
                self.error_occurred.emit(f"Error processing {self.file_path}: {str(e)}")
                return

        except Exception as e:
            self.error_occurred.emit(f"Initialization error: {str(e)}")

    def cancel(self):
        self.cancel_requested = True

class ModernUpscaler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UPSCALE PRO")
        self.setGeometry(300, 100, 1000, 700)
        self.setWindowIcon(QIcon("./assists/Digitalfrem.png"))
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.output_dir = os.path.expanduser("~")
        self.setup_ui()
        self.check_device()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                self.set_image(file_path)

    def setup_ui(self):
        # Dark purple theme
        style = """
        QWidget {
            background-color: rgb(30, 30, 30);
            font-family: "Segoe UI";
            color: #e0e0e0;
        }
        
        QGroupBox {
            border: 1px solid #444;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 15px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px;
        }
        
        QPushButton {
            background-color: #8b3eb7;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
            min-width: 120px;
        }
        
        QPushButton:hover {
            background-color: #9b4ec7;
        }
        
        QPushButton:disabled {
            background-color: #333;
            color: #777;
        }
        
        QComboBox {
            background-color: #252525;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 5px;
            color: #e0e0e0;
            min-width: 120px;
        }
        
        QComboBox:hover {
            border: 1px solid #bb86fc;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #333;
            border-left-style: solid;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #252525;
            selection-background-color: #8b3eb7;
            color: white;
        }
        
        QLineEdit {
            background-color: #252525;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 5px;
            color: #e0e0e0;
        }
        
        QListWidget {
            background-color: #252525;
            border: 1px solid #444;
            border-radius: 4px;
            color: #e0e0e0;
        }
        
        QProgressBar {
            border: 1px solid #444;
            border-radius: 4px;
            text-align: center;
            background-color: #252525;
        }
        
        QProgressBar::chunk {
            background-color: #8b3eb7;
            width: 10px;
        }
        
        #PreviewBox {
            background-color: #252525;
            border: 1px solid #444;
            border-radius: 5px;
            min-width: 300px;
            min-height: 300px;
        }
        
        #PreviewLabel {
            color: #e0e0e0;
            font-weight: bold;
        }
        
        QScrollArea {
            border: none;
        }
        
        QScrollBar:vertical {
            border: none;
            background: #252525;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #8b3eb7;
            min-height: 20px;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
        }
        
        QCheckBox {
            spacing: 5px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        """
        self.setStyleSheet(style)
        
        # Main widget and layout with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)
        
        main_widget = QWidget()
        scroll.setWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Title and logo
        title_layout = QHBoxLayout()
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("./assists/Digitalfrem.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignLeft)
        
        self.title = QLabel("UPSCALE PRO")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.title.setStyleSheet("color: #bb86fc;")
        self.title.setAlignment(Qt.AlignLeft)
        
        title_layout.addWidget(self.logo)
        title_layout.addWidget(self.title)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        # File selection section
        file_group = QGroupBox("Image Selection")
        file_layout = QVBoxLayout()
        
        # Add file button
        btn_layout = QHBoxLayout()
        self.add_file_btn = QPushButton("Select Image")
        self.add_file_btn.clicked.connect(self.select_image)
        self.clear_file_btn = QPushButton("Clear Image")
        self.clear_file_btn.clicked.connect(self.clear_image)
        self.clear_file_btn.setEnabled(False)
        
        btn_layout.addWidget(self.add_file_btn)
        btn_layout.addWidget(self.clear_file_btn)
        btn_layout.addStretch()
        
        # File display
        self.file_label = QLabel("No image selected (drag & drop supported)")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("color: #aaa; font-style: italic;")
        
        file_layout.addLayout(btn_layout)
        file_layout.addWidget(self.file_label)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # Settings section
        settings_group = QGroupBox("Upscale Settings")
        settings_layout = QHBoxLayout()
        
        # Scale factor
        scale_layout = QVBoxLayout()
        scale_layout.addWidget(QLabel("Scale Factor:"))
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["2x", "4x"])
        self.scale_combo.setCurrentIndex(1)  # Default to 4x
        scale_layout.addWidget(self.scale_combo)
        
        # Device info
        device_layout = QVBoxLayout()
        device_layout.addWidget(QLabel("Processing Device:"))
        self.device_label = QLabel("Detecting...")
        self.device_label.setStyleSheet("font-weight: bold; color: #bb86fc;")
        device_layout.addWidget(self.device_label)
        
        # Output format
        format_layout = QVBoxLayout()
        format_layout.addWidget(QLabel("Output Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPG", "WEBP", "BMP"])
        format_layout.addWidget(self.format_combo)
        
        settings_layout.addLayout(scale_layout)
        settings_layout.addLayout(device_layout)
        settings_layout.addLayout(format_layout)
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # Face enhancement option
        self.face_enhance_check = QCheckBox("Enhance Faces (GFPGAN)")
        self.face_enhance_check.setToolTip("Enable face restoration for portraits and images with visible faces")
        self.face_enhance_check.setChecked(False)
        main_layout.addWidget(self.face_enhance_check)

        # Output directory
        output_group = QGroupBox("Output Settings")
        output_layout = QHBoxLayout()
        
        self.output_path = QLineEdit(self.output_dir)
        self.output_path.setReadOnly(True)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.select_output_dir)
        
        output_layout.addWidget(QLabel("Output Folder:"))
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.browse_btn)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QHBoxLayout()
        
        # Before preview
        before_layout = QVBoxLayout()
        before_label = QLabel("Original")
        before_label.setObjectName("PreviewLabel")
        before_label.setAlignment(Qt.AlignCenter)
        self.before_preview = QLabel("Drag & drop an image or click 'Select Image'")
        self.before_preview.setAlignment(Qt.AlignCenter)
        self.before_preview.setObjectName("PreviewBox")
        self.before_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.before_preview.setMinimumSize(300, 300)
        before_layout.addWidget(before_label)
        before_layout.addWidget(self.before_preview)
        
        # After preview
        after_layout = QVBoxLayout()
        after_label = QLabel("Upscaled")
        after_label.setObjectName("PreviewLabel")
        after_label.setAlignment(Qt.AlignCenter)
        self.after_preview = QLabel("Upscaled image will appear here")
        self.after_preview.setAlignment(Qt.AlignCenter)
        self.after_preview.setObjectName("PreviewBox")
        self.after_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.after_preview.setMinimumSize(300, 300)
        after_layout.addWidget(after_label)
        after_layout.addWidget(self.after_preview)
        
        preview_layout.addLayout(before_layout)
        preview_layout.addLayout(after_layout)
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)

        # Progress and action buttons
        action_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.upscale_btn = QPushButton("Upscale Image")
        self.upscale_btn.clicked.connect(self.start_upscaling)
        self.upscale_btn.setEnabled(False)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_upscaling)
        self.cancel_btn.setEnabled(False)
        
        action_layout.addWidget(self.progress_bar)
        action_layout.addWidget(self.upscale_btn)
        action_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(action_layout)

        main_layout.addStretch()

    def check_device(self):
        """Improved device detection for all processor types"""
        try:
            if torch.cuda.is_available():
                self.device = "cuda"
                self.device_label.setText("GPU (CUDA) 🚀")
                print("Using CUDA GPU acceleration")
            elif torch.backends.mps.is_available():  # For Apple M1/M2 chips
                self.device = "mps"
                self.device_label.setText("Apple Silicon (MPS) 🍏")
                print("Using Apple Metal Performance Shaders")
            elif hasattr(torch, "xpu") and torch.xpu.is_available():  # For Intel GPUs
                self.device = "xpu"
                self.device_label.setText("Intel GPU (XPU) 🔵")
                print("Using Intel XPU acceleration")
            else:
                self.device = "cpu"
                self.device_label.setText("CPU ⚙️")
                print("Using CPU (no GPU acceleration available)")
        except Exception as e:
            print(f"Device detection error: {e}")
            self.device = "cpu"
            self.device_label.setText("CPU ⚙️ (Error)")
            print("Falling back to CPU due to error")

    def get_device(self):
        """Return the appropriate torch device object based on detection"""
        if self.device == "cuda":
            return torch.device("cuda")
        elif self.device == "mps":
            return torch.device("mps")
        elif self.device == "xpu":
            return torch.device("xpu")
        else:
            return torch.device("cpu")

    def select_image(self):
        """Select single image through file dialog"""
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", 
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if file:
            self.set_image(file)

    def set_image(self, file_path):
        """Set the current image and update UI"""
        self.image_path = file_path
        self.file_label.setText(os.path.basename(file_path))
        self.file_label.setStyleSheet("color: #e0e0e0; font-style: normal;")
        self.clear_file_btn.setEnabled(True)
        self.upscale_btn.setEnabled(True)
        
        # Update preview
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.before_preview.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.before_preview.setPixmap(scaled_pixmap)
        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Could not load preview: {str(e)}")

    def clear_image(self):
        """Clear the current image"""
        self.image_path = None
        self.file_label.setText("No image selected (drag & drop supported)")
        self.file_label.setStyleSheet("color: #aaa; font-style: italic;")
        self.clear_file_btn.setEnabled(False)
        self.upscale_btn.setEnabled(False)
        self.clear_previews()

    def select_output_dir(self):
        """Select output directory"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_dir)
        if dir_path:
            self.output_dir = dir_path
            self.output_path.setText(dir_path)

    def clear_previews(self):
        """Clear both preview panes"""
        self.before_preview.clear()
        self.after_preview.clear()
        self.before_preview.setText("Drag & drop an image or click 'Select Image'")
        self.after_preview.setText("Upscaled image will appear here")

    def start_upscaling(self):
        """Start the upscaling process for single image"""
        if not self.image_path:
            QMessageBox.warning(self, "No Image", "Please select an image to upscale first.")
            return
        
        # Get settings
        scale_factor = int(self.scale_combo.currentText()[:-1])
        output_format = self.format_combo.currentText().lower()
        enhance_faces = self.face_enhance_check.isChecked()
        
        # Create worker thread
        self.worker = UpscaleWorker(
            self.image_path,
            self.output_dir,
            scale_factor,
            self.device,
            output_format,
            enhance_faces
        )
        
        # Connect signals
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.task_completed.connect(self.task_completed)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.finished.connect(self.upscaling_finished)
        
        # Update UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.upscale_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.add_file_btn.setEnabled(False)
        self.clear_file_btn.setEnabled(False)
        
        # Start worker
        self.worker.start()

    def cancel_upscaling(self):
        """Cancel the upscaling process"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel()
            self.cancel_btn.setEnabled(False)
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(False)

    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def task_completed(self, input_path, output_path):
        """Handle completed upscaling task"""
        try:
            pixmap = QPixmap(output_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.after_preview.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.after_preview.setPixmap(scaled_pixmap)
        except:
            pass

    def upscaling_finished(self):
        """Handle upscaling completion"""
        self.progress_bar.setVisible(False)
        self.upscale_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.add_file_btn.setEnabled(True)
        self.clear_file_btn.setEnabled(True)
        
        QMessageBox.information(self, "Complete", "Image upscaling completed!")

    def show_error(self, error_msg):
        """Show error message"""
        QMessageBox.critical(self, "Error", error_msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Check if models directory exists
    if not os.path.exists("models"):
        os.makedirs("models")
        QMessageBox.warning(None, "Models Missing", 
            "Please place the following model files in the 'models' directory:\n"
            "- RealESRGAN_x2.pth\n"
            "- RealESRGAN_x4.pth\n"
            "- GFPGANv1.4.pth (for face enhancement)")
    
    window = ModernUpscaler()
    window.show()
    sys.exit(app.exec_())