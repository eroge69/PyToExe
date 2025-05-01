import tkinter as tk
from threading import Thread, Event
import time
import keyboard  # Requires `pip install keyboard`

class IntervalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interval App")
        self.running = False
        self.stop_event = Event()
        self.listen_thread = None

        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.pack(pady=20)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop)
        self.stop_button.pack(pady=20)
        self.stop_button.pack_forget()  # Hide initially

    def start(self):
        self.running = True
        self.stop_event.clear()
        self.start_button.pack_forget()
        self.stop_button.pack(pady=20)

        self.listen_thread = Thread(target=self.listen_for_esc)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def stop(self):
        self.running = False
        self.stop_event.set()
        self.stop_button.pack_forget()
        self.start_button.pack(pady=20)

    def listen_for_esc(self):
        print("Listening for 'Esc' key press...")
        while self.running and not self.stop_event.is_set():
            if keyboard.is_pressed("esc"):
                print("ESC detected. Starting 3-second interval task.")
                self.run_interval_task()
                time.sleep(0.5)  # Debounce to avoid multiple triggers
            time.sleep(0.1)

    def run_interval_task(self):
        count = 0
        while self.running and not self.stop_event.is_set():
            print(f"Action #{count + 1}")
            time.sleep(3)
            count += 1
            if count == 20:
                print("20 actions completed. Pausing for 10 seconds...")
                time.sleep(10)
                count = 0  # Reset for next cycle

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = IntervalApp(root)
    root.mainloop()