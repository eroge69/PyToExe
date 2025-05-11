import time
import threading
import ctypes
import tkinter as tk

user32 = ctypes.WinDLL("user32", use_last_error=True)

MOUSE_DOWN, MOUSE_UP = 0x0002, 0x0004
KEYEVENTF_KEYUP = 0x0002


def press_key(vk: int) -> None:
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def select_hotbar_slot(slot: int) -> None:
    if 1 <= slot <= 9:
        vk = 0x30 + slot
        press_key(vk)


TARGET_X, TARGET_Y = 977, 481
HOLD_TIME, WAIT_TIME = 0.75, 3.0
INITIAL_DELAY = 15.0
BLOCKS_PER_PICK = 130
TOTAL_SLOTS = 9


class CobbleMiner(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AFK Cobble Miner")
        self.configure(bg="#000000")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self.running = False
        self.paused = False
        self.pause_start = None
        self.count = 0
        self.start_time = None
        self.current_slot = 1

        self.header = tk.Label(
            self,
            text="AFK Cobble Miner",
            font=("Segoe UI", 22, "bold"),
            bg="#000000",
            fg="#00ff00",
        )
        self.header.pack(pady=(20, 5))

        self._rainbow_colors = [
            "#ff0000",
            "#ff7f00",
            "#ffff00",
            "#7fff00",
            "#00ff00",
            "#00ff7f",
            "#00ffff",
            "#007fff",
            "#0000ff",
            "#7f00ff",
            "#ff00ff",
            "#ff007f",
        ]
        self._rainbow_idx = 0
        self._animate_header()

        credit = tk.Label(
            self,
            text="Made by AWJ Chedder",
            font=("Segoe UI", 12, "bold"),
            bg="#000000",
            fg=self._rainbow_colors[0],
        )
        credit.pack()
        self._credit_idx = 0
        self._animate_credit(credit)

        tk.Label(
            self,
            text="⛏️  USE A STONE PICKAXE  ⛏️",
            font=("Segoe UI", 11, "bold italic"),
            fg="white",
            bg="#000000",
        ).pack(pady=(4, 6))

        self.count_label = tk.Label(
            self,
            text="Cobble Mined 0",
            font=("Segoe UI", 16, "bold"),
            fg="#00ff00",
            bg="#000000",
        )
        self.count_label.pack()
        self.time_label = tk.Label(
            self,
            text="Mining For 0m 0s",
            font=("Segoe UI", 16, "bold"),
            fg="#00ccff",
            bg="#000000",
        )
        self.time_label.pack(pady=(5, 15))

        btn_frame = tk.Frame(self, bg="#000000")
        btn_cfg = {
            "font": ("Segoe UI", 12, "bold"),
            "fg": "white",
            "bd": 0,
            "relief": "flat",
            "width": 10,
            "height": 1,
        }
        self.start_btn = tk.Button(
            btn_frame,
            text="Start",
            bg="#28a745",
            activebackground="#3ec97c",
            command=self.start,
            **btn_cfg,
        )
        self.pause_btn = tk.Button(
            btn_frame,
            text="Pause",
            bg="#ffc107",
            activebackground="#ffcf40",
            command=self.pause_resume,
            state="disabled",
            **btn_cfg,
        )
        self.stop_btn = tk.Button(
            btn_frame,
            text="Stop",
            bg="#dc3545",
            activebackground="#e76b6b",
            command=self.stop,
            state="disabled",
            **btn_cfg,
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        self.pause_btn.grid(row=0, column=1, padx=5)
        self.stop_btn.grid(row=0, column=2, padx=5)
        btn_frame.pack(pady=(0, 20))

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_reqheight()
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(ws - w)//2}+{(hs - h)//2}")

    def _animate_header(self):
        self.header.config(fg=self._rainbow_colors[self._rainbow_idx])
        self._rainbow_idx = (self._rainbow_idx + 1) % len(self._rainbow_colors)
        self.after(150, self._animate_header)

    def _animate_credit(self, widget):
        widget.config(fg=self._rainbow_colors[self._credit_idx])
        self._credit_idx = (self._credit_idx + 1) % len(self._rainbow_colors)
        self.after(200, lambda: self._animate_credit(widget))

    def _click(self, x: int, y: int, duration: float):
        user32.SetCursorPos(x, y)
        user32.mouse_event(MOUSE_DOWN, 0, 0, 0, 0)
        time.sleep(duration)
        user32.mouse_event(MOUSE_UP, 0, 0, 0, 0)

    def _update_timer(self):
        if self.running:
            if not self.paused:
                elapsed = int(time.time() - self.start_time)
                m, s = divmod(elapsed, 60)
                self.time_label.config(text=f"Mining For {m}m {s}s")
            self.after(1000, self._update_timer)

    def start(self):
        if self.running:
            return
        self.running = True
        self.paused = False
        self.count = 0
        self.current_slot = 1
        self.count_label.config(text="Cobble Mined 0")
        self.start_time = time.time()
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal", text="Pause")
        self.stop_btn.config(state="normal")

        self.after(1000, self._update_timer)
        select_hotbar_slot(1)
        threading.Thread(target=self._worker, daemon=True).start()

    def pause_resume(self):
        if not self.running:
            return
        if not self.paused:
            self.paused = True
            self.pause_start = time.time()
            self.pause_btn.config(text="Resume")
        else:
            self.start_time += time.time() - self.pause_start
            self.paused = False
            self.pause_start = None
            self.pause_btn.config(text="Pause")

    def stop(self):
        self.running = False

    def _worker(self):
        time.sleep(INITIAL_DELAY)
        mid_x = user32.GetSystemMetrics(0) // 2
        mid_y = user32.GetSystemMetrics(1) // 2
        self._click(mid_x, mid_y, HOLD_TIME)
        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue
            self._click(TARGET_X, TARGET_Y, HOLD_TIME)
            self.count += 1
            self.after(0, lambda c=self.count: self.count_label.config(text=f"Cobble Mined {c}"))
            if self.count % BLOCKS_PER_PICK == 0:
                if self.current_slot < TOTAL_SLOTS:
                    self.current_slot += 1
                    select_hotbar_slot(self.current_slot)
                else:
                    self.after(0, self.pause_resume)
            time.sleep(WAIT_TIME)
        self._reset()

    def _reset(self):
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="Pause")
        self.stop_btn.config(state="disabled")
        self.time_label.config(text="Mining For: 0m 0s")


if __name__ == "__main__":
    CobbleMiner().mainloop()
