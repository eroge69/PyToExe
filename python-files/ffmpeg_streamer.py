# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# ffmpeg_streamer_tk.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess, threading, json, os, re
from datetime import datetime

CONFIG_FILE = 'config.json'

class StreamerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Multi-Service Streamer GUI')
        self.geometry('650x600')
        self.process = None
        self.stop_flag = threading.Event()
        self.create_widgets()
        self.load_config()
        self.check_ffmpeg()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(fill='x', padx=10, pady=10)

        # 1) 서비스 선택
        ttk.Label(frm, text='Service:').grid(row=0, column=0, sticky='w')
        self.service_var = tk.StringVar(value='YouTube')
        service_cb = ttk.Combobox(frm, textvariable=self.service_var,
                                  values=['YouTube','Twitch','Custom'], width=10, state='readonly')
        service_cb.grid(row=0, column=1, sticky='w')
        service_cb.bind('<<ComboboxSelected>>', lambda e: self.toggle_custom_url())

        # Custom RTMP URL 입력
        self.custom_url_var = tk.StringVar()
        self.custom_url_entry = ttk.Entry(frm, textvariable=self.custom_url_var, width=40)
        self.custom_url_entry.grid(row=0, column=2, columnspan=2, sticky='w')
        self.custom_url_entry.grid_remove()

        # 2) 스트림 키 (YouTube/Twitch)
        ttk.Label(frm, text='Stream Key:').grid(row=1, column=0, sticky='w')
        self.key_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.key_var, width=50).grid(row=1, column=1, columnspan=3, sticky='w')

        # 3) 동영상 파일
        ttk.Label(frm, text='Video File:').grid(row=2, column=0, sticky='w')
        self.file_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.file_var, width=50).grid(row=2, column=1, columnspan=2, sticky='w')
        ttk.Button(frm, text='Browse', command=self.browse_file).grid(row=2, column=3)

        # 4) Option: Loop / Resolution / FPS / Bitrate
        self.loop_var = tk.BooleanVar()
        ttk.Checkbutton(frm, text='Loop', variable=self.loop_var).grid(row=3, column=0, sticky='w')

        ttk.Label(frm, text='Resolution:').grid(row=3, column=1, sticky='e')
        self.res_var = tk.StringVar(value='720p')
        ttk.Combobox(frm, textvariable=self.res_var,
                     values=['720p','1080p'], width=7, state='readonly').grid(row=3, column=2, sticky='w')

        ttk.Label(frm, text='FPS:').grid(row=4, column=0, sticky='w')
        self.fps_var = tk.StringVar(value='30')
        ttk.Combobox(frm, textvariable=self.fps_var,
                     values=['24','30','60'], width=7, state='readonly').grid(row=4, column=1, sticky='w')

        ttk.Label(frm, text='Bitrate:').grid(row=4, column=2, sticky='e')
        self.br_var = tk.StringVar(value='2500k')
        ttk.Combobox(frm, textvariable=self.br_var,
                     values=['1000k','2500k','4500k','6000k'], width=7, state='readonly').grid(row=4, column=3, sticky='w')

        # 5) Schedule
        ttk.Label(frm, text='Schedule (YYYY-MM-DD HH:MM:SS):').grid(row=5, column=0, columnspan=2, sticky='w')
        self.schedule_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.schedule_var, width=25).grid(row=5, column=2, columnspan=2, sticky='w')

        # 6) Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=(0,10))
        ttk.Button(btn_frame, text='Start Streaming', command=self.start_or_schedule).pack(side='left')
        ttk.Button(btn_frame, text='Stop', command=self.stop_stream).pack(side='left', padx=5)

        # 7) Progress display
        prog_frame = ttk.Frame(self)
        prog_frame.pack(fill='x', padx=10)
        ttk.Label(prog_frame, text='Progress:').pack(side='left')
        self.progress_var = tk.StringVar(value='Not started')
        ttk.Label(prog_frame, textvariable=self.progress_var).pack(side='left')

        # 8) Log
        self.log = tk.Text(self, state='disabled')
        self.log.pack(fill='both', expand=True, padx=10, pady=10)

    def toggle_custom_url(self):
        if self.service_var.get() == 'Custom':
            self.custom_url_entry.grid()
        else:
            self.custom_url_entry.grid_remove()

    def browse_file(self):
        path = filedialog.askopenfilename(
            filetypes=[('Video','*.mp4 *.mov *.mkv'),('All','*.*')]
        )
        if path:
            self.file_var.set(path)

    def check_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg','-version'], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, check=True)
        except Exception:
            messagebox.showwarning('Warning','ffmpeg not found. Please install ffmpeg.')

    def log_write(self, msg):
        self.log.config(state='normal')
        self.log.insert('end', msg+'\n')
        self.log.see('end')
        self.log.config(state='disabled')

    def start_or_schedule(self):
        sched = self.schedule_var.get().strip()
        if sched:
            try:
                dt = datetime.strptime(sched, '%Y-%m-%d %H:%M:%S')
                delay = (dt - datetime.now()).total_seconds()
                if delay > 0:
                    self.log_write(f'Scheduled streaming at {sched}')
                    threading.Timer(delay, self.start_stream).start()
                    self.save_config()
                    return
            except Exception:
                messagebox.showerror('Error','Invalid schedule format')
                return
        self.start_stream()

    def start_stream(self):
        if self.process:
            return

        video = self.file_var.get().strip()
        key   = self.key_var.get().strip()
        service = self.service_var.get()

        if not os.path.isfile(video) or (not key and service!='Custom'):
            messagebox.showerror('Error','Select valid video and stream key/URL')
            return

        # 서비스별 RTMP URL 구성
        if service == 'YouTube':
            url = f'rtmp://a.rtmp.youtube.com/live2/{key}'
        elif service == 'Twitch':
            url = f'rtmp://live.twitch.tv/app/{key}'
        else:  # Custom
            url = self.custom_url_var.get().strip()

        fps = int(self.fps_var.get())
        gop = fps * 2  # keyframe interval = 2s
        res = '1280x720' if self.res_var.get()=='720p' else '1920x1080'
        br = self.br_var.get()
        loop = ['-stream_loop','-1'] if self.loop_var.get() else []

        cmd = [
            'ffmpeg', *loop,
            '-re', '-i', video,
            '-c:v', 'libx264', '-b:v', br,
            '-maxrate', br, '-bufsize', str(int(br[:-1])*2)+'k',
            '-preset', 'veryfast',
            '-vf', f'scale={res}',
            '-r', str(fps),
            '-g', str(gop), '-keyint_min', str(gop), '-sc_threshold', '0',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-ac', '2',
            '-f', 'flv', url
        ]

        self.log_write('Executing: ' + ' '.join(cmd))
        self.progress_var.set('Starting...')
        self.stop_flag.clear()

        def run():
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, text=True)
            time_regex = re.compile(r'time=(\d+:\d+:\d+\.\d+)')
            for line in self.process.stdout:
                if self.stop_flag.is_set():
                    break
                self.log_write(line.strip())
                match = time_regex.search(line)
                if match:
                    self.progress_var.set(match.group(1))
            self.process.wait()
            self.process = None
            self.progress_var.set('Stopped')

        threading.Thread(target=run, daemon=True).start()
        self.save_config()

    def stop_stream(self):
        if self.process and self.process.poll() is None:
            self.stop_flag.set()
            self.process.terminate()
            self.log_write('Stream stopped')
            self.progress_var.set('Stopped')

    def load_config(self):
        if os.path.isfile(CONFIG_FILE):
            cfg = json.load(open(CONFIG_FILE))
            self.service_var.set(cfg.get('service','YouTube'))
            self.custom_url_var.set(cfg.get('custom_url',''))
            self.key_var.set(cfg.get('key',''))
            self.file_var.set(cfg.get('video',''))
            self.loop_var.set(cfg.get('loop',False))
            self.res_var.set(cfg.get('resolution','720p'))
            self.fps_var.set(str(cfg.get('fps',30)))
            self.br_var.set(cfg.get('bitrate','2500k'))
            self.schedule_var.set(cfg.get('schedule',''))
            self.toggle_custom_url()

    def save_config(self):
        cfg = {
            'service': self.service_var.get(),
            'custom_url': self.custom_url_var.get(),
            'key': self.key_var.get(),
            'video': self.file_var.get(),
            'loop': self.loop_var.get(),
            'resolution': self.res_var.get(),
            'fps': int(self.fps_var.get()),
            'bitrate': self.br_var.get(),
            'schedule': self.schedule_var.get()
        }
        json.dump(cfg, open(CONFIG_FILE,'w'), indent=2)

if __name__ == '__main__':
    app = StreamerApp()
    app.mainloop()
