import threading
import tkinter as tk
from tkinter import messagebox
from collections import deque
import queue
import os

# Set matplotlib to use TkAgg safely
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    from scapy.all import sniff, IP
except ImportError:
    sniff = None


class TrafficMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Traffic Monitor")
        self.root.geometry("800x600")

        # Dark grey background for the whole GUI
        self.bg_color = "#2e2e2e"
        self.root.configure(bg=self.bg_color)

        self.running = False
        self.ip_to_monitor = ""
        self.packet_queue = queue.Queue()
        self.incoming_traffic = deque([0]*30, maxlen=30)
        self.outgoing_traffic = deque([0]*30, maxlen=30)

        self.create_widgets()

        # Exit cleanly
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def create_widgets(self):
        # Label style uses the bg_color, text in green for visibility
        label_style = {"bg": self.bg_color, "fg": "lime"}
        # Entry style: dark background, white text
        entry_style = {"bg": "#1e1e1e", "fg": "white", "insertbackground": "white"}

        self.ip_label = tk.Label(self.root, text="Enter IP to Monitor:", **label_style)
        self.ip_label.pack(pady=5)

        self.ip_entry = tk.Entry(self.root, width=30, **entry_style)
        self.ip_entry.pack()

        self.start_btn = tk.Button(
            self.root,
            text="Start Monitoring",
            command=self.start_monitoring,
            bg="#444444",
            fg="lime",
            activebackground="#555555",
            activeforeground="lime",
            relief=tk.FLAT,
            bd=0,
        )
        self.start_btn.pack(pady=5)

        # Create matplotlib figure and axis
        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.ax = self.figure.add_subplot(1, 1, 1)
        self.ax.set_facecolor("#1e1e1e")  # dark background for the plot area

        # Hide all spines (borders) to remove white outlines around plot
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        # Remove ticks but keep labels white for readability
        self.ax.tick_params(left=False, bottom=False, labelcolor="white")

        self.ax.set_title("Live Traffic Chart", color="white")
        self.ax.set_xlabel("Time", color="white")
        self.ax.set_ylabel("Packet Size", color="white")

        self.line_in, = self.ax.plot([], [], label="Incoming", color="lime")
        self.line_out, = self.ax.plot([], [], label="Outgoing", color="tomato")

        # Legend with dark background and no edge color
        self.ax.legend(
            loc="upper right",
            facecolor="#1e1e1e",
            edgecolor='none',
            labelcolor="white",
        )

        # Set figure background and edges to the same dark grey as GUI
        self.figure.patch.set_facecolor(self.bg_color)
        self.figure.patch.set_edgecolor(self.bg_color)
        self.figure.patch.set_linewidth(0)

        # Create canvas and remove any widget border or highlight
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.config(bg=self.bg_color, highlightthickness=0, bd=0)

        canvas_widget.pack(fill=tk.BOTH, expand=True)

    def start_monitoring(self):
        if not sniff:
            messagebox.showerror("Error", "Scapy is not installed.")
            return

        if not self.is_admin():
            messagebox.showerror("Permission Error", "Please run as administrator.")
            return

        ip = self.ip_entry.get().strip()
        if not ip:
            messagebox.showwarning("Warning", "Please enter a valid IP.")
            return

        self.ip_to_monitor = ip
        self.incoming_traffic.clear()
        self.outgoing_traffic.clear()
        self.incoming_traffic.extend([0]*30)
        self.outgoing_traffic.extend([0]*30)
        self.running = True

        try:
            sniff_thread = threading.Thread(target=self.sniff_packets, daemon=True)
            sniff_thread.start()
            self.root.after(1000, self.update_chart)
        except Exception as e:
            messagebox.showerror("Error starting monitor", str(e))

    def sniff_packets(self):
        try:
            def process_packet(pkt):
                if IP in pkt:
                    size = len(pkt)
                    if pkt[IP].src == self.ip_to_monitor:
                        self.packet_queue.put(("out", size))
                    elif pkt[IP].dst == self.ip_to_monitor:
                        self.packet_queue.put(("in", size))

            sniff(filter=f"ip host {self.ip_to_monitor}", prn=process_packet, store=0)
        except Exception as e:
            print("Sniff error:", e)
            self.running = False

    def update_chart(self):
        try:
            while not self.packet_queue.empty():
                direction, size = self.packet_queue.get()
                if direction == "in":
                    self.incoming_traffic.append(size)
                    self.outgoing_traffic.append(0)
                elif direction == "out":
                    self.outgoing_traffic.append(size)
                    self.incoming_traffic.append(0)

            self.line_in.set_data(range(len(self.incoming_traffic)), list(self.incoming_traffic))
            self.line_out.set_data(range(len(self.outgoing_traffic)), list(self.outgoing_traffic))

            self.ax.set_xlim(0, len(self.incoming_traffic))
            self.ax.set_ylim(0, max(max(self.incoming_traffic), max(self.outgoing_traffic), 100))

            self.canvas.draw()

            if self.running:
                self.root.after(1000, self.update_chart)
        except Exception as e:
            print("Chart update error:", e)

    def is_admin(self):
        if os.name == 'nt':
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
        return os.getuid() == 0

    def quit_app(self):
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficMonitorApp(root)
    root.mainloop()
