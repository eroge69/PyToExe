import tkinter as tk
from tkinter import messagebox

PASSWORD = "AP"

def check_password():
    if entry.get() == PASSWORD:
        root.destroy()
    else:
        messagebox.showerror("Error", "Incorrect Password")
        entry.delete(0, tk.END)

root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="black")

label = tk.Label(root, text="🔒 Locked. Enter Password to Unlock", font=("Arial", 24), fg="white", bg="black")
label.pack(pady=20)

entry = tk.Entry(root, show="*", font=("Arial", 24), justify="center")
entry.pack(pady=10)
entry.focus_set()

button = tk.Button(root, text="Unlock", font=("Arial", 20), command=check_password)
button.pack(pady=20)

root.protocol("WM_DELETE_WINDOW", lambda: None)
root.bind("<Alt-F4>", lambda e: "break")

root.mainloop()
