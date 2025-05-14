import tkinter as tk
from tkinter import messagebox
import os
import vlc
from screeninfo import get_monitors

VIDEO_PATH = "media/videos"
AUDIO_PATH = "media/audios"
REST_VIDEO_PATH = "media/descanso"

class ProjecaoApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Controle de Projeção - Igreja")
        self.master.geometry("900x700")

        self.preview_player = vlc.MediaPlayer()
        self.projector_player = vlc.MediaPlayer()
        self.audio_player = vlc.MediaPlayer()

        self.projector_window = None

        self.videos = [None, None, None]
        self.video_names = ["", "", ""]
        self.audio_file = None
        self.rest_video = None

        self.miniplayer_players = [vlc.MediaPlayer() for _ in range(3)]
        self.miniplayer_frames = []

        self.create_widgets()
        self.load_rest_video()
        self.open_projector_window()

    def create_widgets(self):
        tk.Label(self.master, text="Miniatura do Vídeo Atual:").pack()
        self.preview_container = tk.Frame(self.master)
        self.preview_container.pack(padx=10, pady=5, fill="x")

        self.preview_frame = tk.Frame(self.preview_container, bg="black", height=150)
        self.preview_frame.pack(fill="x")

        control_row = tk.Frame(self.preview_container)
        control_row.pack(pady=5)

        tk.Button(control_row, text="▶", command=self.resume_video, width=5).pack(side="left", padx=5)
        tk.Button(control_row, text="⏸", command=self.pause_video, width=5).pack(side="left", padx=5)
        tk.Button(control_row, text="⏹", command=self.stop_video, width=5).pack(side="left", padx=5)

        miniplayer_row = tk.Frame(self.master)
        miniplayer_row.pack(padx=10, pady=10, fill="x")

        for i in range(3):
            frame_column = tk.Frame(miniplayer_row)
            frame_column.pack(side="left", padx=5, expand=True, fill="both")

            frame = tk.Frame(frame_column, bg="gray", width=250, height=150)
            frame.pack()
            self.miniplayer_frames.append(frame)

            row = tk.Frame(frame_column)
            row.pack(pady=2)
            tk.Button(row, text="▶", command=lambda i=i: self.play_video(i), width=5).pack(side="top", pady=2)
            tk.Button(row, text="⏸", command=lambda i=i: self.pause_miniplayer(i), width=5).pack(side="top", pady=2)
            tk.Button(row, text="⏹", command=lambda i=i: self.stop_miniplayer(i), width=5).pack(side="top", pady=2)

        load_frame = tk.Frame(self.master)
        load_frame.pack(pady=10)

        for i in range(3):
            btn = tk.Button(load_frame, text=f"Carregar Vídeo {i+1}", command=lambda i=i: self.load_video(i))
            btn.grid(row=0, column=i, padx=5)

        tk.Button(load_frame, text="Carregar Música", command=self.load_audio).grid(row=0, column=3, padx=5)

        self.audio_label = tk.Label(self.master, text="Áudio carregado: nenhum", font=("Helvetica", 10))
        self.audio_label.pack(pady=5)

        play_frame = tk.Frame(self.master)
        play_frame.pack(pady=20)

        for i in range(3):
            btn = tk.Button(play_frame, text=f"▶ Reproduzir Vídeo {i+1}", command=lambda i=i: self.play_video(i))
            btn.grid(row=0, column=i, padx=5)

        tk.Button(play_frame, text="▶ Música", command=self.play_audio).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(play_frame, text="⏸ Pausar Tudo", command=self.pause_all).grid(row=1, column=1, padx=5)
        tk.Button(play_frame, text="⏹ Parar Tudo", command=self.stop_all).grid(row=1, column=2, padx=5)

    def preview_first_frame(self, media_path, frame_widget):
        player = vlc.MediaPlayer()
        media = vlc.Media(media_path)
        player.set_media(media)
        player.set_hwnd(frame_widget.winfo_id())
        player.play()
        self.master.after(200, player.pause)

    def load_video(self, slot):
        files = os.listdir(VIDEO_PATH)
        mp4s = [f for f in files if f.endswith(".mp4")]
        if len(mp4s) <= slot:
            messagebox.showerror("Erro", f"Coloque pelo menos {slot+1} vídeos em /media/videos")
            return
        self.videos[slot] = os.path.join(VIDEO_PATH, mp4s[slot])
        self.video_names[slot] = mp4s[slot]
        messagebox.showinfo("Vídeo Carregado", f"Slot {slot+1}: {mp4s[slot]}")
        self.preview_first_frame(self.videos[slot], self.miniplayer_frames[slot])
        if not any(self.preview_player.get_media()):
            self.preview_first_frame(self.videos[slot], self.preview_frame)

    def load_audio(self):
        files = os.listdir(AUDIO_PATH)
        mp3s = [f for f in files if f.endswith(".mp3")]
        if not mp3s:
            messagebox.showerror("Erro", "Nenhum MP3 encontrado em /media/audios")
            return
        self.audio_file = os.path.join(AUDIO_PATH, mp3s[0])
        self.audio_label.config(text=f"Áudio carregado: {mp3s[0]}")
        messagebox.showinfo("Áudio Carregado", f"Áudio: {mp3s[0]}")

    def load_rest_video(self):
        files = os.listdir(REST_VIDEO_PATH)
        mp4s = [f for f in files if f.endswith(".mp4")]
        if not mp4s:
            messagebox.showerror("Erro", "Coloque um vídeo de descanso em /media/descanso")
            return
        self.rest_video = os.path.join(REST_VIDEO_PATH, mp4s[0])

    def play_rest_video(self):
        if not self.rest_video:
            self.load_rest_video()
        if self.rest_video:
            media = vlc.Media(self.rest_video)
            media.add_option("input-repeat=-1")
            self.projector_player.set_media(media)
            self.projector_player.set_hwnd(self.projector_video_frame.winfo_id())
            self.projector_player.play()
            self.preview_player.set_media(media)
            self.preview_player.set_hwnd(self.preview_frame.winfo_id())
            self.preview_player.play()

    def play_video(self, slot):
        if self.videos[slot] is None:
            messagebox.showwarning("Aviso", f"Carregue um vídeo no slot {slot+1}")
            return
        if self.projector_video_frame is None:
            messagebox.showerror("Erro", "Janela de projeção não foi criada.")
            return
        self.wait_for_projector_window_ready(slot)

    def wait_for_projector_window_ready(self, slot):
        if self.projector_video_frame is None:
            self.master.after(100, self.wait_for_projector_window_ready, slot)
        else:
            media = vlc.Media(self.videos[slot])
            self.preview_player.set_media(media)
            self.preview_player.set_hwnd(self.preview_frame.winfo_id())
            self.preview_player.play()
            self.projector_player.set_media(media)
            self.projector_player.set_hwnd(self.projector_video_frame.winfo_id())
            self.projector_player.play()

    def play_audio(self):
        if not self.audio_file:
            messagebox.showwarning("Aviso", "Carregue o áudio primeiro.")
            return
        self.audio_player.set_media(vlc.Media(self.audio_file))
        self.audio_player.play()

    def pause_video(self):
        self.preview_player.pause()
        self.projector_player.pause()

    def stop_video(self):
        self.preview_player.stop()
        self.projector_player.stop()
        self.play_rest_video()

    def resume_video(self):
        self.preview_player.play()
        self.projector_player.play()

    def pause_all(self):
        self.preview_player.pause()
        self.projector_player.pause()
        self.audio_player.pause()

    def stop_all(self):
        self.preview_player.stop()
        self.projector_player.stop()
        self.audio_player.stop()
        self.play_rest_video()

    def pause_miniplayer(self, i):
        self.miniplayer_players[i].pause()

    def stop_miniplayer(self, i):
        self.miniplayer_players[i].stop()

    def open_projector_window(self):
        monitors = get_monitors()
        if len(monitors) < 2:
            self.show_warning("Erro", "Segunda tela não detectada.")
            return
        second = monitors[1]
        self.projector_window = tk.Toplevel(self.master)
        self.projector_window.overrideredirect(True)
        self.projector_window.geometry(f"{second.width}x{second.height}+{second.x}+{second.y}")
        self.projector_window.configure(bg="black")
        self.projector_video_frame = tk.Frame(self.projector_window, bg="black")
        self.projector_video_frame.pack(fill="both", expand=True)
        self.projector_window.protocol("WM_DELETE_WINDOW", lambda: None)
        self.play_rest_video()

    def show_warning(self, title, message):
        warning_window = tk.Toplevel(self.master)
        warning_window.title(title)
        warning_window.geometry("400x200")
        warning_window.configure(bg="#f0f0f0")
        warning_window.resizable(False, False)
        title_label = tk.Label(warning_window, text=title, font=("Helvetica", 16, "bold"), fg="white", bg="#f39c12", pady=10)
        title_label.pack(fill="x")
        message_label = tk.Label(warning_window, text=message, font=("Helvetica", 12), bg="#f0f0f0", pady=10, padx=20)
        message_label.pack(fill="both", expand=True)
        close_button = tk.Button(warning_window, text="Fechar", command=warning_window.destroy, width=15, height=2, bg="#3498db", fg="white")
        close_button.pack(pady=10)
        close_button.config(font=("Helvetica", 12, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjecaoApp(root)
    root.mainloop()
