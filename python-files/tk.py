import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont

def main():
    root = tk.Tk()
    root.title("Min Tkinter Mal (C64 Style)")

    c64_background_blue = "#352879"
    c64_text_blue = "#6c5eb5"
    c64_active_background = "#4a3b8f"
    c64_active_foreground = "#8c7dc7"

    root.configure(bg=c64_background_blue)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = int(screen_width / 3)
    window_height = int(screen_height / 3)

    pos_x = int((screen_width / 2) - (window_width / 2))
    pos_y = int((screen_height / 2) - (window_height / 2))

    geometry_string = f"{window_width}x{window_height}+{pos_x}+{pos_y}"
    root.geometry(geometry_string)
    print(f"Setter vindusgeometri til: {geometry_string}")

    try:
        c64_font = tkFont.Font(family="Courier New", size=12, weight="bold")
    except tk.TclError:
        c64_font = tkFont.Font(family="Consolas", size=12, weight="bold")

    welcome_label = tk.Label(
        root,
        text="VELKOMMEN TIL TKINTER!",
        fg=c64_text_blue,
        bg=c64_background_blue,
        font=c64_font
    )
    welcome_label.pack(pady=40)

    def close_window():
        print("Avslutter applikasjonen...")
        root.destroy()

    exit_button = tk.Button(
        root,
        text="AVSLUTT",
        command=close_window,
        fg=c64_text_blue,
        bg=c64_background_blue,
        font=c64_font,
        relief=tk.RAISED, # Endret fra FLAT til RAISED
        activebackground=c64_active_background,
        activeforeground=c64_active_foreground,
        # highlightthickness og highlightbackground er mindre kritiske nå,
        # men kan beholdes hvis du vil.
        highlightthickness=1,
        highlightbackground=c64_text_blue
    )
    exit_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
