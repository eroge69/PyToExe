
import serial
import tkinter as tk
from tkinter import scrolledtext

def connect_serial():
    try:
        global ser
        ser = serial.Serial(port_entry.get(), 115200, timeout=1)
        output.insert(tk.END, "Terhubung ke " + port_entry.get() + "\n")
        read_serial()
    except:
        output.insert(tk.END, "Gagal konek ke port.\n")

def read_serial():
    if ser.in_waiting:
        line = ser.readline().decode("utf-8").strip()
        output.insert(tk.END, line + "\n")
        output.see(tk.END)
    root.after(100, read_serial)

root = tk.Tk()
root.title("MacLogic AutoDiag v1.0")

port_entry = tk.Entry(root)
port_entry.insert(0, "COM3")
port_entry.pack()

connect_btn = tk.Button(root, text="Connect", command=connect_serial)
connect_btn.pack()

output = scrolledtext.ScrolledText(root, width=80, height=20)
output.pack()

root.mainloop()
