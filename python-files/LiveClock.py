
import tkinter as tk
from time import strftime

root = tk.Tk()
root.title("Live Clock")
root.geometry("250x100")
root.resizable(False, False)

label = tk.Label(root, font=("Helvetica", 36), background="black", foreground="cyan")
label.pack(fill="both", expand=1)

def time():
    string = strftime('%H:%M:%S')
    label.config(text=string)
    label.after(1000, time)

time()
root.mainloop()
