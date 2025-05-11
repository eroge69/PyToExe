import os
import time
from datetime import datetime
import pyautogui
from pynput import mouse, keyboard
import tkinter as tk
from tkinter import ttk

class MacroRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Macro Recorder")
        self.root.geometry("300x200")

        self.actions = []
        self.is_recording = False
        self.last_action_time = None

        # GUI Elements
        self.status_label = ttk.Label(root, text="Status: Idle")
        self.status_label.pack(pady=10)

        self.record_button = ttk.Button(root, text="Record", command=self.toggle_recording)
        self.record_button.pack(pady=5)

        self.replay_button = ttk.Button(root, text="Replay", command=self.playback, state="disabled")
        self.replay_button.pack(pady=5)

        self.exit_button = ttk.Button(root, text="Exit", command=root.quit)
        self.exit_button.pack(pady=5)

        # Set up directory
        self.screenshot_dir = os.path.join(os.getcwd(), 'screenshots')
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

        # Mouse and Keyboard Listeners
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def on_click(self, x, y, button, pressed):
        if self.is_recording and pressed and button == mouse.Button.left:
            current_time = time.time()
            delay = 0 if self.last_action_time is None else current_time - self.last_action_time
            self.actions.append({'type': 'click', 'position': (x, y), 'delay': delay})
            self.last_action_time = current_time

    def on_press(self, key):
        if self.is_recording and hasattr(key, 'char') and key.char == 's':
            current_time = time.time()
            delay = 0 if self.last_action_time is None else current_time - self.last_action_time
            self.actions.append({'type': 'screenshot', 'delay': delay})
            self.last_action_time = current_time

    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.actions.clear()
            self.last_action_time = None
            self.status_label.config(text="Status: Recording")
            self.record_button.config(text="Stop Recording")
            self.replay_button.config(state="disabled")
        else:
            self.status_label.config(text="Status: Idle")
            self.record_button.config(text="Record")
            self.replay_button.config(state="normal")

    def playback(self):
        if not self.actions:
            self.status_label.config(text="Status: No actions recorded")
            return
        self.status_label.config(text="Status: Playing...")
        self.root.update()
        for action in self.actions:
            time.sleep(action['delay'])
            if action['type'] == 'click':
                pyautogui.click(action['position'][0], action['position'][1])
            elif action['type'] == 'screenshot':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"screenshot_{timestamp}.png"
                image = pyautogui.screenshot()
                image.save(os.path.join(self.screenshot_dir, filename))
        self.status_label.config(text="Status: Idle")

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroRecorder(root)
    root.mainloop()