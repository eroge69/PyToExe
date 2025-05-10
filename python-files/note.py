import tkinter as tk

# Create main window
root = tk.Tk()
root.overrideredirect(True)  # Remove title bar
root.geometry("70x70+200+200")  # Smaller default size
root.configure(bg="white")

# Functions to allow window dragging
def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

# Resizer
resizer = tk.Frame(root, bg="white", cursor="bottom_right_corner")
resizer.place(relx=1.0, rely=1.0, anchor="se", width=10, height=10)

def resize_window(event):
    new_width = event.x_root - root.winfo_rootx()
    new_height = event.y_root - root.winfo_rooty()
    if new_width > 200 and new_height > 100:
        root.geometry(f"{new_width}x{new_height}")

resizer.bind("<B1-Motion>", resize_window)

# Close button (top-left) - visually subtle
close_btn = tk.Button(root, text="X", command=root.destroy,
                      bg="white", fg="black", bd=0, highlightthickness=0,
                      font=("Arial", 10, "bold"), activebackground="white", activeforeground="white")
close_btn.place(x=5, y=5, width=20, height=20)

# Text area
text_area = tk.Text(root, wrap="word", bg="white", fg="black",
                    insertbackground="black", undo=True, bd=0)
text_area.pack(expand=1, fill="both", padx=10, pady=(30, 10))  # Space for close button

# Right-click menu
context_menu = tk.Menu(root, tearoff=0, bg="white", fg="black")
context_menu.add_command(label="Copy", command=lambda: text_area.event_generate("<<Copy>>"))
context_menu.add_command(label="Paste", command=lambda: text_area.event_generate("<<Paste>>"))
text_area.bind("<Button-3>", lambda event: context_menu.tk_popup(event.x_root, event.y_root))

# Make window draggable
root.bind("<Button-1>", start_move)
root.bind("<B1-Motion>", do_move)

# Run the app
root.mainloop()
