import tkinter as tk
from pynput import mouse
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

click_times = []

# Mouse click listener
def on_click(x, y, button, pressed):
    if pressed and button.name == 'left':
        click_times.append(datetime.now())

# Start mouse listener in background
listener = mouse.Listener(on_click=on_click)
listener.start()

# Set up GUI window
root = tk.Tk()
root.title("Mouse Click Tracker")

# Set up matplotlib figure
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Update plot
def update_plot(frame):
    ax.clear()
    if click_times:
        times = [(t - click_times[0]).total_seconds() for t in click_times]
        ax.plot(times, [1]*len(times), 'ro')
        ax.set_title("Mouse Clicks Over Time")
        ax.set_xlabel("Time (s)")
        ax.set_yticks([])
        ax.set_ylim(0, 2)

ani = animation.FuncAnimation(fig, update_plot, interval=1000)

# Run the app
root.mainloop()
