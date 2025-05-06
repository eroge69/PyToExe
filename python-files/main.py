# pip install pybluez pandas
import bluetooth
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform

paired_device_address = None

def open_bluetooth_settings():
    os_name = platform.system()
    try:
        if os_name == "Windows":
            subprocess.run(["start", "ms-settings:bluetooth"], shell=True)
        elif os_name == "Linux":
            subprocess.run(["blueman-manager"])
        else:
            messagebox.showinfo("Manual Pairing Required", "Please pair the device manually via system settings.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def scan_devices():
    devices = bluetooth.discover_devices(duration=8, lookup_names=True)
    device_listbox.delete(0, tk.END)
    for addr, name in devices:
        device_listbox.insert(tk.END, f"{name} - {addr}")

def pair_device():
    selected = device_listbox.curselection()
    if not selected:
        messagebox.showwarning("Select Device", "Please select a device to pair.")
        return

    device_info = device_listbox.get(selected[0])
    addr = device_info.split(" - ")[-1]
    global paired_device_address
    paired_device_address = addr

    open_bluetooth_settings()
    messagebox.showinfo("Pair Device", f"Please pair the device manually with address: {addr}.")


def receive_csv_via_bluetooth():
    if not paired_device_address:
        messagebox.showwarning("Not Paired", "Please pair with a device first.")
        return

    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    bluetooth.advertise_service(server_sock, "CSVReceiver",
                                service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE])

    print(f"Waiting for connection on RFCOMM channel {port}")
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")

    with open("received.csv", "wb") as f:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            f.write(data)

    client_sock.close()
    server_sock.close()
    print("File received. Loading into GUI...")

    load_csv("received.csv")

def load_csv(file_path):
    for i in tree.get_children():
        tree.delete(i)

    try:
        df = pd.read_csv(file_path)
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        for col in df.columns:
            tree.heading(col, text=col)
        for row in df.itertuples(index=False):
            tree.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI Setup
root = tk.Tk()
root.title("Bluetooth CSV Viewer")

frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

tk.Label(frame, text="Available Devices:").pack(anchor="w")

device_listbox = tk.Listbox(frame, height=6)
device_listbox.pack(fill="x", padx=5)

btn_scan = tk.Button(frame, text="Scan Devices", command=scan_devices)
btn_scan.pack(pady=2)

btn_pair = tk.Button(frame, text="Pair Device", command=pair_device)
btn_pair.pack(pady=2)

btn_receive = tk.Button(frame, text="Receive CSV", command=receive_csv_via_bluetooth)
btn_receive.pack(pady=5)

tree = ttk.Treeview(root)
tree.pack(fill="both", expand=True)

root.mainloop()
