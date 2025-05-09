import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class MetroUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Metro UI")
        self.geometry("320x520")
        self.configure(bg="black")
        self.resizable(False, False)

        # Status bar
        time_label = tk.Label(self, text=datetime.now().strftime("%H:%M"),
                              fg="white", bg="black", font=("Segoe UI", 10))
        time_label.place(x=10, y=10)

        signal_label = tk.Label(self, text="📶 🔋",
                                fg="white", bg="black", font=("Segoe UI", 10))
        signal_label.place(x=240, y=10)

        # Tiles
        tile_size = 120
        padding = 10
        start_y = 40

        self.add_tile("📞", "Phone", "dodger blue", padding, start_y, self.phone_click)
        self.add_tile("💬", "Messages", "orange", tile_size + 2 * padding, start_y, self.messages_click)
        self.add_tile("📷", "Camera", "medium purple", padding, start_y + tile_size + padding, self.camera_click)

    def add_tile(self, emoji, label, color, x, y, command):
        btn = tk.Button(self, text=f"{emoji}\n{label}",
                        bg=color, fg="white",
                        font=("Segoe UI", 12, "bold"),
                        width=10, height=5,
                        command=command,
                        relief="flat")
        btn.place(x=x, y=y)

    def phone_click(self):
        messagebox.showinfo("Phone", "Phone app launched!")

    def messages_click(self):
        messagebox.showinfo("Messages", "Messages app launched!")

    def camera_click(self):
        messagebox.showinfo("Camera", "Camera app launched!")


if __name__ == "__main__":
    app = MetroUI()
    app.mainloop()
