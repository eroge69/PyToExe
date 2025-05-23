import tkinter as tk
import sys

def fake_bsod():
    root = tk.Tk()
    root.title("System Error")
    root.attributes("-fullscreen", True)
    root.configure(background="blue")

    label = tk.Label(
        root,
        text=(
            "Your PC ran into a problem and needs to restart.\n"
            "We're just collecting some error info, and then we'll restart for you.\n\n"
            "For more information about this issue and possible fixes, visit\n"
            "https://www.windows.com/stopcode\n\n"
            "If you call a support person, give them this info:\n"
            "Stop code: FAKE_BSOD"
        ),
        font=("Consolas", 18),
        fg="white",
        bg="blue",
        justify="left"
    )
    label.pack(expand=True)

    # دکمه خروج مخفی: Ctrl + Q
    def close(event):
        if event.state == 4 and event.keysym == 'q':  # Ctrl + Q
            sys.exit()

    root.bind("<Key>", close)
    root.mainloop()

fake_bsod()