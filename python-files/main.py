import cv2
import mediapipe as mp
import numpy as np
import time
from math import hypot
import os
from threading import Thread
from collections import deque

class ProFaceHandTracker:
    def __init__(self):
        print("Initializing Professional Tracking System...")

        self.mp_hands = mp.solutions.hands
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0
        )

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=False
        )

        self.cap = cv2.VideoCapture(0)
        self.setup_camera()

        self.fps_buffer = deque(maxlen=30)
        self.running = True
        self.show_mesh = True
        self.show_hands = True
        self.fullscreen = False

        self.stats = {
            'fps': 0,
            'processing_time': 0
        }

        self.colors = {
            'primary': (0, 255, 0),
            'secondary': (255, 0, 0),
            'accent': (0, 0, 255),
            'text': (255, 255, 255),
            'signature': (200, 200, 200)
        }

        cv2.namedWindow('Pro Tracking System v1.0', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Pro Tracking System v1.0', 1280, 720)
        cv2.setWindowProperty('Pro Tracking System v1.0', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

        Thread(target=self.update_stats, daemon=True).start()

    def setup_camera(self):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def update_stats(self):
        while self.running:
            if self.fps_buffer:
                self.stats['fps'] = int(np.mean(self.fps_buffer))
            time.sleep(0.1)

    def process_frame(self, frame):
        frame = cv2.resize(frame, (1280, 720))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results_hands = self.hands.process(frame_rgb)
        results_face = self.face_mesh.process(frame_rgb)

        if self.show_hands and results_hands.multi_hand_landmarks:
            frame = self.draw_hands(frame, results_hands)

        if self.show_mesh and results_face.multi_face_landmarks:
            frame = self.draw_face_mesh(frame, results_face)

        return frame

    def draw_hands(self, frame, results):
        for hand_landmarks in results.multi_hand_landmarks:
            self.mp_draw.draw_landmarks(
                frame, 
                hand_landmarks, 
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=self.colors['primary'], thickness=1),
                self.mp_draw.DrawingSpec(color=self.colors['secondary'], thickness=1)
            )
        return frame

    def draw_face_mesh(self, frame, results):
        for face_landmarks in results.multi_face_landmarks:
            self.mp_draw.draw_landmarks(
                frame,
                face_landmarks,
                self.mp_face_mesh.FACEMESH_CONTOURS,
                self.mp_draw.DrawingSpec(color=self.colors['primary'], thickness=1),
                self.mp_draw.DrawingSpec(color=self.colors['accent'], thickness=1)
            )
        return frame

    def draw_interface(self, frame):
        stats_panel = np.zeros((80, frame.shape[1], 3), dtype=np.uint8)
        texts = [
            f"FPS: {self.stats['fps']}",
            "Pro Tracking System v1.0"
        ]

        for i, txt in enumerate(texts):
            cv2.putText(stats_panel, txt, (10, 25 * (i + 1)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors['text'], 2)

        frame_with_stats = np.vstack([stats_panel, frame])

        signature_panel = np.zeros((40, frame.shape[1], 3), dtype=np.uint8)
        cv2.putText(signature_panel, "MADE BY KYRYLL SENATOR", 
                   (frame.shape[1] // 2 - 180, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors['signature'], 2, cv2.LINE_AA)

      #  cv2.putText(signature_panel, "FOR DASHA :) ", 
        ##           (frame.shape[1] - 200, 30),
          #         cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.colors['signature'], 2, cv2.LINE_AA)

        return np.vstack([frame_with_stats, signature_panel])

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            cv2.setWindowProperty('Pro Tracking System v1.0', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty('Pro Tracking System v1.0', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Pro Tracking System v1.0', 1280, 720)

    def run(self):
        print("Starting Professional Tracking System...")

        while self.running:
            start_time = time.time()
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            processed_frame = self.process_frame(frame)
            output_frame = self.draw_interface(processed_frame)

            self.fps_buffer.append(1 / (time.time() - start_time))
            self.stats['processing_time'] = (time.time() - start_time) * 1000

            cv2.imshow('Pro Tracking System v1.0', output_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
            elif key == ord('h'):
                self.show_hands = not self.show_hands
            elif key == ord('m'):
                self.show_mesh = not self.show_mesh
            elif key == ord('f'):
                self.toggle_fullscreen()

        self.cap.release()
        cv2.destroyAllWindows()
        print("Professional Tracking System shutdown complete.")

if __name__ == "__main__":
    tracker = ProFaceHandTracker()
    tracker.run()