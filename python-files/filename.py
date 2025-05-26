import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# Klientklass som upprättar en permanent anslutning till servern
class ClusterClient:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        # Skapa en TCP-klient
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
        except Exception as e:
            print("Kunde inte ansluta till servern:", e)
            exit(1)
        self.lock = threading.Lock()

    def send(self, data):
        with self.lock:
            self.sock.sendall(data.encode('utf-8'))
    
    def receive(self, bufsize=4096):
        with self.lock:
            return self.sock.recv(bufsize).decode('utf-8')
    
    def close(self):
        self.sock.close()

# Tkinter GUI för klienten
class ClientGUI(tk.Tk):
    def __init__(self, client):
        super().__init__()
        self.title("Kluster Client GUI")
        self.geometry("600x400")
        self.client = client
        
        self.create_widgets()
        # Starta en tråd som kontinuerligt lyssnar på serverns svar
        self.read_thread = threading.Thread(target=self.read_from_server, daemon=True)
        self.read_thread.start()

    def create_widgets(self):
        # Textområde med scrollbar där svar från servern visas.
        self.output_area = ScrolledText(self, width=80, height=20)
        self.output_area.pack(padx=10, pady=10)

        # Entry widget för att skriva in ett kommando
        self.input_entry = tk.Entry(self, width=80)
        self.input_entry.pack(padx=10, pady=(0, 10))
        
        # Knapp för att skicka kommandot
        self.send_button = tk.Button(self, text="Skicka kommando", command=self.send_command)
        self.send_button.pack(pady=(0, 10))

    def send_command(self):
        command = self.input_entry.get().strip()
        if command:
            try:
                # Skicka kommandot följt av en radbrytning
                self.client.send(command + "\n")
            except Exception as e:
                self.append_text("Fel vid sändning: " + str(e))
            self.input_entry.delete(0, tk.END)

    def read_from_server(self):
        while True:
            try:
                data = self.client.receive(4096)
                if data:
                    self.append_text(data)
                else:
                    # Om inga data kommer tillbaka stängs anslutningen
                    self.append_text("Servern stängde anslutningen.")
                    break
            except Exception as e:
                self.append_text("Fel vid mottagning: " + str(e))
                break

    def append_text(self, text):
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)

if __name__ == '__main__':
    # Skapa en klient som ansluter till tcp-servern på port 9000
    client = ClusterClient("127.0.0.1", 9000)
    app = ClientGUI(client)
    app.mainloop()
