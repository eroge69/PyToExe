import customtkinter as ctk
from screeninfo import get_monitors
import psutil
import time
import GPUtil
import re
import sys
import os
import logging
import matplotlib
from matplotlib.lines import Line2D
matplotlib.use('Agg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
logging.getLogger('GPUtil').setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger('psutil').setLevel(logging.CRITICAL)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

sys.stdout = sys.stderr = open(os.devnull, 'w')

PRIMARY_ACCENT = "#00ffe7"
SECONDARY_ACCENT = "#1e90ff"
FRAME_BG = "#222831"
LABEL_BG = "#393e46"

class SystemMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Detect monitors and set position to top-left of 3rd screen
        monitors = get_monitors()
        target_monitor = None
        for m in monitors:
            if m.width == 800 and m.height == 480:
                target_monitor = m
                break
        if target_monitor:
            self.fixed_x = target_monitor.x
            self.fixed_y = target_monitor.y
        else:
            self.fixed_x = monitors[0].x
            self.fixed_y = monitors[0].y

        # Remove title bar
        self.overrideredirect(True)
        self.geometry(f"800x480+{self.fixed_x}+{self.fixed_y}")
        self.resizable(False, False)
        self.configure(bg=FRAME_BG)

        # Prevent window from being moved
        self.bind('<Configure>', self.keep_in_place)

        # Main container for CPU and Disk side by side
        self.top_main = ctk.CTkFrame(self, fg_color="transparent", width=780, height=220)
        self.top_main.place(x=10, y=10)
        self.top_main.grid_columnconfigure(0, weight=1, uniform="group1")
        self.top_main.grid_columnconfigure(1, weight=1, uniform="group1")
        self.top_main.grid_rowconfigure(0, weight=1)

        # ========== CPU FRAME ==========
        self.cpu_frame = ctk.CTkFrame(self.top_main, corner_radius=20, fg_color=FRAME_BG)
        self.cpu_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        self.cpu_label = ctk.CTkLabel(self.cpu_frame, text="CPU USAGE", font=("Segoe UI", 20, "bold"),
                                      text_color=PRIMARY_ACCENT, fg_color=LABEL_BG, corner_radius=10, width=360, height=30)
        self.cpu_label.pack(pady=(10,5))

        # Per-core grid
        self.core_frame = ctk.CTkFrame(self.cpu_frame, fg_color="transparent")
        self.core_frame.pack(pady=(0,10), padx=5, fill="both", expand=True)
        for col in range(4):
            self.core_frame.grid_columnconfigure(col, weight=1)

        self.core_widgets = []
        cores = psutil.cpu_count()
        for i in range(cores):
            row = i // 4
            col = i % 4
            core_box = ctk.CTkFrame(self.core_frame, corner_radius=12, fg_color=LABEL_BG)
            core_box.grid(row=row, column=col, padx=2.5, pady=2.5, sticky="nsew")
            core_label = ctk.CTkLabel(core_box, text=f"C{i}", font=("Segoe UI", 13, "bold"),
                                      text_color=SECONDARY_ACCENT)
            core_label.pack(pady=(4,0))
            core_bar = ctk.CTkProgressBar(core_box, width=60, height=8, corner_radius=4, progress_color=PRIMARY_ACCENT)
            core_bar.pack(pady=2)
            core_val = ctk.CTkLabel(core_box, text="0%", font=("Segoe UI", 12), text_color="#fff")
            core_val.pack()
            self.core_widgets.append((core_label, core_bar, core_val))

        # ========== DISK USAGE FRAME ==========
        self.disk_frame = ctk.CTkFrame(self.top_main, corner_radius=20, fg_color=FRAME_BG)
        self.disk_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        self.disk_label = ctk.CTkLabel(self.disk_frame, text="DISKS", font=("Segoe UI", 20, "bold"),
                                       text_color=PRIMARY_ACCENT, fg_color=LABEL_BG, corner_radius=10, width=360, height=30)
        self.disk_label.pack(pady=(10,5), padx=(10,10))
        self.disk_content = ctk.CTkFrame(self.disk_frame, fg_color="transparent")
        self.disk_content.pack(pady=(0,10), padx=5, fill="both", expand=True)
        self.disk_bars = {}
        for part in psutil.disk_partitions(all=False):
            if part.fstype:
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    row_frame = ctk.CTkFrame(self.disk_content, fg_color="transparent")
                    row_frame.pack(fill="x", pady=2)
                    label = ctk.CTkLabel(row_frame, text=f"{part.device}", font=("Segoe UI", 13, "bold"),
                                         text_color=SECONDARY_ACCENT, fg_color="transparent", width=60)
                    label.pack(side="left", padx=(0,5))
                    bar = ctk.CTkProgressBar(row_frame, width=140, height=14, corner_radius=7, progress_color=PRIMARY_ACCENT)
                    bar.pack(side="left", padx=(0,5))
                    bar.set(usage.percent/100)
                    size_label = ctk.CTkLabel(row_frame,
                        text=f"{self.format_size(usage.free)} free / {self.format_size(usage.total)}",
                        font=("Segoe UI", 12), text_color="#fff", fg_color="transparent")
                    size_label.pack(side="left", padx=(0,5))
                    self.disk_bars[part.device] = (bar, size_label, part.mountpoint)
                except Exception:
                    continue

        # ========== RAM, TIME, UPTIME ==========
        self.info_frame = ctk.CTkFrame(self, width=780, height=50, corner_radius=20, fg_color=FRAME_BG)
        self.info_frame.place(x=10, y=230)
        self.ram_label = ctk.CTkLabel(self.info_frame, text="RAM", font=("Segoe UI", 15, "bold"),
                                      text_color=PRIMARY_ACCENT, fg_color=LABEL_BG, corner_radius=10, width=80, height=30)
        self.ram_label.place(x=10, y=10)
        self.ram_bar = ctk.CTkProgressBar(self.info_frame, width=180, height=16, corner_radius=8, progress_color=SECONDARY_ACCENT)
        self.ram_bar.place(x=100, y=16)
        self.ram_val = ctk.CTkLabel(self.info_frame, text="0%", font=("Segoe UI", 15), text_color="#fff", fg_color="transparent")
        self.ram_val.place(x=290, y=10)

        self.time_label = ctk.CTkLabel(self.info_frame, text="--:--:--", font=("Segoe UI", 13), text_color="white", fg_color="transparent")
        self.time_label.place(x=400, y=10)
        self.uptime_label = ctk.CTkLabel(self.info_frame, text="Uptime: --:--:--", font=("Segoe UI", 13), text_color="white", fg_color="transparent")
        self.uptime_label.place(x=570, y=10)

        # ========== GPU USAGE ==========
        self.gpu_frame = ctk.CTkFrame(self, width=780, height=50, corner_radius=20, fg_color=FRAME_BG)
        self.gpu_frame.place(x=10, y=290)
        self.gpu_labels = []

        # ========== GRAPH FRAME ==========
        self.graph_frame = ctk.CTkFrame(self, width=780, height=180, corner_radius=20, fg_color=FRAME_BG)
        self.graph_frame.place(x=10, y=350)

        # ========== GRAPH DATA & PLOT ==========
        self.cpu_history = deque([0]*60, maxlen=60)
        self.gpu_history = deque([0]*60, maxlen=60)
        self.time_history = deque([i for i in range(-59, 1)], maxlen=60)

        self.fig, self.ax = plt.subplots(figsize=(7.5, 1.1), dpi=100)
        self.cpu_line, = self.ax.plot(self.time_history, self.cpu_history, label="CPU", color=PRIMARY_ACCENT)
        self.gpu_line, = self.ax.plot(self.time_history, self.gpu_history, label="GPU", color=SECONDARY_ACCENT)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(-59, 0)
        self.ax.set_yticks([0, 25, 50, 75, 100])
        self.ax.set_ylabel("")
        self.ax.set_xlabel("Seconds Ago")
        self.ax.legend(loc="upper center", fontsize=8)
        self.ax.set_facecolor(FRAME_BG)
        self.fig.patch.set_facecolor(FRAME_BG)
        self.ax.tick_params(axis='x', colors=FRAME_BG)
        self.ax.tick_params(axis='y', colors='white')
        
        legend_handles = [
            Line2D([0], [1], color=PRIMARY_ACCENT, lw=1, label="CPU"),
            Line2D([0], [1], color=SECONDARY_ACCENT, lw=1, label="GPU")
        ]

        self.ax.legend(handles=legend_handles, loc="center left", bbox_to_anchor=(1.005, 0.5), fontsize=8, borderaxespad=0.)
        self.ax.yaxis.label.set_color(FRAME_BG)
        self.ax.xaxis.label.set_color(FRAME_BG)
        for spine in self.ax.spines.values():
            spine.set_color(FRAME_BG)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=10)

        self.update_stats()

    def keep_in_place(self, event):
        geo = self.geometry()
        m = re.match(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)', geo)
        if m:
            w, h, x, y = map(int, m.groups())
            if x != self.fixed_x or y != self.fixed_y:
                self.geometry(f"{w}x{h}+{self.fixed_x}+{self.fixed_y}")

    def format_size(self, bytes):
        gb = bytes / (1024 ** 3)
        return f"{gb:.1f}GB"

    def update_stats(self):
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        per_cpu = psutil.cpu_percent(percpu=True)
        self.cpu_label.configure(text=f"CPU USAGE: {cpu_percent}%")
        for i, (core, widgets) in enumerate(zip(per_cpu, self.core_widgets)):
            _, bar, val = widgets
            bar.set(core/100)
            val.configure(text=f"{core:.0f}%")
            bar.configure(progress_color=self.get_usage_color(core))

        # RAM
        ram = psutil.virtual_memory().percent
        self.ram_bar.set(ram/100)
        self.ram_val.configure(text=f"{ram:.0f}%")

        # Time & Uptime
        self.time_label.configure(text=f"Time: {time.strftime('%H:%M:%S')}")
        uptime = int(time.time() - psutil.boot_time())
        self.uptime_label.configure(text=f"Uptime: {time.strftime('%H:%M:%S', time.gmtime(uptime))}")

        # Disks
        for device, (bar, label, mount) in self.disk_bars.items():
            try:
                usage = psutil.disk_usage(mount)
                bar.set(usage.percent/100)
                label.configure(
                    text=f"{self.format_size(usage.free)} free / {self.format_size(usage.total)}"
                )
            except Exception:
                continue

       # GPU
        gpus = GPUtil.getGPUs()
        gpu_percent = 0

        for idx, gpu in enumerate(gpus):
            gpu_percent = gpu.load * 100
            gpu_text = (
                f"GPU {gpu.id} ({gpu.name}): {gpu.load*100:.1f}% | "
                f"{gpu.memoryUsed}/{gpu.memoryTotal} MB | Temp: {gpu.temperature}°C"
            )

            if idx < len(self.gpu_labels):
                glabel = self.gpu_labels[idx]
                glabel.configure(text=gpu_text, text_color=PRIMARY_ACCENT)
                glabel.place(x=15, y=10 + idx * 35)
            else:
                glabel = ctk.CTkLabel(self.gpu_frame, text=gpu_text, font=("Segoe UI", 14, "bold"),
                                    text_color=PRIMARY_ACCENT, fg_color=LABEL_BG,
                                    corner_radius=10, width=750, height=28)
                glabel.place(x=15, y=10 + idx * 35)
                self.gpu_labels.append(glabel)

        # Hide extra labels if fewer GPUs are detected now
        for idx in range(len(gpus), len(self.gpu_labels)):
            self.gpu_labels[idx].place_forget()

        # If no GPUs detected, show fallback
        if not gpus:
            if not self.gpu_labels:
                glabel = ctk.CTkLabel(self.gpu_frame, text="No NVIDIA GPU detected.",
                                    font=("Segoe UI", 14, "bold"), text_color="#888",
                                    fg_color=LABEL_BG, corner_radius=10, width=750, height=28)
                glabel.place(x=15, y=10)
                self.gpu_labels.append(glabel)
            else:
                self.gpu_labels[0].configure(text="No NVIDIA GPU detected.", text_color="#888")
                self.gpu_labels[0].place(x=15, y=10)

            # Hide others if any
            for idx in range(1, len(self.gpu_labels)):
                self.gpu_labels[idx].place_forget()

            gpu_percent = 0


        # ===== Update Graph Data =====
        self.cpu_history.append(cpu_percent)
        self.gpu_history.append(gpu_percent)
        self.cpu_line.set_ydata(self.cpu_history)
        self.gpu_line.set_ydata(self.gpu_history)
        self.canvas.draw()

        self.after(1000, self.update_stats)

    def get_usage_color(self, percentage):
        if percentage < 50: return PRIMARY_ACCENT
        elif percentage < 75: return "#ffb300"
        else: return "#ff1744"

if __name__ == "__main__":
    app = SystemMonitor()
    app.mainloop()
