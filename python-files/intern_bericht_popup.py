
import tkinter as tk
import threading
import platform

def play_beep():
    try:
        if platform.system() == 'Windows':
            import winsound
            winsound.Beep(1000, 200)
            winsound.Beep(1500, 200)
    except Exception as e:
        print("Beep failed:", e)

def close_after_delay(window):
    window.after(15000, window.destroy)

root = tk.Tk()
root.title("Nieuw intern bericht")
root.attributes('-topmost', True)
root.geometry("400x100+700+400")
root.resizable(False, False)

label = tk.Label(root, text="📬 Je hebt een nieuw intern bericht ontvangen!", font=("Segoe UI", 12))
label.pack(expand=True, padx=20, pady=20)

# Start beep sound in another thread
threading.Thread(target=play_beep).start()

# Auto-close after 15 seconds
close_after_delay(root)

root.mainloop()
