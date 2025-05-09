import tkinter as tk
from tkinter import simpledialog, messagebox

def zapytaj_o_wiek():
    wiek = simpledialog.askinteger("Question", "How old are you?")
    if wiek is not None:
        messagebox.showinfo("I think...", f"I think... you are {wiek} years old!")

okno = tk.Tk()
okno.title("I will guess how old are you!")

label = tk.Label(okno, text="I will guess how old are you!", font=("Arial", 16))
label.pack(pady=20)

przycisk = tk.Button(okno, text="OK", command=zapytaj_o_wiek)
przycisk.pack(pady=10)

okno.mainloop()