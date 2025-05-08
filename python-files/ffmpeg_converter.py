import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def run_ffmpeg(cmd, status_label):
    status_label.config(text="Processing...", foreground="blue")
    def target():
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, err = p.communicate()
        if p.returncode == 0:
            status_label.config(text="Done!", foreground="green")
        else:
            status_label.config(text="Error", foreground="red")
            messagebox.showerror("FFmpeg Error", err.decode("utf-8", errors="ignore"))
    threading.Thread(target=target, daemon=True).start()

class FFmpegGUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FFmpeg Converter & Encoder")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        media_tab = ttk.Frame(notebook)
        self._build_media_tab(media_tab)
        notebook.add(media_tab, text="Media Transcoder")

        photo_tab = ttk.Frame(notebook)
        self._build_photo_tab(photo_tab)
        notebook.add(photo_tab, text="Photo Encoder")

        notebook.pack(expand=True, fill="both", padx=10, pady=10)

    def _build_media_tab(self, frame):
        pad = {"padx":5,"pady":5}
        ttk.Label(frame, text="Input File:").grid(row=0,column=0,sticky="w",**pad)
        self.med_in = ttk.Entry(frame,width=40); self.med_in.grid(row=0,column=1,**pad)
        ttk.Button(frame,text="...",width=3,command=self._choose_med_input).grid(row=0,column=2,**pad)

        ttk.Label(frame, text="Output Format:").grid(row=1,column=0,sticky="w",**pad)
        self.med_format = ttk.Combobox(frame, values=["mp4","mkv","avi","mov"], state="readonly")
        self.med_format.current(0); self.med_format.grid(row=1,column=1,**pad)

        ttk.Label(frame, text="Video Codec:").grid(row=2,column=0,sticky="w",**pad)
        self.med_vcodec = ttk.Combobox(frame, values=["copy","h264","h265","vp9"], state="readonly")
        self.med_vcodec.current(1); self.med_vcodec.grid(row=2,column=1,**pad)

        ttk.Label(frame, text="Audio Codec:").grid(row=3,column=0,sticky="w",**pad)
        self.med_acodec = ttk.Combobox(frame, values=["copy","aac","mp3","wav","opus"], state="readonly")
        self.med_acodec.current(1); self.med_acodec.grid(row=3,column=1,**pad)

        ttk.Label(frame, text="Video Bitrate:").grid(row=4,column=0,sticky="w",**pad)
        self.med_vbit = ttk.Combobox(frame, values=["2500k","3000k","5000k"], state="readonly")
        self.med_vbit.current(0); self.med_vbit.grid(row=4,column=1,**pad)
        self.med_vbit_custom = ttk.Entry(frame,width=10); self.med_vbit_custom.grid(row=4,column=2,**pad)

        ttk.Label(frame, text="Audio Bitrate:").grid(row=5,column=0,sticky="w",**pad)
        self.med_abit = ttk.Entry(frame,width=10); self.med_abit.insert(0,"128k"); self.med_abit.grid(row=5,column=1,**pad)

        ttk.Button(frame,text="Start", command=self._on_med_start).grid(row=6,column=0,columnspan=3,sticky="ew",**pad)
        self.med_status = ttk.Label(frame,text="Ready",foreground="green")
        self.med_status.grid(row=7,column=0,columnspan=3,sticky="w",**pad)

    def _choose_med_input(self):
        f = filedialog.askopenfilename(
            title="Select media",
            filetypes=[("Media files","*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.flac *.aac"),("All files","*.*")]
        )
        if f:
            self.med_in.delete(0,tk.END)
            self.med_in.insert(0,f)

    def _on_med_start(self):
        inp = self.med_in.get().strip()
        if not inp:
            messagebox.showerror("Error","Select input file")
            return

        base = os.path.splitext(os.path.basename(inp))[0]
        fmt = self.med_format.get()
        out = filedialog.asksaveasfilename(
            title="Save as",
            initialfile=f"{base}.{fmt}",
            defaultextension=f".{fmt}",
            filetypes=[(fmt.upper(),f"*.{fmt}")]
        )
        if not out: return

        cmd = ["ffmpeg","-y","-i",inp]
        # Video codec
        vc = self.med_vcodec.get()
        if vc == "copy":
            cmd += ["-c:v","copy"]
        else:
            cmd += ["-c:v",f"lib{vc}"]
            vb = self.med_vbit_custom.get() or self.med_vbit.get()
            cmd += ["-b:v", vb]
        # Audio codec
        ac = self.med_acodec.get()
        if ac == "copy":
            cmd += ["-c:a","copy"]
        else:
            lib = {"mp3":"libmp3lame","wav":"pcm_s16le","opus":"libopus"}.get(ac,ac)
            cmd += ["-c:a", lib, "-b:a", self.med_abit.get()]

        cmd.append(out)
        run_ffmpeg(cmd, self.med_status)

    def _build_photo_tab(self, frame):
        pad = {"padx":5,"pady":5}
        ttk.Label(frame, text="Input Image:").grid(row=0,column=0,sticky="w",**pad)
        self.img_in = ttk.Entry(frame,width=40); self.img_in.grid(row=0,column=1,**pad)
        ttk.Button(frame,text="...",width=3,command=self._choose_img_input).grid(row=0,column=2,**pad)

        ttk.Label(frame, text="Output Format:").grid(row=1,column=0,sticky="w",**pad)
        img_formats = ["png","jpeg","jpg","tiff"]
        self.img_format = ttk.Combobox(frame, values=img_formats, state="readonly")
        self.img_format.current(0); self.img_format.grid(row=1,column=1,**pad)

        ttk.Button(frame,text="Convert", command=self._on_img_start).grid(row=2,column=0,columnspan=3,sticky="ew",**pad)
        self.img_status = ttk.Label(frame,text="Ready",foreground="green")
        self.img_status.grid(row=3,column=0,columnspan=3,sticky="w",**pad)

    def _choose_img_input(self):
        f = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Images","*.png *.jpg *.jpeg *.tiff"),("All files","*.*")]
        )
        if f:
            self.img_in.delete(0,tk.END)
            self.img_in.insert(0,f)

    def _on_img_start(self):
        inp = self.img_in.get().strip()
        if not inp:
            messagebox.showerror("Error","Select input image")
            return

        base = os.path.splitext(os.path.basename(inp))[0]
        fmt = self.img_format.get()
        out = filedialog.asksaveasfilename(
            title="Save as",
            initialfile=f"{base}.{fmt}",
            defaultextension=f".{fmt}",
            filetypes=[(fmt.upper(),f"*.{fmt}")]
        )
        if not out: return

        # FFmpeg로 지원 가능한 포맷만 변환
        cmd = ["ffmpeg","-y","-i",inp,out]
        run_ffmpeg(cmd, self.img_status)

if __name__ == "__main__":
    app = FFmpegGUIApp()
    app.mainloop()
