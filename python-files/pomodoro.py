import tkinter as tk
from tkinter import ttk
import math
from win10toast import ToastNotifier
from PIL import Image
import os
from pystray import Icon, MenuItem as item, Menu
def create_image():
    # Load your icon file (must be in .ico or .png format for pystray)
    return Image.open(os.path.join(os.path.dirname(__file__), "tomato.ico"))
toast = ToastNotifier()
class PomodoroApp:
    def __init__(self, root):
        self.root = root        
        self.root.protocol("WM_DELETE_WINDOW", self.safehide)
        self.root.title("Pomodoro Timer")
        self.root.configure(bg="#1e1e1e")
        self.root.bind("<Control-Shift-B>", self.emergency_break)
        self.timer_running = False
        self.paused = False
        self.remaining_sec = 0
        self.timer_id = None

        # === Work Frame ===
        self.work_frame = ttk.Frame(root, padding=20)
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 12))
        self.style.configure("TButton", font=("Segoe UI", 10))

        self.title = ttk.Label(self.work_frame, text="Pomodoro Timer", font=("Segoe UI", 24, "bold"))
        self.title.grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self.work_frame, text="Enter work minutes:").grid(row=1, column=0)
        self.minutes_var = tk.StringVar()
        self.entry = ttk.Entry(self.work_frame, textvariable=self.minutes_var, width=5, font=("Segoe UI", 12))
        self.entry.grid(row=1, column=1)

        self.timer_label = ttk.Label(self.work_frame, text="Timer: 00:00", font=("Segoe UI", 20))
        self.timer_label.grid(row=2, column=0, columnspan=2, pady=10)

        self.start_button = ttk.Button(self.work_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=3, column=0)

        self.pause_button = ttk.Button(self.work_frame, text="Pause", command=self.pause_timer, state="disabled")
        self.pause_button.grid(row=3, column=1)

        self.reset_button = ttk.Button(self.work_frame, text="Reset", command=self.reset_timer, state="disabled")
        self.reset_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.work_frame.grid()

        # === Break Frame ===
        self.break_frame = tk.Frame(root, bg="black")
        self.break_entry = None
        self.break_time_label = None
        self.break_start_btn = None
    def create_tray_icon(self):
        menu = Menu(
            item('Show', self.show_window, default=True),
            item('Early Break', self.early_break),
            item('Timer Controls', Menu(item('Pause/Resume', self.pause_timer), item('Reset', self.reset_timer), item('Add 5 Minutes', self.add_five))),
            item('Exit', self.quit_app)
        )
        self.tray_icon = Icon("pomodoro", create_image(), "Pomodoro Timer", menu)
        import threading
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
    def safehide(self):
        self.root.withdraw()
        self.create_tray_icon()
        self.update_tray_options()
    def show_window(self, _=None):
        self.root.after(0, self._show_main_window)
    def update_tray_options(self):
        # make sure stuff are enabled/disabled correctly in the TRAY
        if not self.tray_icon:
            return
        presume = "Pause" if self.timer_running and not self.paused else "Resume"
        allow_break = self.timer_running and not self.paused
        # Update the tray icon menu based on the timer state
        self.tray_icon.menu = Menu(
            item('Show', self.show_window, default=True),
            item('Early Break', self.early_break, enabled=allow_break),
            item('Timer Controls', Menu(item(presume, self.pause_timer), item('Reset', self.reset_timer), item('Add 5 Minutes', self.add_five))),
            item('Exit', self.quit_app)
        )
        self.tray_icon.update_menu()
        self.root.after(1000, self.update_tray_options)  # Update every second
    def _show_main_window(self):
        self.root.deiconify()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
            self.tray_icon = None

    def quit_app(self, _=None):
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.destroy()

    def start_timer(self):
        try:
            min = int(self.minutes_var.get())
            if min < 0:
                raise ValueError("Negative value not allowed")
            self.remaining_sec = min * 60
            self.timer_running = True
            self.paused = False
            self.root.withdraw()
            self.send_notification("Pomodoro Alert", f"Starting a {min} minute session! Have fun!")
            self.create_tray_icon()
            self.update_timer()
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.reset_button.config(state="normal")
        except ValueError:
            self.timer_label.config(text="Invalid input!")

    def pause_timer(self):
        if self.timer_running:
            self.paused = not self.paused
            if self.paused:
                self.pause_button.config(text="Resume")
                if self.tray_icon:
                    self.tray_icon.title = f"Pomodoro Timer - Paused"
                if self.timer_id:
                    self.root.after_cancel(self.timer_id)
            else:
                self.pause_button.config(text="Pause")
                self.update_timer()

    def reset_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.timer_running = False
        self.paused = False
        self.remaining_sec = 0
        self.timer_label.config(text="Timer: 00:00")
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled", text="Pause")
        self.reset_button.config(state="disabled")
        if self.tray_icon:
            self.tray_icon.title = "Pomodoro Timer"
    def add_five(self):
        if self.timer_running and not self.paused:
            self.remaining_sec += 5 * 60
            self.update_timer()
            self.send_notification("Pomodoro Alert", "Added 5 minutes to your session!")
    def update_timer(self):
        if self.timer_running and not self.paused:
            mins = self.remaining_sec // 60
            secs = self.remaining_sec % 60
            # update systray
            if self.tray_icon:
                self.tray_icon.title = f"Pomodoro Timer - {mins}:{secs:02d}"
            self.timer_label.config(text=f"Timer: {mins}:{secs:02d}")
            if self.remaining_sec == 60:
                self.send_notification("Pomodoro Alert", "1 minute remaining in your session!")

            if self.remaining_sec > 0:
                self.remaining_sec -= 1
                self.timer_id = self.root.after(1000, self.update_timer)
            else:
                self.timer_done()

    def timer_done(self):
        self.work_frame.grid_remove()
        self.show_break_screen()
    def early_break(self, event=None):
        # reset timer and run the timer done
        if self.timer_running:
            self.reset_timer()
            self.timer_done()
    def emergency_break(self, event=None):
      if self.break_frame.winfo_ismapped():
          self.end_break()
          self.send_notification("Pomodoro Alert", "Wow, are you sure you don't want a break?")	
        
    def show_break_screen(self):
        self.root.deiconify()  # Ensure the window is visible
        self.root.attributes("-fullscreen", True)
        self.break_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        tk.Label(self.break_frame, text="Time for a break!", fg="white", bg="black", font=("Segoe UI", 40, "bold")).pack(pady=40)

        tk.Label(self.break_frame, text="Enter break time (min ≥ 5):", fg="white", bg="black", font=("Segoe UI", 20)).pack()

        self.break_var = tk.StringVar()
        self.break_entry = tk.Entry(self.break_frame, textvariable=self.break_var, font=("Segoe UI", 20), width=5, justify='center')
        self.break_entry.pack(pady=10)

        self.break_time_label = tk.Label(self.break_frame, text="", fg="white", bg="black", font=("Segoe UI", 30))
        self.break_time_label.pack(pady=20)

        self.break_start_btn = tk.Button(self.break_frame, text="Start Break", font=("Segoe UI", 20), command=self.start_break)
        self.break_start_btn.pack()

    def start_break(self):
        try:
            min = int(self.break_var.get())
            if min < 5:
                raise ValueError("Minimum break is 5 minutes")
            self.break_sec = min * 60
            self.break_start_btn.destroy()
            self.update_break_timer()
        except ValueError:
            self.break_time_label.config(text="Invalid input!", fg="red")

    def update_break_timer(self):
        mins = self.break_sec // 60
        secs = self.break_sec % 60
        self.break_time_label.config(text=f"Break: {mins}:{secs:02d}", fg="white")
        if self.break_sec > 0:
            self.break_sec -= 1
            self.root.after(1000, self.update_break_timer)
        else:
            self.end_break()

    def end_break(self):
        self.break_frame.place_forget()
        self.root.attributes("-fullscreen", False)
        self.reset_timer()
        self.work_frame.grid()
        self.minutes_var.set("")

    def send_notification(self, title, message):
        toast.show_toast(title, message, duration=10, threaded=True)

# === Start App ===
root = tk.Tk()
root.attributes('-toolwindow', True)
app = PomodoroApp(root)
root.mainloop()