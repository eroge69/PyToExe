import time
import random
import threading
import tkinter as tk
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode, Key
import win32api
import win32con

# Advanced randomization settings
BASE_MIN_CPS = 14
BASE_MAX_CPS = 21
JITTER_RANGE = 0.08  # 8% timing variation
BREAK_CHANCE = 0.003  # 0.3% chance of short pause

class AdvancedAutoClicker:
    def __init__(self):
        self.mouse = Controller()
        self.running = False
        self.min_cps = BASE_MIN_CPS
        self.max_cps = BASE_MAX_CPS
        self.root = None
        self.listener = None
        self.last_click_time = 0
        self.click_count = 0
        
    def human_like_click(self):
        while self.running:
            # Advanced randomization
            base_delay = 1 / random.uniform(self.min_cps, self.max_cps)
            jitter = base_delay * random.uniform(-JITTER_RANGE, JITTER_RANGE)
            final_delay = max(0.01, base_delay + jitter)
            
            # Random short breaks (human-like)
            if random.random() < BREAK_CHANCE:
                time.sleep(random.uniform(0.05, 0.15))
                
            # Simulate human click duration
            click_duration = random.uniform(0.01, 0.03)
            
            # Perform click with realistic timing
            self.mouse.press(Button.left)
            time.sleep(click_duration)
            self.mouse.release(Button.left)
            
            # Variable sleep after click
            time.sleep(final_delay - click_duration)
            
            # Burst pattern simulation
            self.click_count += 1
            if self.click_count > random.randint(50, 150):
                time.sleep(random.uniform(0.1, 0.3))
                self.click_count = 0

    def start_stop(self):
        self.running = not self.running
        if self.running:
            threading.Thread(target=self.human_like_click, daemon=True).start()

    def create_gui(self):
        if self.root:
            self.root.destroy()
            self.root = None
            return

        self.root = tk.Tk()
        self.root.title("Minecraft Helper")
        self.root.geometry("280x180")
        self.root.resizable(False, False)
        
        # Window styling
        self.root.attributes('-alpha', 0.95)
        self.root.attributes('-topmost', 1)
        
        # CPS Control Frame
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Min CPS Slider
        tk.Label(frame, text="Min CPS:").grid(row=0, column=0, sticky="w")
        self.min_slider = tk.Scale(frame, from_=8, to=22, orient=tk.HORIZONTAL)
        self.min_slider.set(self.min_cps)
        self.min_slider.grid(row=0, column=1, sticky="ew")
        
        # Max CPS Slider
        tk.Label(frame, text="Max CPS:").grid(row=1, column=0, sticky="w")
        self.max_slider = tk.Scale(frame, from_=10, to=25, orient=tk.HORIZONTAL)
        self.max_slider.set(self.max_cps)
        self.max_slider.grid(row=1, column=1, sticky="ew")
        
        # Apply Button
        apply_btn = tk.Button(frame, text="Apply Settings", command=self.apply_settings)
        apply_btn.grid(row=2, columnspan=2, pady=10)
        
        # Status Label
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Ready")
        tk.Label(frame, textvariable=self.status_var).grid(row=3, columnspan=2)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_gui_close)
        self.root.mainloop()

    def apply_settings(self):
        self.min_cps = self.min_slider.get()
        self.max_cps = self.max_slider.get()
        self.status_var.set(f"Settings applied: {self.min_cps}-{self.max_cps} CPS")
        
    def on_gui_close(self):
        self.root.destroy()
        self.root = None

    def on_press(self, key):
        if key == KeyCode.from_char('r'):
            self.start_stop()
            if self.running:
                self.status_var.set("Status: ACTIVE (Press R to stop)")
            else:
                self.status_var.set("Status: INACTIVE (Press R to start)")
        elif key == Key.shift_r:
            self.create_gui()

    def run(self):
        with Listener(on_press=self.on_press) as self.listener:
            print("AutoClicker initialized. Press R to toggle, RShift for GUI.")
            self.listener.join()

if __name__ == "__main__":
    clicker = AdvancedAutoClicker()
    clicker.run()