# Hinweis: Dieses Skript verwendet tkinter, das in manchen Python-Umgebungen nicht vorinstalliert ist.
# Falls tkinter nicht verfügbar ist, kann es unter Linux mit "sudo apt install python3-tk" nachinstalliert werden.

try:
    import tkinter as tk
    import random
    import threading
    import pyaudio
    import numpy as np
except ModuleNotFoundError:
    print("Fehler: Ein erforderliches Modul ist nicht verfügbar. Bitte stelle sicher, dass tkinter, pyaudio und numpy installiert sind.")
    tk = None

if tk is not None:
    class TalkingFaceApp:
        def __init__(self, root):
            self.root = root
            self.root.title("Sprechendes Gesicht")
            self.root.configure(bg='black')
            self.fullscreen = False

            # Skalierbares Fenster
            self.root.geometry("600x400")
            self.root.minsize(300, 200)
            self.root.bind('<F11>', self.toggle_fullscreen)

            # Canvas zum Zeichnen
            self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)

            # Reagiere auf Fenstergrösse
            self.canvas.bind('<Configure>', self.redraw_face)

            # Gesichtsstatus
            self.face_active = True
            self.blinking = False
            self.eye_shift = 0
            self.mouth_open = 0

            # Tastenbindung
            self.root.bind('<a>', lambda e: self.activate_face())
            self.root.bind('<c>', lambda e: self.deactivate_face())
            self.root.bind('<KeyPress-space>', lambda e: self.start_listening())
            self.root.bind('<KeyRelease-space>', lambda e: self.stop_listening())

            # Audio-Konfiguration
            self.listening = False
            self.audio_thread = threading.Thread(target=self.listen_audio, daemon=True)
            self.audio_thread.start()

            # Animation starten
            self.animate()
            self.redraw_face()

        def toggle_fullscreen(self, event=None):
            self.fullscreen = not self.fullscreen
            self.root.attributes("-fullscreen", self.fullscreen)

        def activate_face(self):
            self.face_active = True
            self.redraw_face()

        def deactivate_face(self):
            self.face_active = False
            self.redraw_face()

        def animate(self):
            if self.face_active:
                if random.random() < 0.05:
                    self.blinking = not self.blinking
                if random.random() < 0.1:
                    self.eye_shift = random.randint(-3, 3)
                self.redraw_face()
            self.root.after(300, self.animate)

        def start_listening(self):
            self.listening = True

        def stop_listening(self):
            self.listening = False
            self.mouth_open = 0

        def listen_audio(self):
            # Audio-Stream initialisieren
            pa = pyaudio.PyAudio()
            stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
            while True:
                if self.listening:
                    data = np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
                    volume = np.linalg.norm(data) / 1000
                    self.mouth_open = min(max(int(volume * 10), 1), 10)
                else:
                    self.mouth_open = 0

        def redraw_face(self, event=None):
            self.canvas.delete("all")
            if not self.face_active:
                return

            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()

            # Gesichtsdimensionen
            eye_radius = min(w, h) // 20
            eye_offset_x = w // 5
            eye_y = h // 3
            nose_y = h // 2
            mouth_y = int(h * 0.7)
            mouth_width = w // 5
            mouth_height = h // 40 + self.mouth_open  # Mundhöhe hängt von Audio ab

            # Augen
            eye_height = 2 if self.blinking else eye_radius
            self.canvas.create_oval(w//2 - eye_offset_x - eye_radius + self.eye_shift, eye_y - eye_height,
                                    w//2 - eye_offset_x + eye_radius + self.eye_shift, eye_y + eye_height,
                                    fill='white')
            self.canvas.create_oval(w//2 + eye_offset_x - eye_radius + self.eye_shift, eye_y - eye_height,
                                    w//2 + eye_offset_x + eye_radius + self.eye_shift, eye_y + eye_height,
                                    fill='white')

            # Nase
            self.canvas.create_polygon(w//2, nose_y - 10,
                                       w//2 - 5, nose_y + 10,
                                       w//2 + 5, nose_y + 10,
                                       fill='white')

            # Mund
            self.canvas.create_rectangle(w//2 - mouth_width//2, mouth_y,
                                         w//2 + mouth_width//2, mouth_y + mouth_height,
                                         fill='white')

    if __name__ == "__main__":
        root = tk.Tk()
        app = TalkingFaceApp(root)
        root.mainloop()
else:
    print("Das Programm wird beendet, da tkinter nicht verfügbar ist.")
