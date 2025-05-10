from tkinter import messagebox, Tk

root = Tk()
root.withdraw()

question = messagebox.askyesno("The Question","Are you a furry?")

if question:
    messagebox.showinfo(title="The Question", message="Haha!")
else:
    messagebox.showinfo(title="The Question", message="Sure buddy...")

