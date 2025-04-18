import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# Funzione per scaricare il video
def download_video(url, output_dir, yt_dlp_path, ffmpeg_path, trim_start=None, trim_end=None):
    # Percorso del file di output
    output_file = os.path.join(output_dir, "video_trimmato")

    # Configurazione yt-dlp
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_file + '.%(ext)s',
        'ffmpeg_location': ffmpeg_path,  # Utilizzo del percorso specifico di ffmpeg
    }

    # Download del video
    try:
        print("Scaricando il video...")
        command = [yt_dlp_path, '--ffmpeg-location', ffmpeg_path, '-f', 'bestvideo+bestaudio/best', '-o', output_file + '.%(ext)s', url]
        subprocess.run(command, check=True)
        print(f"Download completato: {output_file}")

        # Se sono forniti i parametri di trimmaggio, procediamo con ffmpeg
        if trim_start and trim_end:
            trim_video(output_file + '.mkv', output_dir, trim_start, trim_end, ffmpeg_path)
        else:
            messagebox.showinfo("Successo", f"Download completato: {output_file}.mkv")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Errore", f"Si è verificato un errore durante il download: {e}")

# Funzione per trimmare il video
def trim_video(input_file, output_dir, trim_start, trim_end, ffmpeg_path):
    try:
        print(f"Trimmando il video da {trim_start} a {trim_end}...")
        # Definisci il nome del file trimmato
        output_file = os.path.join(output_dir, "video_trimmato_trimmato.mp4")

        # Costruire il comando ffmpeg
        command = [
            ffmpeg_path,
            '-i', input_file,
            '-ss', trim_start,  # Tempo di inizio
            '-to', trim_end,    # Tempo di fine
            '-c:v', 'copy',     # Copia il video senza modificarlo
            '-c:a', 'copy',     # Copia l'audio senza modificarlo
            output_file
        ]

        # Esegui il comando ffmpeg
        subprocess.run(command, check=True)
        messagebox.showinfo("Successo", f"Trimmaggio completato! File salvato come {output_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Errore", f"Si è verificato un errore durante il trimmaggio: {e}")

# Funzione per gestire il click del pulsante di download
def on_download_click():
    url = url_entry.get()
    trim_choice = trim_entry.get()

    if url:
        yt_dlp_path = yt_dlp_entry.get()

        # Ottieni il percorso di ffmpeg dalla stessa cartella dello script
        current_directory = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(current_directory, "non_toccare", "ffmpeg", "bin", "ffmpeg.exe")

        if trim_choice:
            try:
                start_time, end_time = trim_choice.split('-')
                download_video(url, os.getcwd(), yt_dlp_path, ffmpeg_path, trim_start=start_time, trim_end=end_time)
            except ValueError:
                messagebox.showerror("Errore", "Formato intervallo non valido. Usa MM:SS-MM:SS.")
        else:
            download_video(url, os.getcwd(), yt_dlp_path, ffmpeg_path)
    else:
        messagebox.showerror("Errore", "Per favore, inserisci un URL valido.")

# Creazione della finestra GUI
window = tk.Tk()
window.title("Scarica e Trimmare Video")
window.geometry("500x350")

# URL video
url_label = tk.Label(window, text="Inserisci l'URL del video:")
url_label.pack(pady=10)
url_entry = tk.Entry(window, width=40)
url_entry.pack(pady=5)

# Percorso dell'eseguibile yt-dlp
yt_dlp_label = tk.Label(window, text="Inserisci il percorso di yt-dlp.exe:")
yt_dlp_label.pack(pady=10)
yt_dlp_entry = tk.Entry(window, width=40)
yt_dlp_entry.pack(pady=5)

# Intervallo di trimmaggio
trim_label = tk.Label(window, text="Inserisci intervallo di trimmaggio (MM:SS-MM:SS), oppure lascia vuoto:")
trim_label.pack(pady=10)
trim_entry = tk.Entry(window, width=40)
trim_entry.pack(pady=5)

# Pulsante di download
download_button = tk.Button(window, text="Scarica e Trimmare", command=on_download_click)
download_button.pack(pady=20)

# Avvio della GUI
window.mainloop()
