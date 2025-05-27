import win32gui
import win32con
import win32api
import time
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard
from threading import Thread, Lock
from collections import defaultdict
from queue import Queue, Empty

KEYBOARD_LAYOUT = [
    ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
    ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
    ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'Enter'],
    ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
    ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Win', 'Menu', 'Ctrl']
]

class VisualKeyboard(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.key_boxes = {}
        self.key_colors = {
            'default': '#e0e0e0',
            'active': '#ff9999',
            'modifier': '#99ccff'
        }
        self.key_width = 42
        self.key_height = 48
        self.spacing = 4
        self.build_keyboard()
        self.update_queue = Queue()
        self.after(3, self.process_updates)

    def build_keyboard(self):
        row_y = 0
        for row in KEYBOARD_LAYOUT:
            x = 0
            for key in row:
                width = self.get_key_width(key)
                fill = self.get_key_color(key)
                
                key_id = self.create_rectangle(
                    x, row_y, x + width - self.spacing, row_y + self.key_height - self.spacing,
                    fill=fill, outline='#999999', width=1
                )
                self.key_boxes[self.normalize_key_name(key)] = key_id
                self.create_text(
                    x + (width - self.spacing)/2, row_y + (self.key_height - self.spacing)/2,
                    text=key, font=('Arial', 10, 'bold')
                )
                x += width
            row_y += self.key_height + self.spacing

    def process_updates(self):
        try:
            while True:
                key_name, state = self.update_queue.get_nowait()
                self._update_key(key_name, state)
        except Empty:
            pass
        self.after(3, self.process_updates)

    def _update_key(self, key_name, state):
        key_name = self.normalize_key_name(key_name)
        if key_name not in self.key_boxes:
            return

        new_color = self.key_colors['active'] if state else self.get_key_color(key_name)
        self.itemconfig(self.key_boxes[key_name], fill=new_color)

    def update_key(self, key_name, is_pressed):
        self.update_queue.put((key_name, is_pressed))

    def get_key_width(self, key):
        widths = {
            'Backspace': 2.2, 'Tab': 1.5, '\\': 1.5, 'Caps': 1.8,
            'Enter': 2.2, 'Shift': 2.5, 'Ctrl': 1.5, 'Alt': 1.5,
            'Win': 1.5, 'Menu': 1.5, 'Space': 6.5
        }
        return widths.get(key, 1) * self.key_width

    def get_key_color(self, key):
        modifiers = ['Shift', 'Ctrl', 'Alt', 'Win', 'Menu', 'Caps']
        return self.key_colors['modifier'] if key in modifiers else self.key_colors['default']

    def normalize_key_name(self, name):
        specials = {
            'caps lock': 'caps', 'shift_r': 'shift', 'shift_l': 'shift',
            'ctrl_r': 'ctrl', 'ctrl_l': 'ctrl', 'alt_r': 'alt', 'alt_l': 'alt',
            'cmd': 'win', 'space': 'space', 'backspace': 'backspace',
            'enter': 'enter', 'tab': 'tab', 'esc': 'esc'
        }
        return specials.get(name.lower(), name.split('_')[0].lower())

class WindowSelector:
    def __init__(self):
        self.selected_windows = []
        self.listener = None
        self.hotkey_listener = None
        self.is_duplicating = False
        self.active_window_hwnd = None
        
        self.root = tk.Tk()
        self.root.title("Keyboard Duplicator Pro")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_ui()
        self.populate_window_list()
        self.start_hotkey_listener()

    def start_hotkey_listener(self):
        def on_hotkey():
            if self.root.winfo_exists():
                self.root.after(0, self.toggle_duplication)

        def listen_hotkeys():
            with keyboard.GlobalHotKeys({'<F6>': on_hotkey}) as listener:
                self.hotkey_listener = listener
                listener.join()

        hotkey_thread = Thread(target=listen_hotkeys, daemon=True)
        hotkey_thread.start()

    def toggle_duplication(self):
        if self.is_duplicating:
            self.stop_duplication()
        else:
            self.start_duplication()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(
            list_frame, 
            width=80, 
            height=15,
            selectmode=tk.MULTIPLE
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.keyboard = VisualKeyboard(main_frame, width=1000, height=300, bg='white')
        self.keyboard.pack(pady=10)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        self.btn_start = ttk.Button(
            control_frame,
            text="Start",
            command=self.start_duplication,
            state=tk.DISABLED
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = ttk.Button(
            control_frame,
            text="Stop",
            command=self.stop_duplication,
            state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Refresh", command=self.populate_window_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Exit", command=self.on_close).pack(side=tk.RIGHT, padx=5)

        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X)
        self.update_status("Ready")

    def get_windows(self):
        windows = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append((hwnd, title))
        win32gui.EnumWindows(callback, None)
        return windows

    def populate_window_list(self):
        self.listbox.delete(0, tk.END)
        windows = self.get_windows()
        for hwnd, title in windows:
            self.listbox.insert(tk.END, f"{title[:60]}... (Handle: {hwnd})")
        self.window_list = windows
        self.btn_start.config(state=tk.NORMAL if windows else tk.DISABLED)

    def start_duplication(self):
        if not self.listbox.curselection():
            messagebox.showwarning("Error", "Select at least one window first!")
            return
            
        if not self.is_duplicating:
            selections = self.listbox.curselection()
            self.selected_windows = [self.window_list[i] for i in selections]
            self.is_duplicating = True
            
            self.duplicator = KeyDuplicator(
                [hwnd for hwnd, title in self.selected_windows],
                self.keyboard
            )
            self.listener = keyboard.Listener(
                on_press=self.duplicator.on_press,
                on_release=self.duplicator.on_release,
                suppress=False
            )
            
            self.listener.start()
            self.update_controls(True)
            self.update_status(f"Active: {len(self.selected_windows)} windows (F6 to stop)")

    def stop_duplication(self):
        if self.is_duplicating:
            if self.listener and self.listener.is_alive():
                self.listener.stop()
            self.is_duplicating = False
            self.update_controls(False)
            self.update_status("Stopped (F6 to start)")

    def update_controls(self, is_running):
        state = tk.DISABLED if is_running else tk.NORMAL
        self.btn_start.config(state=state)
        self.btn_stop.config(state=tk.NORMAL if is_running else tk.DISABLED)
        self.listbox.config(state=tk.DISABLED if is_running else tk.NORMAL)

    def update_status(self, message):
        self.status_var.set(f"Status: {message}")

    def on_close(self):
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        self.stop_duplication()
        self.root.destroy()

class KeyDuplicator:
    def __init__(self, hwnd_list, keyboard_widget):
        self.hwnd_list = hwnd_list
        self.keyboard = keyboard_widget
        self.active_keys = defaultdict(bool)
        self.modifiers = defaultdict(bool)
        self.event_queue = Queue()
        self.lock = Lock()
        self.worker = Thread(target=self.process_events)
        self.worker.daemon = True
        self.worker.start()

        self.key_map = {
            'ctrl_l': win32con.VK_CONTROL,
            'ctrl_r': win32con.VK_CONTROL,
            'alt_l': win32con.VK_MENU,
            'alt_r': win32con.VK_MENU,
            'shift_l': win32con.VK_SHIFT,
            'shift_r': win32con.VK_SHIFT,
            'cmd_l': win32con.VK_LWIN,
            'cmd_r': win32con.VK_RWIN
        }

    def get_virtual_key(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                return win32api.VkKeyScan(key.char)
            elif hasattr(key, 'name'):
                return self.key_map.get(key.name, getattr(win32con, f'VK_{key.name.upper()}', 0))
            return 0
        except Exception as e:
            print(f"Key error: {e}")
            return 0

    def process_events(self):
        while True:
            try:
                event = self.event_queue.get(timeout=0.01)
                hwnd, vk_code, is_pressed = event
                
                current_active_hwnd = win32gui.GetForegroundWindow()
                targets = [h for h in self.hwnd_list if h != current_active_hwnd]

                with self.lock:
                    if is_pressed:
                        self.active_keys[vk_code] = True
                    else:
                        if vk_code in self.active_keys:
                            del self.active_keys[vk_code]

                    for target_hwnd in targets:
                        scan_code = win32api.MapVirtualKey(vk_code, 0)
                        flags = 0 if is_pressed else win32con.KEYEVENTF_KEYUP
                        win32api.SendMessage(
                            target_hwnd,
                            win32con.WM_KEYDOWN if is_pressed else win32con.WM_KEYUP,
                            vk_code,
                            (scan_code << 16) | flags
                        )

            except Empty:
                continue
            except Exception as e:
                print(f"Processing error: {e}")

    def on_press(self, key):
        try:
            vk_code = self.get_virtual_key(key)
            if vk_code == 0:
                return

            key_name = key.char if hasattr(key, 'char') else key.name
            self.keyboard.update_key(key_name, True)

            for hwnd in self.hwnd_list:
                self.event_queue.put((hwnd, vk_code, True))

        except Exception as e:
            print(f"Press error: {e}")

    def on_release(self, key):
        try:
            vk_code = self.get_virtual_key(key)
            if vk_code == 0:
                return

            key_name = key.char if hasattr(key, 'char') else key.name
            self.keyboard.update_key(key_name, False)

            for hwnd in self.hwnd_list:
                self.event_queue.put((hwnd, vk_code, False))

        except Exception as e:
            print(f"Release error: {e}")

if __name__ == "__main__":
    app = WindowSelector()
    app.root.mainloop()