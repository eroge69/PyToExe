import os
import shutil
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Exif reading libraries
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    import exifread
except ImportError:
    raise ImportError("Bitte installieren Sie die Abhängigkeiten: pip install pillow exifread")


def get_exif_date_time_original(filepath):
    """
    Liest das EXIF-Datum (DateTimeOriginal) eines Bildes aus.
    """
    try:
        with open(filepath, 'rb') as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
            dto = tags.get("EXIF DateTimeOriginal") or tags.get("Image DateTime")
            if dto:
                dt = str(dto)
                return datetime.datetime.strptime(dt, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"Fehler beim Lesen von EXIF für {filepath}: {e}")
    return None


def scan_and_copy(sd_path, target_path, date):
    """
    Durchsucht die SD-Karte nach Bildern mit dem angegebenen Datum
    und kopiert sie in den Zielordner.
    """
    count = 0
    for root, dirs, files in os.walk(sd_path):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".cr2", ".nef", ".arw", ".dng")):
                fullpath = os.path.join(root, file)
                dt = get_exif_date_time_original(fullpath)
                if dt and dt.date() == date:
                    dest = os.path.join(target_path, os.path.basename(fullpath))
                    try:
                        shutil.copy2(fullpath, dest)
                        count += 1
                    except Exception as e:
                        print(f"Kopiervorgang fehlgeschlagen für {fullpath}: {e}")
    return count


def get_sd_stats(sd_path):
    """
    Ermittelt Gesamt-, Belegt- und Freispeicherplatz und Berechnet den Belegungsprozentsatz.
    """
    total, used, free = shutil.disk_usage(sd_path)
    used_percent = used / total * 100
    return total, used, free, used_percent


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lightroom Auto Import")
        self.geometry("550x250")
        self.create_widgets()

    def create_widgets(self):
        # SD-Karte Pfad
        tk.Label(self, text="SD-Karten Pfad:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.sd_entry = tk.Entry(self, width=40)
        self.sd_entry.grid(row=0, column=1, padx=5)
        tk.Button(self, text="Durchsuchen", command=self.browse_sd).grid(row=0, column=2, padx=5)

        # Lightroom Watch-Ordner
        tk.Label(self, text="Watch-Ordner (Lightroom):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.target_entry = tk.Entry(self, width=40)
        self.target_entry.grid(row=1, column=1, padx=5)
        tk.Button(self, text="Durchsuchen", command=self.browse_target).grid(row=1, column=2, padx=5)

        # Datumseingabe
        tk.Label(self, text="Datum (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = tk.Entry(self, width=20)
        self.date_entry.grid(row=2, column=1, padx=5)

        # Statistiken
        self.stats_label = tk.Label(self, text="", fg="blue")
        self.stats_label.grid(row=3, column=0, columnspan=3, pady=10)

        # Import-Button
        tk.Button(self, text="Importieren", command=self.import_photos, width=15).grid(row=4, column=1, pady=10)

    def browse_sd(self):
        path = filedialog.askdirectory()
        if path:
            self.sd_entry.delete(0, tk.END)
            self.sd_entry.insert(0, path)

    def browse_target(self):
        path = filedialog.askdirectory()
        if path:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, path)

    def import_photos(self):
        sd_path = self.sd_entry.get().strip()
        target_path = self.target_entry.get().strip()
        date_str = self.date_entry.get().strip()

        # Eingaben prüfen
        if not sd_path or not target_path or not date_str:
            messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen.")
            return
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Fehler", "Ungültiges Datum. Bitte im Format YYYY-MM-DD eingeben.")
            return

        # SD-Karten Statistiken
        total, used, free, used_percent = get_sd_stats(sd_path)
        stats_text = (
            f"SD-Karte: Gesamt: {total // (1024**3)} GB, Belegt: {used // (1024**3)} GB "
            f"({used_percent:.1f}%), Frei: {free // (1024**3)} GB"
        )
        self.stats_label.config(text=stats_text)
        if used_percent > 75:
            messagebox.showwarning(
                "Warnung", 
                "Achtung, der Speicherplatz auf der SD-Karte ist über 75% belegt!"
            )

        # Kopiervorgang starten
        count = scan_and_copy(sd_path, target_path, date)
        messagebox.showinfo("Fertig", f"{count} Dateien aus dem {date_str} importiert.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
