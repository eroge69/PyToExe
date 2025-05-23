import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QFileDialog, QComboBox, QMessageBox, QHBoxLayout, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFontMetrics


class UpscaleWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, input_path, output_path, scale, quality="ultrafast", high_quality=False):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.scale = scale
        self.quality = quality
        self.high_quality = high_quality

    def run(self):
        command = [
            "ffmpeg", "-i", self.input_path,
            "-vf", f"scale={self.scale}",
            "-c:v", "libx264", "-crf", "18", "-preset", self.quality,
            "-y"
        ]

        if self.high_quality:
            command += ["-profile:v", "high", "-tune", "film", "-b:v", "25M"]

        command.append(self.output_path)

        try:
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            self.finished.emit(True, self.output_path)
        except subprocess.CalledProcessError as e:
            self.finished.emit(False, str(e))


class VideoUpscaler(QWidget):
    def __init__(self):
        super().__init__()
        self.video_path = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🚀 Fast Video Upscaler")
        self.setGeometry(300, 300, 500, 250)

        self.label = QLabel("📂 Select a video file to upscale.", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        self.btn_browse = QPushButton("🔍 Browse")
        self.btn_browse.clicked.connect(self.browse_file)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["720p", "1080p", "1440p", "4K"])

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["ultrafast (Fast)", "slow (Better Quality)"])

        self.btn_upscale = QPushButton("⏫ Upscale Now")
        self.btn_upscale.clicked.connect(self.upscale_video)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_browse)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(QLabel("Resolution:"))
        hbox1.addWidget(self.resolution_combo)
        hbox1.addStretch()
        hbox1.addWidget(QLabel("Preset:"))
        hbox1.addWidget(self.quality_combo)
        layout.addLayout(hbox1)

        layout.addWidget(self.btn_upscale)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setStyleSheet("""
            QLabel { font-size: 14px; }
            QPushButton { padding: 10px; font-weight: bold; }
            QComboBox { padding: 5px; }
        """)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.webm)"
        )
        if file_path:
            self.video_path = file_path
            self.display_short_path(file_path)

    def display_short_path(self, path):
        metrics = QFontMetrics(self.label.font())
        elided = metrics.elidedText(f"✅ Selected: {path}", Qt.ElideMiddle, self.label.width() - 20)
        self.label.setText(elided)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.video_path:
            self.display_short_path(self.video_path)

    def upscale_video(self):
        if not self.video_path:
            QMessageBox.warning(self, "No File", "Please select a video file first.")
            return

        resolution = self.resolution_combo.currentText()
        quality_label = self.quality_combo.currentText()
        quality = "ultrafast" if "Fast" in quality_label else "slow"

        scale_dict = {
            "720p": "1280:720",
            "1080p": "1920:1080",
            "1440p": "2560:1440",
            "4K": "3840:2160"
        }
        scale = scale_dict[resolution]
        output_path = self.video_path.rsplit('.', 1)[0] + f"_{resolution}.mp4"
        high_quality = resolution == "4K"

        self.btn_upscale.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        self.worker = UpscaleWorker(self.video_path, output_path, scale, quality, high_quality)
        self.worker.finished.connect(self.on_upscale_finished)
        self.worker.start()

    def on_upscale_finished(self, success, message):
        self.btn_upscale.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            QMessageBox.information(self, "✅ Success", f"Upscaled video saved at:\n{message}")
        else:
            QMessageBox.critical(self, "❌ Error", f"Upscaling failed:\n{message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoUpscaler()
    window.show()
    sys.exit(app.exec_())
