import tkinter as tk
from tkinter import ttk
import socket
import threading
import re

class CodeDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Number of Codes")
        self.running = False
        self.client_socket = None
        self.counter = 0  # ← Teller begint bij 0

        self.create_widgets()

    def create_widgets(self):
        # IP en poort invoer
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(side="top", fill="x")

        ttk.Label(input_frame, text="IP address:").pack(side="left")
        self.ip_entry = ttk.Entry(input_frame, width=15)
        self.ip_entry.pack(side="left")
        self.ip_entry.insert(0, "192.168.1.100")

        ttk.Label(input_frame, text="Poort:").pack(side="left", padx=(10, 0))
        self.port_entry = ttk.Entry(input_frame, width=6)
        self.port_entry.pack(side="left")
        self.port_entry.insert(0, "51237")

        self.connect_button = ttk.Button(input_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(side="left", padx=(10, 0))

        # Grote display
        self.code_label = tk.Label(self.root, text="No Data", font=("Helvetica", 200), fg="green")
        self.code_label.pack(expand=True, pady=50)

        # Counter label rechtsonder
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side="bottom", fill="x", anchor="se")
        self.counter_label = ttk.Label(bottom_frame, text="Valid messages: 0", anchor="e")
        self.counter_label.pack(side="right", padx=10, pady=5)

    def toggle_connection(self):
        if not self.running:
            ip = self.ip_entry.get()
            port = int(self.port_entry.get())
            self.connect_button.config(text="Disconnect")
            self.running = True
            threading.Thread(target=self.connect_socket, args=(ip, port), daemon=True).start()
        else:
            self.running = False
            self.connect_button.config(text="Connect")
            if self.client_socket:
                try:
                    self.client_socket.shutdown(socket.SHUT_RDWR)
                    self.client_socket.close()
                except:
                    pass

    def connect_socket(self, ip, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((ip, port))
            while self.running:
                try:
                    data = self.client_socket.recv(1024)
                    if not data:
                        break
                    message = data.decode(errors='ignore').strip()
                    self.process_message(message)
                except socket.error:
                    break
        except Exception as e:
            self.show_message(f"Error: {e}")
        finally:
            self.running = False
            self.client_socket.close()
            self.client_socket = None
            self.root.after(0, lambda: self.connect_button.config(text="Connect"))

    def process_message(self, message):
        match = re.search(r'Number of codes\s*=\s*(\d{1,4})', message)
        if match:
            code = match.group(1)
            self.counter += 1
            self.root.after(0, lambda: self.code_label.config(text=code))
            self.root.after(0, lambda: self.counter_label.config(text=f"Trigger counter: {self.counter}"))

    def show_message(self, text):
        self.root.after(0, lambda: self.code_label.config(text=text))

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeDisplayApp(root)
    root.mainloop()
