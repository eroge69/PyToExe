import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class PartTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Part Tracker")
        self.root.geometry("500x300")
        self.inv_path = ""
        self.track_path = ""
        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.root, text="Part Tracker", font=('Arial', 16))
        title_label.pack(pady=10)

        # Inventory Button
        self.inventory_btn = ttk.Button(  # Fixed: Changed from tracker_btn to inventory_btn
            self.root,
            text="1. Upload Inventory File",
            command=self.select_inv,
            width=30
        )
        self.inventory_btn.pack(pady=5)
        self.inventory_label = tk.Label(self.root, text="No file selected", fg="gray")
        self.inventory_label.pack()

        # Tracker Button
        self.tracker_btn = ttk.Button(
            self.root,
            text="2. Upload Tracker File",
            command=self.select_track, 
            width=30
        )
        self.tracker_btn.pack(pady=5)
        self.tracker_label = tk.Label(self.root, text="No file selected", fg="gray")
        self.tracker_label.pack()

        # Process Button
        self.process_btn = ttk.Button(
            self.root,
            text="3. Process Files",
            command=self.process_files,
            width=30,
            state=tk.DISABLED
        )
        self.process_btn.pack(pady=20)

        # Status Label
        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack()

    def select_inv(self):
        self.inv_path = filedialog.askopenfilename(
            title="Select INVENTORY File",
            filetypes=[("Excel/CSV files", "*.xlsx *.csv")]
        )
        if self.inv_path:
            self.inventory_label.config(text=self.inv_path.split('/')[-1], fg="green")
            self.check_files_ready()

    def select_track(self):
        self.track_path = filedialog.askopenfilename(
            title="Select TRACKER File",
            filetypes=[("Excel/CSV files", "*.xlsx *.csv")]
        )
        if self.track_path:
            self.tracker_label.config(text=self.track_path.split('/')[-1], fg="green")
            self.check_files_ready()

    def check_files_ready(self):
        if self.inv_path and self.track_path:
            self.process_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Ready to process!", fg="green")
        else:
            self.process_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Please upload both files", fg="red")

    def process_files(self):
        try:
            # Read files
            if self.inv_path.endswith(".xlsx"):
                inv_df = pd.read_excel(self.inv_path)
            else:
                inv_df = pd.read_csv(self.inv_path)

            if self.track_path.endswith(".xlsx"):
                track_df = pd.read_excel(self.track_path)
            else:
                track_df = pd.read_csv(self.track_path)

            # Process data
            merged = pd.merge(inv_df, track_df, on='ID', how='inner')
            merged['Delta'] = merged['Qty Rem'] - merged['Req']
            flagged_df = merged[merged['Delta'] < 0].copy()

            # Save output
            output_path = filedialog.asksaveasfilename(
                title="Save Output As",
                defaultextension='.xlsx',
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")] 
            )
            if output_path:
                flagged_df.to_excel(output_path, index=False)
                messagebox.showinfo("Success", f"Output saved to:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PartTracker(root)
    root.mainloop()