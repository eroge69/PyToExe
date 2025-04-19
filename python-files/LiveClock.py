
import tkinter as tk
from time import strftime

def update_time():
    current_time = strftime('%I:%M:%S %p')  # 12-hour format with AM/PM
    label.config(text=current_time)
    label.after(1000, update_time)

def show_context_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)

def close_app():
    root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    root.overrideredirect(True)  # Removes window borders and title bar
    root.geometry("250x100+100+100")
    root.configure(background='black')

    label = tk.Label(root, font=("Helvetica", 36), fg="cyan", bg="black")
    label.pack(fill="both", expand=True)

    # Right-click context menu
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Exit", command=close_app)
    root.bind("<Button-3>", show_context_menu)

    update_time()
    root.mainloop()
