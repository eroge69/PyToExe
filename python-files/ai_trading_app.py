import tkinter as tk
from datetime import datetime

class AITradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Trading App")
        self.root.geometry("800x600")
        self.root.configure(bg="white")

        self.header = tk.Label(root, text="AI Trading App Dashboard", font=("Helvetica", 20), bg="white")
        self.header.pack(pady=20)

        self.time_label = tk.Label(root, text="", font=("Helvetica", 16), bg="white", fg="black")
        self.time_label.pack()

        self.status_label = tk.Label(root, text="System Status: ⚡ Active", font=("Helvetica", 14), bg="white", fg="green")
        self.status_label.pack(pady=10)

        self.refresh_button = tk.Button(root, text="🔄 Refresh Data", command=self.refresh_data)
        self.refresh_button.pack(pady=5)

        self.output_box = tk.Text(root, height=20, width=90, font=("Courier", 10))
        self.output_box.pack(pady=10)

        self.update_time()
        self.insert_sample_data()

    def update_time(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"Current Time: {now}")
        self.root.after(1000, self.update_time)

    def refresh_data(self):
        self.output_box.delete("1.0", tk.END)
        self.insert_sample_data()

    def insert_sample_data(self):
        stocks = ["GNS", "HCDI", "MULN", "COSM", "SNTI", "VINE"]
        for stock in stocks:
            self.output_box.insert(tk.END, f"[{stock}] - AI Bot Analyzing... Risk: ⚠️ Moderate | ETA: 00:14\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = AITradingApp(root)
    root.mainloop()
