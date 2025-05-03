import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import keyboard
from pynput.mouse import Button, Controller

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Set application icon (can be customized)
        try:
            self.root.iconbitmap("mouse.ico")  # Add your own icon file if available
        except:
            pass
        
        # Variables
        self.is_running = False
        self.click_thread = None
        self.total_clicks = 0
        self.mouse = Controller()
        self.hotkey = "F6"  # Default hotkey
        self.click_interval = tk.IntVar(value=100)  # Default interval in ms
        self.selected_button = tk.StringVar(value="left")
        
        # Configure style
        style = ttk.Style()
        style.configure("TButton", padding=5, font=('Segoe UI', 10))
        style.configure("TRadiobutton", font=('Segoe UI', 10))
        style.configure("TLabel", font=('Segoe UI', 10))
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Auto Clicker", font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Mouse button selection
        button_frame = ttk.LabelFrame(main_frame, text="Mouse Button", padding="10 10 10 10")
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Radiobutton(button_frame, text="Left Click", variable=self.selected_button, value="left").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(button_frame, text="Right Click", variable=self.selected_button, value="right").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(button_frame, text="Middle Click", variable=self.selected_button, value="middle").pack(anchor=tk.W, pady=2)
        
        # Click interval
        interval_frame = ttk.LabelFrame(main_frame, text="Click Interval (ms)", padding="10 10 10 10")
        interval_frame.pack(fill=tk.X, pady=10)
        
        interval_scale = ttk.Scale(
            interval_frame, 
            from_=10, 
            to=2000, 
            orient=tk.HORIZONTAL, 
            variable=self.click_interval,
            command=lambda val: interval_value.config(text=f"{int(float(val))} ms")
        )
        interval_scale.pack(fill=tk.X, pady=5)
        
        interval_value = ttk.Label(interval_frame, text=f"{self.click_interval.get()} ms")
        interval_value.pack()
        
        # Hotkey settings
        hotkey_frame = ttk.LabelFrame(main_frame, text="Hotkey Settings", padding="10 10 10 10")
        hotkey_frame.pack(fill=tk.X, pady=10)
        
        self.hotkey_label = ttk.Label(hotkey_frame, text=f"Current hotkey: {self.hotkey}")
        self.hotkey_label.pack(pady=5)
        
        hotkey_button = ttk.Button(hotkey_frame, text="Change Hotkey", command=self.change_hotkey)
        hotkey_button.pack(fill=tk.X, pady=5)
        
        # Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10 10 10 10")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.clicks_label = ttk.Label(stats_frame, text=f"Total clicks: {self.total_clicks}")
        self.clicks_label.pack(pady=5)
        
        # Control buttons
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(controls_frame, text="Start (F6)", command=self.toggle_clicking)
        self.start_button.pack(fill=tk.X, pady=5)
        
        reset_button = ttk.Button(controls_frame, text="Reset Counter", command=self.reset_counter)
        reset_button.pack(fill=tk.X, pady=5)
        
        # Status
        self.status_var = tk.StringVar(value="Status: Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=('Segoe UI', 9))
        status_label.pack(side=tk.BOTTOM, pady=10)
        
        # Set up hotkey listener
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
        
        # Clean up on exit
        root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def toggle_clicking(self):
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def start_clicking(self):
        if self.is_running:
            return
            
        self.is_running = True
        self.start_button.config(text=f"Stop ({self.hotkey})")
        self.status_var.set("Status: Running")
        
        # Start clicking in a separate thread
        self.click_thread = threading.Thread(target=self.perform_clicks)
        self.click_thread.daemon = True
        self.click_thread.start()
    
    def stop_clicking(self):
        self.is_running = False
        self.start_button.config(text=f"Start ({self.hotkey})")
        self.status_var.set("Status: Stopped")
    
    def perform_clicks(self):
        # Determine which mouse button to click
        button_map = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle
        }
        button = button_map.get(self.selected_button.get(), Button.left)
        
        # Click loop
        while self.is_running:
            self.mouse.click(button)
            self.total_clicks += 1
            self.clicks_label.config(text=f"Total clicks: {self.total_clicks}")
            time.sleep(self.click_interval.get() / 1000)  # Convert ms to seconds
    
    def reset_counter(self):
        self.total_clicks = 0
        self.clicks_label.config(text=f"Total clicks: {self.total_clicks}")
    
    def change_hotkey(self):
        # Create a simple dialog for hotkey change
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Hotkey")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Press the key you want to use:").pack(pady=(0, 10))
        
        key_var = tk.StringVar()
        key_entry = ttk.Entry(frame, textvariable=key_var, font=('Segoe UI', 12), justify='center')
        key_entry.pack(pady=10, fill=tk.X)
        key_entry.focus()
        
        def on_key_press(e):
            if e.keysym in ('Escape', 'Return'):
                dialog.destroy()
                return
                
            # Remove old hotkey
            try:
                keyboard.remove_hotkey(self.hotkey)
            except:
                pass
                
            # Set new hotkey
            self.hotkey = e.keysym
            keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
            self.hotkey_label.config(text=f"Current hotkey: {self.hotkey}")
            self.start_button.config(text=f"Start ({self.hotkey})" if not self.is_running else f"Stop ({self.hotkey})")
            dialog.destroy()
        
        dialog.bind("", on_key_press)
    
    def on_close(self):
        try:
            keyboard.remove_hotkey(self.hotkey)
        except:
            pass
        self.stop_clicking()
        self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AutoClickerApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")