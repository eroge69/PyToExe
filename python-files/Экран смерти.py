import tkinter as tk
import time
import threading

def fake_bsod():
    root = tk.Tk()
    root.configure(bg="#0078d7")
    root.attributes("-fullscreen", True)
    root.config(cursor="none")
    root.title("")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    percent_var = tk.StringVar(value="0")

    static_text = (
        "Your PC ran into a problem and needs to restart. We're just\n"
        "collecting some error info, and then we'll restart for you. ({}% complete)\n\n"
        "If you'd like to know more, you can search online later for this error: HAL_INITIALIZATION_FAILED"
    )

    bsod_face = tk.Label(
        root,
        text=":(",
        fg="white",
        bg="#0078d7",
        font=("Segoe UI", 80, "bold"),
        justify="center"
    )
    bsod_face.place(relx=0.5, rely=0.25, anchor="center")

    bsod_text = tk.Label(
        root,
        text=static_text.format(percent_var.get()),
        fg="white",
        bg="#0078d7",
        font=("Segoe UI", 22),
        justify="center"
    )
    bsod_text.place(relx=0.5, rely=0.45, anchor="n")

    restarting_label = tk.Label(
        root,
        text="Restarting...",
        fg="white",
        bg="#0078d7",
        font=("Segoe UI", 26),
        justify="center"
    )

    def update_percent():
        for i in range(1, 101):
            percent_var.set(str(i))
            bsod_text.config(text=static_text.format(percent_var.get()))
            time.sleep(0.05)
        # Переход на фейковый "Restarting..."
        bsod_face.place_forget()
        bsod_text.place_forget()
        restarting_label.place(relx=0.5, rely=0.5, anchor="center")
        time.sleep(3)
        root.destroy()

    def close(event=None):
        root.destroy()

    root.bind("<Escape>", close)

    threading.Thread(target=update_percent, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    fake_bsod()
