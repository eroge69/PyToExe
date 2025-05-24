
import tkinter as tk
import sys

def create_bsod():
    root = tk.Tk()
    root.configure(bg="#0078D7")
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    root.overrideredirect(True)

    text = (
        ":(\n\n"
        "Your PC ran into a problem and needs to restart.\n"
        "We're just collecting some error info, and then we'll restart for you.\n\n"
        "If you'd like to know more, you can search online later for this error:\n"
        "DELL_REBOOT_TRIGGERED"
    )

    label = tk.Label(
        root, text=text,
        font=("Segoe UI", 24),
        fg="white", bg="#0078D7",
        justify="left", anchor="nw", padx=100, pady=100
    )
    label.pack(expand=True, fill="both")

    root.bind("<Key>", lambda e: sys.exit())
    root.bind("<Button>", lambda e: sys.exit())

    root.mainloop()

create_bsod()
