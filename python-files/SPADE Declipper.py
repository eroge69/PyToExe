import sys
if sys.platform == 'win32':
    import ctypes
    # Setze explizit eine AppUserModelID, damit das Fenster­-Icon auch in der Taskleiste angezeigt wird
    myappid = u'SPADE.Audio.Declipper'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    # Konsolenfenster ausblenden
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

import os
import threading
import numpy as np
from scipy.fftpack import dct, idct
import soundfile as sf
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog, messagebox
import tkinter as tk  # Für tkinter-Variablen
from PIL import Image

# ---------------------------
# Audioverarbeitungsfunktionen
# ---------------------------
def normalize_peak(audio, target_dB=-0.5):
    """
    Normalisiert ein Audiosignal so, dass die maximale Amplitude dem Zielpegel entspricht.
    target_dB: Zielpegel in dB (z. B. -0.5 dB entspricht ca. 0.944 als linearer Faktor).
    """
    target_amp = 10 ** (target_dB / 20.0)
    max_val = np.max(np.abs(audio))
    if max_val == 0:
        return audio
    scale = target_amp / max_val
    return audio * scale

def _spade_declipping_mono(sig, threshold, iterations, sparsity_ratio, alpha, verbose, progress_callback=None):
    """
    Deklippt ein Mono-Audiosignal mithilfe des DCT-basierten SPADE-Algorithmus.
    
    sig: Eingabesignal (numpy-Array).
    threshold: Schwellenwert, ab dem ein Sample als geclippt gilt.
    iterations, sparsity_ratio, alpha: Parameter des Algorithmus.
    progress_callback: Optionaler Callback zur Fortschrittsanzeige.
    """
    original = np.copy(sig)
    sig_hat = np.copy(sig)

    indices_pos = np.where(sig >= threshold)[0]
    indices_neg = np.where(sig <= -threshold)[0]
    indices_unclipped = np.where(np.abs(sig) < threshold)[0]

    if len(indices_pos) == 0 and len(indices_neg) == 0:
        return sig

    for it in range(iterations):
        coeffs = dct(sig_hat, norm='ortho')
        n = len(coeffs)
        num_keep = max(1, int(sparsity_ratio * n))
        sorted_indices = np.argsort(np.abs(coeffs))
        keep_indices = sorted_indices[-num_keep:]
        coeffs_thresholded = np.zeros_like(coeffs)
        coeffs_thresholded[keep_indices] = coeffs[keep_indices]
        sig_temp = idct(coeffs_thresholded, norm='ortho')

        # Datenkonsistenz wahren:
        sig_proj = np.copy(sig_temp)
        sig_proj[indices_unclipped] = original[indices_unclipped]
        sig_proj[indices_pos] = np.where(sig_temp[indices_pos] < threshold, threshold, sig_temp[indices_pos])
        sig_proj[indices_neg] = np.where(sig_temp[indices_neg] > -threshold, -threshold, sig_temp[indices_neg])

        sig_hat = sig_hat + alpha * (sig_proj - sig_hat)

        if progress_callback:
            progress_callback(it + 1, iterations)

    return sig_hat

def spade_declipping(audio, threshold, iterations, sparsity_ratio, alpha, verbose=False, progress_callback=None):
    """
    Deklippt ein Mono- oder Mehrkanal-Audiosignal.
    """
    if audio.ndim == 1:
        return _spade_declipping_mono(audio, threshold, iterations, sparsity_ratio, alpha, verbose, progress_callback)
    elif audio.ndim == 2:
        repaired_channels = []
        for ch in range(audio.shape[1]):
            repaired_channel = _spade_declipping_mono(
                audio[:, ch], threshold, iterations, sparsity_ratio, alpha, verbose, progress_callback
            )
            repaired_channels.append(repaired_channel)
        return np.stack(repaired_channels, axis=-1)
    else:
        raise ValueError("Nicht unterstütztes Audioformat.")

# ---------------------------
# GUI-Klasse mit customtkinter & Drag-n-Drop
# ---------------------------
class DeclipperGUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        # Versuche, das Fenster-Icon zu setzen 
        try:
            self.iconbitmap("C:\\Users\\david\\OneDrive\\Dokumente\\SPADE Declipper\\Audiowelle.ico")
        except Exception:
            from tkinter import PhotoImage
            icon_path = os.path.join(os.path.dirname(__file__), "C:\\Users\\david\\OneDrive\\Dokumente\\SPADE Declipper\\Audiowelle.png")
            if os.path.exists(icon_path):
                img = PhotoImage(file="C:\\Users\\david\\OneDrive\\Dokumente\\SPADE Declipper\\Audiowelle.png")
                self.tk.call('wm', 'iconphoto', self._w, img)
        self.title("SPADE Audio Declipper")
        self.geometry("550x320")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.configure(bg="#e6f9ff")

        # Variablen
        self.input_file = tk.StringVar()
        # Zielpegel zur Normalisierung (in dB, Bereich -2.0 bis 0.0, Standard -0.5 dB)
        self.norm_target = tk.DoubleVar(value=-0.5)

        self.create_widgets()
        # Trace, um das Label bei Änderungen auf eine Nachkommastelle mit " dB" zu aktualisieren
        self.norm_target.trace("w", self.update_norm_label)

    def create_widgets(self):
        # Hauptcontainer
        self.main_frame = ctk.CTkFrame(master=self, width=500, height=300, fg_color="#e6f9ff")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.main_frame.drop_target_register(DND_FILES)
        self.main_frame.dnd_bind("<<Drop>>", self.drop_file)

        # Hinweis-Label für Drag-&-Drop
        self.drop_or_label = ctk.CTkLabel(
            master=self.main_frame,
            text="Datei hier ablegen oder",
            font=("Segoe UI", 12)
        )
        self.drop_or_label.pack(pady=(5,2))

        # Dateiauswahl: "Durchsuchen"-Button und Dateiname-Label
        self.file_button = ctk.CTkButton(
            master=self.main_frame,
            text="Durchsuchen",
            command=self.browse_input,
            corner_radius=20
        )
        self.file_button.pack(pady=5)
        self.file_label = ctk.CTkLabel(
            master=self.main_frame,
            text="Keine Datei ausgewählt",
            font=("Segoe UI", 12)
        )
        self.file_label.pack(pady=5)

        # Regler: "Normalisieren auf:" – Zielpegel in dB (Bereich -2.0 bis 0.0)
        slider_frame = ctk.CTkFrame(master=self.main_frame, fg_color="#e6f9ff")
        slider_frame.pack(pady=10, fill="x")
        self.norm_label = ctk.CTkLabel(
            master=slider_frame,
            text="Normalisieren auf:",
            font=("Segoe UI", 12)
        )
        self.norm_label.pack(side="left", padx=(10, 5))
        self.norm_slider = ctk.CTkSlider(
            master=slider_frame,
            from_=-2.0,
            to=0.0,
            variable=self.norm_target
        )
        self.norm_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.norm_value_label = ctk.CTkLabel(
            master=slider_frame,
            text=f"{self.norm_target.get():.1f} dB",
            font=("Segoe UI", 12),
            width=50
        )
        self.norm_value_label.pack(side="left", padx=5)

        # Aktionsbereich: Startknopf (später wird hier eine Fortschrittsleiste angezeigt)
        self.action_frame = ctk.CTkFrame(master=self.main_frame, fg_color="#e6f9ff")
        self.action_frame.pack(pady=10)
        self.start_button = ctk.CTkButton(
            master=self.action_frame,
            text="Start",
            command=self.start_processing,
            corner_radius=20
        )
        self.start_button.pack(pady=5)

        # Statusanzeige
        self.status_label = ctk.CTkLabel(
            master=self.main_frame,
            text="",
            font=("Segoe UI", 12)
        )
        self.status_label.pack(pady=10)

    def update_norm_label(self, *args):
        value = round(self.norm_target.get(), 1)
        self.norm_value_label.configure(text=f"{value:.1f} dB")

    def browse_input(self):
        file_path = filedialog.askopenfilename(
            title="Select Input Audio",
            filetypes=[("Audio Files", "*.wav *.flac *.ogg *.mp3")]
        )
        if file_path:
            self.input_file.set(file_path)
            self.file_label.configure(text=os.path.basename(file_path))

    def drop_file(self, event):
        file_path = event.data
        if file_path.startswith("{") and file_path.endswith("}"):
            file_path = file_path[1:-1]
        self.input_file.set(file_path)
        self.file_label.configure(text=os.path.basename(file_path))

    def start_processing(self):
        if not self.input_file.get():
            messagebox.showerror("Error", "Bitte wählen Sie eine Input-Datei aus.")
            return

        try:
            audio, samplerate = sf.read(self.input_file.get())
        except Exception as e:
            messagebox.showerror("Error", f"Fehler beim Laden der Datei:\n{str(e)}")
            return

        # Automatische Bestimmung des Clipping-Thresholds: 95. Perzentil der absoluten Amplituden
        threshold_val = np.percentile(np.abs(audio), 95)
        num_clipped = np.sum(np.abs(audio) >= threshold_val)
        total_samples = audio.size
        clip_ratio = num_clipped / total_samples

        iterations = max(200, min(int(200 + clip_ratio * 600), 800))
        if clip_ratio < 0.1:
            sparsity_ratio = 0.10
            alpha = 0.7
        elif clip_ratio < 0.3:
            sparsity_ratio = 0.15
            alpha = 0.5
        else:
            sparsity_ratio = 0.20
            alpha = 0.3

        # Ersetze den Startknopf durch eine Fortschrittsleiste
        self.start_button.destroy()
        self.progress_bar = ctk.CTkProgressBar(master=self.action_frame, width=200)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)
        self.status_label.configure(text="Verarbeite...")

        thread = threading.Thread(
            target=self.process_audio,
            args=(threshold_val, iterations, sparsity_ratio, alpha, samplerate, self.input_file.get())
        )
        thread.start()

    def update_progress(self, current, total):
        progress = current / total
        self.progress_bar.set(progress)
        self.update_idletasks()

    def process_audio(self, threshold_val, iterations, sparsity_ratio, alpha, samplerate, input_path):
        try:
            audio, _ = sf.read(input_path)
        except Exception as e:
            messagebox.showerror("Error", f"Fehler beim Laden der Datei:\n{str(e)}")
            self.start_button = ctk.CTkButton(
                master=self.action_frame,
                text="Start",
                command=self.start_processing,
                corner_radius=20
            )
            self.start_button.pack(pady=5)
            return

        repaired_audio = spade_declipping(
            audio, threshold_val, iterations, sparsity_ratio, alpha,
            verbose=False, progress_callback=self.update_progress
        )
        norm_db = self.norm_target.get()
        repaired_audio = normalize_peak(repaired_audio, target_dB=norm_db)

        dirname = os.path.dirname(input_path)
        basename = os.path.basename(input_path)
        name, ext = os.path.splitext(basename)
        output_file = os.path.join(dirname, f"{name}-declipped{ext}")

        try:
            sf.write(output_file, repaired_audio, samplerate)
        except Exception as e:
            messagebox.showerror("Error", f"Fehler beim Speichern der Datei:\n{str(e)}")

        self.status_label.configure(text="Fertig")
        self.progress_bar.set(1)

if __name__ == "__main__":
    app = DeclipperGUI()
    app.mainloop()
