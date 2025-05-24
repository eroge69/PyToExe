import pandas as pd
import win32print
import win32ui
from tkinter import Tk, Label, Entry, Button, StringVar, filedialog
import os

class BarcodeApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Barcode Scanner to Printer")
        self.root.geometry("500x300")
        
        self.excel_path = StringVar()
        self.scanned_barcode = StringVar()
        self.status_message = StringVar(value="Ready to scan")
        self.barcode_map = None
        self.printer_name = None
        self.use_zpl = True  # Change this to False to use EPL
        
        Label(root, text="Excel File:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        Label(root, textvariable=self.excel_path, width=30).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        Button(root, text="Browse...", command=self.load_excel).grid(row=0, column=2, padx=10, pady=10)
        
        Label(root, text="Scan Barcode A:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        entry = Entry(root, textvariable=self.scanned_barcode, width=30)
        entry.grid(row=1, column=1, padx=10, pady=10)
        entry.bind('<Return>', self.process_barcode)
        
        Button(root, text="Select Printer", command=self.select_printer).grid(row=2, column=0, padx=10, pady=10)
        Button(root, text="Toggle ZPL/EPL", command=self.toggle_language).grid(row=2, column=1, padx=10, pady=10)
        
        Label(root, text="Status:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        Label(root, textvariable=self.status_message).grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="w")
    
    def toggle_language(self):
        self.use_zpl = not self.use_zpl
        mode = "ZPL" if self.use_zpl else "EPL"
        self.status_message.set(f"Switched to {mode} mode")

    def load_excel(self):
        file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=(("Excel files", "*.xlsx *.xls"),))
        if file_path:
            try:
                self.barcode_map = pd.read_excel(file_path)
                if 'A' not in self.barcode_map.columns or 'B' not in self.barcode_map.columns:
                    self.status_message.set("Excel must have 'A' and 'B' columns")
                    self.barcode_map = None
                    return
                self.excel_path.set(os.path.basename(file_path))
                self.status_message.set(f"Loaded {len(self.barcode_map)} barcode pairs")
            except Exception as e:
                self.status_message.set(f"Error: {str(e)}")

    def select_printer(self):
        printers = [printer[2] for printer in win32print.EnumPrinters(2)]
        printer_window = Tk()
        printer_window.title("Select Printer")
        for printer in printers:
            btn = Button(printer_window, text=printer, command=lambda p=printer: self.set_printer(p, printer_window))
            btn.pack(padx=10, pady=5, fill="x")
        printer_window.mainloop()

    def set_printer(self, printer_name, dialog):
        self.printer_name = printer_name
        self.status_message.set(f"Selected: {printer_name}")
        dialog.destroy()

    def process_barcode(self, event=None):
        if self.barcode_map is None:
            self.status_message.set("Load Excel first")
            return
        if not self.printer_name:
            self.status_message.set("Select printer first")
            return

        barcode_a = self.scanned_barcode.get().strip()
        if not barcode_a:
            return

        matches = self.barcode_map[self.barcode_map['A'] == barcode_a]
        if len(matches) == 0:
            self.status_message.set(f"No match for {barcode_a}")
            self.print_barcode("12345678")  # fallback test
        else:
            barcode_b = matches.iloc[0]['B']
            self.print_barcode(str(barcode_b))
            self.status_message.set(f"Printed: {barcode_b}")
        
        self.scanned_barcode.set("")

    def print_barcode(self, data):
        try:
            hPrinter = win32print.OpenPrinter(self.printer_name)
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Barcode Job", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)

            if self.use_zpl:
                command = f"^XA\n^FO50,50^BY2\n^BCN,100,Y,N,N\n^FD{data}^FS\n^XZ"
            else:
                command = f"N\nB50,50,0,1,2,4,100,N,\"{data}\"\nP1\n"

            print("Sending to printer:\n", command)
            win32print.WritePrinter(hPrinter, command.encode())
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            win32print.ClosePrinter(hPrinter)
        except Exception as e:
            self.status_message.set(f"Print error: {str(e)}")

if _name_ == "_main_":
    root = Tk()
    app = BarcodeApp(root)
    root.mainloop()