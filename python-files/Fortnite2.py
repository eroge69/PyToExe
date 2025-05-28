import tkinter as tk

def launch():
    # Clear window
    for widget in root.winfo_children():
        widget.destroy()
    # Show loading text
    loading_label = tk.Label(root, text="Deleting windows", fg="white", bg="black", font=("Arial", 30))
    loading_label.pack(expand=True)
    # After 3 seconds, show black screen
    root.after(3000, show_black_screen)

def show_black_screen():
    # Clear window again
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg="black")
    root.attributes("-fullscreen", True)

def on_key(event):
    if event.keysym == 'BackSpace':
        root.destroy()

root = tk.Tk()
root.title("Fortnite 2")
root.geometry("400x200")
root.configure(bg="gray20")

launch_button = tk.Button(root, text="Launch Fortnite 2", font=("Arial", 20), command=launch)
launch_button.pack(expand=True)

root.bind("<Key>", on_key)

root.mainloop()
