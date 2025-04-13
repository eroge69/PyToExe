import sys
import cv2
import numpy as np
import threading
import time
import ctypes
import os
import win32gui
import win32con
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QGraphicsDropShadowEffect
)
from insightface.app import FaceAnalysis
from scipy.spatial.distance import cosine
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize



# Initialize face analysis
app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0)

PIN_CODE = "837787"

class FaceLoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.face_analysis = FaceAnalysis()
        self.face_analysis.prepare(ctx_id=0, det_size=(640, 640)) 
        self.status_message = "Initializing face lock..."
        self.initUI()
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.recognized = False
        self.recognized_timer = 0
        # Hide taskbar and desktop icons
        self.hide_desktop_and_taskbar()
        self.status_message = "Scanning… Please align your face"

        # Load reference image and compute its embedding
        self.reference_face = self.load_reference_face('reference.jpg')

    def hide_desktop_and_taskbar(self):
        # Hide the taskbar
        taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        if taskbar_hwnd:
            win32gui.ShowWindow(taskbar_hwnd, win32con.SW_HIDE)

        # Hide desktop icons
        progman = win32gui.FindWindow("Progman", None)
        if progman:
            win32gui.ShowWindow(progman, win32con.SW_HIDE)

        # Force the window to stay in front
        hwnd = self.winId().__int__()
        ctypes.windll.user32.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    def initUI(self):
        self.setWindowTitle("Face ID Login")
        self.showFullScreen()  # Set to full screen
        self.setStyleSheet("background-color: #083C6D;")  # Darker blue background

        # Video feed
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(480, 480)
        self.camera_label.setStyleSheet("border-radius: 30px; overflow: hidden;")

        # Status message
        self.status_label = QLabel(self.status_message, self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #FFD700; font-size: 18px; font-weight: bold;")

        # PIN entry
        self.pin_input = QLineEdit(self)
        self.pin_input.setPlaceholderText("Enter PIN")
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setStyleSheet("background-color: #E9F0F8; color: #333333; padding: 6px; border-radius: 6px;")

        # Submit button with icon
        self.submit_button = QPushButton(self)
        self.submit_button.setIcon(QIcon(QPixmap('submit_icon.png')))
        self.submit_button.setIconSize(QSize(30, 30))  # Adjust icon size
        self.submit_button.setStyleSheet("background: transparent; border: none;")
        self.submit_button.clicked.connect(self.check_pin)

        pin_layout = QHBoxLayout()
        pin_layout.addStretch(1)  # This will center the PIN input and button
        pin_layout.addWidget(self.pin_input)
        pin_layout.addWidget(self.submit_button)
        pin_layout.addStretch(1)  # Add another stretch to center them horizontally

        

        # ID box (initially hidden)
        self.id_box = QLabel("Access Granted!", self)
        self.id_box.setStyleSheet("""
            background-color: rgba(0, 119, 255, 0.2);
            border: 2px solid #0077FF;
            color: #FFFFFF;
            font-size: 20px;
            padding: 20px;
            border-top-left-radius: 30px;
            border-bottom-right-radius: 30px;
        """)
        self.id_box.setVisible(False)
        self.id_box.setAlignment(Qt.AlignCenter)

        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.camera_label, alignment=Qt.AlignHCenter)
        main_layout.addWidget(self.status_label)
        main_layout.addLayout(pin_layout)
        main_layout.addWidget(self.id_box)
        main_layout.addStretch()

        outer_layout = QHBoxLayout(self)
        outer_layout.addLayout(main_layout, stretch=2)
        

        self.setLayout(outer_layout)


    def load_reference_face(self, path):
        # Load and process reference image to extract its face embedding
        ref_img = cv2.imread(path)
        ref_img_rgb = cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB)
        faces = self.face_analysis.get(ref_img_rgb)
        if faces:
            return faces[0].embedding
        return None

    def update_frame(self):
        if self.recognized:  # Skip processing if already recognized
            # Trigger the close event after 3 seconds
            if time.time() - self.recognized_timer > 3:
                QApplication.quit()
            return

        ret, frame = self.capture.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.face_analysis.get(rgb_frame)

        if faces:
            self.status_message = "Face detected ✅"
            self.status_label.setStyleSheet("color: #00FF9D; font-size: 18px; font-weight: bold;")
            detected_face = faces[0]
            detected_embedding = detected_face.embedding

            if self.reference_face is not None:
                # Compare embeddings (using cosine similarity)
                dist = cosine(self.reference_face, detected_embedding)
                if dist < 0.4:  # Threshold for recognizing faces, can adjust
                    if not self.recognized:
                        self.recognized = True
                        self.recognized_timer = time.time()
                        self.id_box.setVisible(True)
                        self.show_id()  # Show ID with name and picture
                else:
                    self.status_message = "Face not recognized ❌ Try again"
                    self.status_label.setStyleSheet("color: #FF4C4C; font-size: 18px; font-weight: bold;")
            else:
                self.status_message = "No reference face loaded ❌"
                self.status_label.setStyleSheet("color: #FF4C4C; font-size: 18px; font-weight: bold;")
        else:
            self.status_message = "No face detected ❌ Try again"
            self.status_label.setStyleSheet("color: #FF4C4C; font-size: 18px; font-weight: bold;")

        if self.recognized and time.time() - self.recognized_timer > 7:
            self.recognized = False
            self.id_box.setVisible(False)

        self.status_label.setText(self.status_message)

        # Draw mesh overlay (for visualization)
        if faces:
            face = faces[0]
            for coord in face.kps:
                x, y = int(coord[0]), int(coord[1])
                cv2.circle(rgb_frame, (x, y), 3, (97, 232, 247), -1)
            for i in range(0, len(face.kps) - 1):
                pt1 = tuple(face.kps[i].astype(int))
                pt2 = tuple(face.kps[i + 1].astype(int))
                cv2.line(rgb_frame, pt1, pt2, (0, 207, 255), 1)
            cv2.line(rgb_frame, tuple(face.kps[-1].astype(int)), tuple(face.kps[0].astype(int)), (0, 207, 255), 1)

        qt_image = QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(qt_image).scaled(self.camera_label.width(), self.camera_label.height(), Qt.KeepAspectRatio)
        self.camera_label.setPixmap(pix)


    def show_id(self):
        self.id_box.setText("<b>Name:</b> Vaidyanathan Srinath<br><b> </b> <br><img src='id.jpg' style='width: 100px; height: 100px; border-radius: 50%;'>")
        self.id_box.setVisible(True)

    def check_pin(self):
        if self.pin_input.text() == PIN_CODE:
            self.recognized = True
            self.recognized_timer = time.time()
            self.id_box.setVisible(True)
            self.status_label.setText("PIN accepted ✅")
            self.status_label.setStyleSheet("color: #00FF9D; font-size: 18px; font-weight: bold;")
        else:
            self.status_label.setText("Incorrect PIN ❌")
            self.status_label.setStyleSheet("color: #FF4C4C; font-size: 18px; font-weight: bold;")

    def closeEvent(self, event):
        self.capture.release()

        # Restore desktop and taskbar when app closes
        taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        if taskbar_hwnd:
            win32gui.ShowWindow(taskbar_hwnd, win32con.SW_SHOW)

        progman = win32gui.FindWindow("Progman", None)
        if progman:
            win32gui.ShowWindow(progman, win32con.SW_SHOW)


        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_app = FaceLoginApp()
    login_app.show()
    sys.exit(app.exec_())