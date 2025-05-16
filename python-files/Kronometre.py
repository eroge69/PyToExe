import tkinter as tk
import time
import threading

class KronometreApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Kronometre")
        self.running = False
        self.start_time = None
        self.elapsed_time = 0

        self.label = tk.Label(master, text="00:00:00.000", font=("Helvetica", 40))
        self.label.pack(pady=20)

        self.start_button = tk.Button(master, text="Başlat", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(master, text="Durdur", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        self.reset_button = tk.Button(master, text="Sıfırla", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=10)

    def update(self):
        while self.running:
            current_time = time.time()
            total_time = self.elapsed_time + (current_time - self.start_time)
            hours, rem = divmod(int(total_time), 3600)
            minutes, seconds = divmod(rem, 60)
            milliseconds = int((total_time - int(total_time)) * 1000)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
            self.label.config(text=time_str)
            time.sleep(0.05)

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True
            threading.Thread(target=self.update, daemon=True).start()

    def stop(self):
        if self.running:
            self.elapsed_time += time.time() - self.start_time
            self.running = False

    def reset(self):
        self.running = False
        self.start_time = None
        self.elapsed_time = 0
        self.label.config(text="00:00:00.000")

if __name__ == "__main__":
    root = tk.Tk()
    app = KronometreApp(root)
    root.mainloop()