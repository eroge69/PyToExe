import cv2
import joblib
import mediapipe as mp
import numpy as np
from gtts import gTTS
import pygame
import threading
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import ttkbootstrap as tb

# --- Hàm chọn và load model ---
def load_model():
    default_model = "hand_model.pkl"
    if not os.path.exists(default_model):
        messagebox.showinfo("Select Model", "Không tìm thấy hand_model.pkl. Hãy chọn file mô hình (.pkl)")
        model_path = filedialog.askopenfilename(title="Chọn file mô hình", filetypes=[("Pickle files", "*.pkl")])
        if not model_path:
            messagebox.showerror("Error", "❌ Không chọn được file mô hình. Thoát.")
            exit()
    else:
        use_default = messagebox.askyesno("Model Found", f"Tìm thấy {default_model}. Dùng luôn file này?")
        if use_default:
            model_path = default_model
        else:
            model_path = filedialog.askopenfilename(title="Chọn file mô hình", filetypes=[("Pickle files", "*.pkl")])
            if not model_path:
                messagebox.showerror("Error", "❌ Không chọn được file mô hình. Thoát.")
                exit()

    try:
        model = joblib.load(model_path)
        print(f"✅ Đã load mô hình từ: {model_path}")
        return model
    except Exception as e:
        messagebox.showerror("Error", f"❌ Lỗi khi load mô hình: {str(e)}")
        exit()

# --- Khởi tạo MediaPipe ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)

# --- Hàm lấy landmarks ---
def get_landmarks_from_hand(hand_landmarks):
    return [coord for lm in hand_landmarks.landmark for coord in (lm.x, lm.y, lm.z)]

# --- Class chính ---
class HandTypingApp:
    def __init__(self, root):
        self.root = root
        self.style = tb.Style("litera")
        self.root.title("🖐️ Hand Gesture Typing")
        self.root.geometry("500x700")

        self.model = load_model()
        self.mode = "light"
        self.text_output = ""
        self.last_prediction = ""
        self.prediction_history = []
        self.normalized_text = ""
        self.mouse_clicked = None
        self.confirm_rect = (10, 120, 160, 170)
        self.delete_rect = (170, 120, 320, 170)
        self.space_rect = (330, 120, 480, 170)
        self.no_movement_counter = 0

        self.setup_ui()

    def setup_ui(self):
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(fill="both", expand=True)

        ttk.Label(self.frame, text="🖐️ Hand Gesture Typing", font=("Helvetica", 20, "bold")).pack(pady=(10, 15))

        self.start_btn = ttk.Button(self.frame, text="▶️ Start Recognition", style="success.TButton", command=self.start_recognition)
        self.start_btn.pack(pady=10, ipadx=10, ipady=5)

        self.output_entry = ttk.Entry(self.frame, font=("Helvetica", 14), justify="center")
        self.output_entry.pack(pady=10, ipadx=5, ipady=5, fill="x")
        self.output_entry.insert(0, "Results will be displayed here...")

        self.history_label = ttk.Label(self.frame, text="⏱ Prediction History:", font=("Helvetica", 10))
        self.history_label.pack(pady=(5, 5))

        self.prediction_list = tk.Listbox(self.frame, height=4, font=("Courier", 12))
        self.prediction_list.pack(pady=(0, 15), fill="x")

        self.clear_btn = ttk.Button(self.frame, text="🧹 Clear All", style="warning.TButton", command=self.clear_output)
        self.clear_btn.pack(pady=5, ipadx=10, ipady=5)

        self.normalize_btn = ttk.Button(self.frame, text="🌌 Normalize Text", style="secondary.TButton", command=self.normalize_text)
        self.normalize_btn.pack(pady=5, ipadx=10, ipady=5)

        self.normalized_textbox_label = ttk.Label(self.frame, text="Normalized Text:", font=("Helvetica", 10))
        self.normalized_textbox_label.pack(pady=(10, 5))

        self.normalized_textbox = ttk.Entry(self.frame, font=("Helvetica", 14), justify="center")
        self.normalized_textbox.pack(pady=(5, 15), ipadx=5, ipady=5, fill="x")
        self.normalized_textbox.insert(0, "Normalized text will appear here.")

        self.accept_btn = ttk.Button(self.frame, text="🔔 Accept Text", style="success.TButton", command=self.accept_normalized_text)
        self.accept_btn.pack(pady=5, ipadx=10, ipady=5)

        self.play_btn = ttk.Button(self.frame, text="🔊 Play Audio", style="primary.TButton", command=self.play_audio)
        self.play_btn.pack(pady=5, ipadx=10, ipady=5)

        self.theme_btn = ttk.Button(self.frame, text="🌃 Light/Dark Theme", style="info.TButton", command=self.toggle_theme)
        self.theme_btn.pack(pady=10, ipadx=10, ipady=5)

        self.quit_btn = ttk.Button(self.frame, text="❌ Exit", style="danger.TButton", command=self.root.quit)
        self.quit_btn.pack(pady=5, ipadx=10, ipady=5)

        self.status_label = ttk.Label(self.frame, text="", font=("Helvetica", 10))
        self.status_label.pack(pady=(10, 0))

    def toggle_theme(self):
        if self.mode == "light":
            self.style.theme_use("darkly")
            self.mode = "dark"
        else:
            self.style.theme_use("litera")
            self.mode = "light"

    def start_recognition(self):
        threading.Thread(target=self.run_camera, daemon=True).start()

    def play_audio(self):
        if os.path.exists("output.mp3"):
            try:
                pygame.mixer.init()
                pygame.mixer.music.load("output.mp3")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.quit()
            except Exception as e:
                messagebox.showerror("Error", f"Could not play audio: {str(e)}")
        else:
            messagebox.showinfo("Information", "No audio file found to play.")

    def clear_output(self):
        self.text_output = ""
        self.output_entry.delete(0, tk.END)
        self.prediction_list.delete(0, tk.END)
        self.prediction_history.clear()
        self.normalized_textbox.delete(0, tk.END)
        self.normalized_textbox.insert(0, "Normalized text will appear here.")
        messagebox.showinfo("Cleared", "Results and history have been cleared.")

    def normalize_text(self):
        if self.text_output:
            self.normalized_text = self.text_output.strip().upper().replace("_", " ")
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.normalized_text)
            self.normalized_textbox.delete(0, tk.END)
            self.normalized_textbox.insert(0, self.normalized_text)
            messagebox.showinfo("Normalized", "Text has been normalized!")
        else:
            messagebox.showinfo("Information", "No content to normalize.")

    def accept_normalized_text(self):
        if self.normalized_text:
            tts = gTTS(text=self.normalized_text, lang="en")
            tts.save("output.mp3")
            messagebox.showinfo("TTS", "🎷 Audio created!")
        else:
            messagebox.showinfo("Information", "No normalized text to save.")

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.confirm_rect[0] <= x <= self.confirm_rect[2] and self.confirm_rect[1] <= y <= self.confirm_rect[3]:
                self.mouse_clicked = "confirm"
            elif self.delete_rect[0] <= x <= self.delete_rect[2] and self.delete_rect[1] <= y <= self.delete_rect[3]:
                self.mouse_clicked = "delete"
            elif self.space_rect[0] <= x <= self.space_rect[2] and self.space_rect[1] <= y <= self.space_rect[3]:
                self.mouse_clicked = "space"

    def run_camera(self):
        cap = cv2.VideoCapture(0)
        frame_count = 0
        cooldown = 10
        self.mouse_clicked = None
        self.last_prediction = ""
        self.no_movement_counter = 0

        cv2.namedWindow("Hand Typing")
        cv2.setMouseCallback("Hand Typing", self.mouse_callback)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            self.status_label.config(text="Processing...")

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    landmarks = get_landmarks_from_hand(hand_landmarks)

                    if len(landmarks) == 63 and frame_count == 0:
                        prediction = self.model.predict([landmarks])[0]
                        self.last_prediction = prediction
                        frame_count = cooldown
                        break

            if frame_count > 0:
                frame_count -= 1

            cv2.putText(frame, f"Predict: {self.last_prediction}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Output: {self.text_output}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            cv2.rectangle(frame, self.confirm_rect[:2], self.confirm_rect[2:], (100, 200, 255), -1)
            cv2.putText(frame, "Confirm", (self.confirm_rect[0] + 10, self.confirm_rect[1] + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            cv2.rectangle(frame, self.delete_rect[:2], self.delete_rect[2:], (255, 100, 100), -1)
            cv2.putText(frame, "Delete", (self.delete_rect[0] + 20, self.delete_rect[1] + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

            cv2.rectangle(frame, self.space_rect[:2], self.space_rect[2:], (200, 200, 200), -1)
            cv2.putText(frame, "Space", (self.space_rect[0] + 25, self.space_rect[1] + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

            if self.mouse_clicked == "confirm" and self.last_prediction:
                self.text_output += self.last_prediction
                self.prediction_history.append(self.last_prediction)
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, self.text_output)
                self.prediction_list.insert(tk.END, f"> {self.last_prediction}")
                self.mouse_clicked = None
                self.no_movement_counter = 0

            elif self.mouse_clicked == "delete" and self.text_output:
                self.text_output = self.text_output[:-1]
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, self.text_output)
                self.mouse_clicked = None
                self.no_movement_counter = 0

            elif self.mouse_clicked == "space":
                self.text_output += " "
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, self.text_output)
                self.prediction_list.insert(tk.END, "> (space)")
                self.mouse_clicked = None
                self.no_movement_counter = 0

            cv2.imshow("Hand Typing", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# --- Main chương trình ---
if __name__ == "__main__":
    root = tb.Window(themename="litera")
    app = HandTypingApp(root)
    root.mainloop()
