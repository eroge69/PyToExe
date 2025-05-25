import tkinter as tk
from tkinter import messagebox

def on_yes():
    messagebox.showinfo("Response", "I love you too 💖")
    root.destroy()

def on_little():
    messagebox.showinfo("Response", "Try harder 😏")

def on_no():
    messagebox.showinfo("Response", "Wrong answer 😤")

def main():
    global root
    root = tk.Tk()
    root.title("Love Question")
    root.geometry("400x180")
    root.eval('tk::PlaceWindow . center')

    label = tk.Label(root, text="Do you love me?", font=("Arial", 14))
    label.pack(pady=20)

    button_frame = tk.Frame(root)
    button_frame.pack()

    yes_button = tk.Button(button_frame, text="Yes", command=on_yes, width=12, bg="lightgreen")
    yes_button.grid(row=0, column=0, padx=5)

    little_button = tk.Button(button_frame, text="A Little Bit", command=on_little, width=12, bg="khaki")
    little_button.grid(row=0, column=1, padx=5)

    no_button = tk.Button(button_frame, text="No", command=on_no, width=12, bg="lightcoral")
    no_button.grid(row=0, column=2, padx=5)

    root.mainloop()

if __name__ == "__main__":
    main()