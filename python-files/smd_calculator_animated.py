
import tkinter as tk
from tkinter import ttk

class SMD_Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("ISRO SMD Footprint Calculator")
        
        # Initialize history
        self.history = []

        # Create input fields
        self.create_input_fields()

        # Create calculate button
        self.create_calculate_button()

        # Create history display
        self.create_history_display()

    def create_input_fields(self):
        self.input_frame = tk.LabelFrame(self.root, text="Input Fields", padx=10, pady=10)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10)

        self.label_L = tk.Label(self.input_frame, text="Total Body Length (L) in mm:")
        self.label_L.grid(row=0, column=0, padx=10, pady=5)
        self.entry_L = tk.Entry(self.input_frame)
        self.entry_L.grid(row=0, column=1, padx=10, pady=5)

        self.label_W = tk.Label(self.input_frame, text="Maximum Width (W) in mm:")
        self.label_W.grid(row=1, column=0, padx=10, pady=5)
        self.entry_W = tk.Entry(self.input_frame)
        self.entry_W.grid(row=1, column=1, padx=10, pady=5)

        self.label_e = tk.Label(self.input_frame, text="Pad Width (e) in mm:")
        self.label_e.grid(row=2, column=0, padx=10, pady=5)
        self.entry_e = tk.Entry(self.input_frame)
        self.entry_e.grid(row=2, column=1, padx=10, pady=5)

        self.label_copper = tk.Label(self.input_frame, text="Copper Thickness:")
        self.label_copper.grid(row=3, column=0, padx=10, pady=5)
        self.copper_var = tk.StringVar()
        self.copper_combobox = ttk.Combobox(self.input_frame, textvariable=self.copper_var)
        self.copper_combobox['values'] = ('1 Oz', '2 Oz')
        self.copper_combobox.grid(row=3, column=1, padx=10, pady=5)

    def create_calculate_button(self):
        self.calculate_button = tk.Button(self.root, text="Calculate", command=self.calculate)
        self.calculate_button.grid(row=1, column=0, pady=10)

    def create_history_display(self):
        self.history_frame = tk.LabelFrame(self.root, text="Calculation History (Last 5)", padx=10, pady=10)
        self.history_frame.grid(row=2, column=0, padx=10, pady=10)
        
        self.history_text = tk.Text(self.history_frame, height=10, width=50)
        self.history_text.grid(row=0, column=0, padx=10, pady=5)
        self.history_text.config(state=tk.DISABLED)

    def calculate(self):
        try:
            L = float(self.entry_L.get())
            W = float(self.entry_W.get())
            e = float(self.entry_e.get())
            copper_thickness = self.copper_var.get()

            if copper_thickness == '1 Oz':
                prt = 0.13
                plt = 0.1
            elif copper_thickness == '2 Oz':
                prt = 0.2
                plt = 0.1
            else:
                raise ValueError("Invalid copper thickness")

            G = L - (2 * e + prt + plt)
            Z = L + prt + plt + 2 * 0.75
            Y = Z - (G / 2)
            X = W + prt + plt + 2 * 0.15
            A = G + Y

            result = f"L: {L}, W: {W}, e: {e}, Copper: {copper_thickness}\nG: {G:.2f}, Z: {Z:.2f}, Y: {Y:.2f}, X: {X:.2f}, A: {A:.2f}\n"
            self.update_history(result)

            # Animation: Change button color briefly
            self.calculate_button.config(bg="lightgreen")
            self.root.after(200, lambda: self.calculate_button.config(bg="SystemButtonFace"))

        except ValueError as ve:
            self.update_history(f"Error: {ve}")

    def update_history(self, result):
        if len(self.history) >= 5:
            self.history.pop(0)
        self.history.append(result)
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        for entry in self.history:
            self.history_text.insert(tk.END, entry + "\n")
        self.history_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SMD_Calculator(root)
    root.mainloop()
