
import tkinter as tk
from time import strftime

def time():
    string = strftime('%I:%M:%S %p')  # 12-hour format with AM/PM
    label.config(text=string)
    label.after(1000, time)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Live Clock")
    root.geometry("300x120")
    root.resizable(False, False)
    root.attributes("-topmost", True)  # Always on top

    label = tk.Label(root, font=("Helvetica", 36), background="black", foreground="cyan")
    label.pack(fill="both", expand=1)

    time()
    root.mainloop()
