
import tkinter as tk
from tkinter import messagebox
import threading
import time
import pyautogui
from pynput.mouse import Listener as MouseListener, Button

class AutoClicker:
    def __init__(self, root):
        self.running = False
        self.clicks_per_sec = 100
        self.trigger_button = Button.x_button1  # Mouse Button 6
        self.click_button = 'xbutton1'

        self.label_status = tk.Label(root, text="status: idle")
        self.label_status.pack()

        self.start_button = tk.Button(root, text="STOP!", command=self.toggle_clicking)
        self.start_button.pack()

        self.help_button = tk.Button(root, text="Help", command=self.show_help)
        self.help_button.pack()

        root.protocol("WM_DELETE_WINDOW", self.close)
        self.mouse_listener = MouseListener(on_click=self.on_click)
        self.mouse_listener.start()

    def show_help(self):
        messagebox.showinfo("Help", "AutoClicker will start clicking when Mouse Button 6 (side front button) is clicked.")

    def toggle_clicking(self):
        self.running = not self.running
        self.label_status.config(text="status: running" if self.running else "status: idle")
        if self.running:
            threading.Thread(target=self.click_loop, daemon=True).start()

    def click_loop(self):
        interval = 1.0 / self.clicks_per_sec
        while self.running:
            pyautogui.click(button=self.click_button)
            time.sleep(interval)

    def on_click(self, x, y, button, pressed):
        if button == self.trigger_button and pressed:
            self.toggle_clicking()

    def close(self):
        self.running = False
        self.mouse_listener.stop()
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("FastClicker Clone")
    app = AutoClicker(root)
    root.mainloop()
