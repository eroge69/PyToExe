
import tkinter as tk
from time import strftime, localtime
import datetime
import holidays

us_holidays = holidays.US()

def update_time():
    now = datetime.datetime.now()
    current_time = now.strftime('%I:%M:%S %p')
    label.config(text=current_time)

    # Check for US market holiday
    today = now.date()
    if today in us_holidays:
        status = f"Market Closed: {us_holidays[today]}"
    else:
        # NYSE market hours in EST (assume local time is EST)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        if market_open <= now <= market_close and now.weekday() < 5:
            status = "Market Open"
        else:
            status = "Market Closed"

    status_label.config(text=status)
    root.after(1000, update_time)

def show_context_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)

def close_app():
    root.destroy()

def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

if __name__ == '__main__':
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("320x130+100+100")
    root.configure(background='black')

    # Enable window drag
    root.bind("<Button-1>", start_move)
    root.bind("<ButtonRelease-1>", stop_move)
    root.bind("<B1-Motion>", do_move)

    label = tk.Label(root, font=("Helvetica", 36, "bold"), fg="cyan", bg="black")
    label.pack(pady=(10,0))

    status_label = tk.Label(root, font=("Helvetica", 14), fg="white", bg="black")
    status_label.pack()

    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Exit", command=close_app)
    root.bind("<Button-3>", show_context_menu)

    update_time()
    root.mainloop()
