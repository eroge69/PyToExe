import tkinter as tk

def calculate():
    try:
        result.set(eval(entry.get()))
    except:
        result.set("Error")

root = tk.Tk()
root.title("Calc")

entry = tk.Entry(root, width=20)
entry.pack()

result = tk.StringVar()
tk.Label(root, textvariable=result).pack()

tk.Button(root, text="=", command=calculate).pack()

root.mainloop()
