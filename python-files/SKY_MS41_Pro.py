
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import binascii
import difflib
import struct
import os

class SKYMS41Editor:
    def __init__(self, master):
        self.master = master
        self.master.title("SKY MS41")
        self.original_bin = None
        self.modified_bin = None
        self.filename = None
        self.monitor_addresses = {
            "Catalyst Monitor": 0x159CC,
            "EVAP System Monitor": 0x159CD,
            "Oxygen Sensor Monitor": 0x159CE,
            "Oxygen Sensor Heater": 0x159CF,
            "EGR Monitor": 0x159D0,
            "Secondary Air Monitor": 0x159D1
        }
        self.monitor_vars = {}
        self.create_widgets()

    def create_widgets(self):
        tab_control = ttk.Notebook(self.master)
        self.editor_tab = ttk.Frame(tab_control)
        self.diff_tab = ttk.Frame(tab_control)
        tab_control.add(self.editor_tab, text='Monitor Editor')
        tab_control.add(self.diff_tab, text='Hex Diff Viewer')
        tab_control.pack(expand=1, fill="both")

        # Editor Tab
        ttk.Button(self.editor_tab, text="Open BIN", command=self.load_bin).pack(pady=5)
        frame_flags = ttk.LabelFrame(self.editor_tab, text="Readiness Monitors")
        frame_flags.pack(padx=10, pady=10)
        for monitor in self.monitor_addresses:
            var = tk.IntVar()
            self.monitor_vars[monitor] = var
            ttk.Checkbutton(frame_flags, text=monitor, variable=var).pack(anchor="w")
        ttk.Button(self.editor_tab, text="Apply Changes", command=self.apply_changes).pack(pady=5)
        ttk.Button(self.editor_tab, text="Auto Pass All Monitors", command=self.auto_pass_all).pack(pady=5)
        ttk.Button(self.editor_tab, text="Permanent Patch (Always Ready)", command=self.permanent_patch).pack(pady=5)
        ttk.Button(self.editor_tab, text="Save Modified BIN", command=self.save_bin).pack(pady=10)

        # Diff Tab
        self.diff_text = tk.Text(self.diff_tab, wrap="none")
        self.diff_text.pack(expand=True, fill="both")
        ttk.Button(self.diff_tab, text="Generate Diff", command=self.show_diff).pack(pady=5)

    def load_bin(self):
        file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
        if not file_path:
            return
        with open(file_path, 'rb') as f:
            self.original_bin = f.read()
            self.modified_bin = bytearray(self.original_bin)
        self.filename = os.path.basename(file_path)
        messagebox.showinfo("Loaded", f"Loaded {self.filename} successfully!")

    def apply_changes(self):
        if not self.modified_bin:
            messagebox.showerror("Error", "Load a BIN file first!")
            return
        for monitor, var in self.monitor_vars.items():
            addr = self.monitor_addresses[monitor]
            self.modified_bin[addr] = 0x01 if var.get() else 0x00
        self.fix_checksum()
        messagebox.showinfo("Success", "Readiness flags updated!")

    def auto_pass_all(self):
        if not self.modified_bin:
            messagebox.showerror("Error", "Load a BIN file first!")
            return
        for var in self.monitor_vars.values():
            var.set(1)
        self.apply_changes()

    def permanent_patch(self):
        if not self.modified_bin:
            messagebox.showerror("Error", "Load a BIN file first!")
            return
        patch_start = 0x159C0  # 12 bytes before flags
        patch_sequence = [
            0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
            0x01, 0x01, 0x01, 0x01, 0x01, 0x01
        ]
        for i, byte in enumerate(patch_sequence):
            self.modified_bin[patch_start + i] = byte
        for addr in self.monitor_addresses.values():
            self.modified_bin[addr] = 0x01
        self.fix_checksum()
        messagebox.showinfo("Patched!", "Permanent readiness patch applied!")

    def fix_checksum(self):
        if not self.modified_bin:
            return
        checksum_region = self.modified_bin[0:0x8000]
        checksum = sum(checksum_region) & 0xFFFF
        checksum_bytes = struct.pack('>H', checksum) # Big endian
        self.modified_bin[0x7FFE:0x8000] = checksum_bytes

    def show_diff(self):
        if not self.modified_bin:
            messagebox.showerror("Error", "Load a BIN file first!")
            return
        original_hex = binascii.hexlify(self.original_bin).decode('utf-8')
        modified_hex = binascii.hexlify(self.modified_bin).decode('utf-8')
        diff = difflib.unified_diff(original_hex.splitlines(), modified_hex.splitlines(), fromfile='Original', tofile='Modified')
        self.diff_text.delete('1.0', tk.END)
        self.diff_text.insert('1.0', '
'.join(diff))

    def save_bin(self):
        if not self.modified_bin:
            messagebox.showerror("Error", "Load a BIN file first!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".bin", initialfile="modified_" + (self.filename or "output.bin"))
        if not file_path:
            return
        with open(file_path, 'wb') as f:
            f.write(self.modified_bin)
        messagebox.showinfo("Saved", f"Modified BIN saved as {file_path}!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SKYMS41Editor(root)
    root.mainloop()
