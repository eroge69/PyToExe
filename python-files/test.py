import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import pandas as pd
import re

class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Processor")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f2f5")  # Light gray background
        self.root.resizable(False, False)  # Disable resizing

        # Set window icon (replace 'icon.ico' with your icon file if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Hardcoded default output directory
        self.download_dir = Path(r"C:\Users\PRERAK SHAH\OneDrive - Access Computech Pvt. Ltd\Desktop\Abb\updated")

        # Styling
        self.root.style = ttk.Style()
        self.root.style.configure("TButton", font=("Segoe UI", 12), padding=10)
        self.root.style.configure("TLabel", font=("Segoe UI", 12), background="#f0f2f5")

        # Main Frame
        self.main_frame = tk.Frame(self.root, bg="#f0f2f5")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Title Label
        self.label = tk.Label(
            self.main_frame,
            text="File Processor",
            font=("Segoe UI", 18, "bold"),
            bg="#f0f2f5",
            fg="#2c3e50"
        )
        self.label.pack(pady=(0, 20))

        # Select File Button with Hover Effect
        self.select_file_btn = ttk.Button(
            self.main_frame,
            text="Select Input File",
            command=self.select_file,
            style="Custom.TButton"
        )
        self.select_file_btn.pack(pady=10, fill="x", padx=50)
        self.root.style.configure("Custom.TButton", background="#3498db", foreground="white")
        self.select_file_btn.bind("<Enter>", lambda e: self.select_file_btn.configure(style="Hover.TButton"))
        self.select_file_btn.bind("<Leave>", lambda e: self.select_file_btn.configure(style="Custom.TButton"))
        self.root.style.configure("Hover.TButton", background="#2980b9")

        # Process Button
        self.process_btn = ttk.Button(
            self.main_frame,
            text="Process File",
            command=self.process_file,
            state="disabled",
            style="Custom.TButton"
        )
        self.process_btn.pack(pady=10, fill="x", padx=50)

        # Status Label
        self.status_label = tk.Label(
            self.main_frame,
            text=f"No file selected\nOutput directory: {self.download_dir}",
            font=("Segoe UI", 10),
            bg="#f0f2f5",
            fg="#34495e",
            justify="center"
        )
        self.status_label.pack(pady=20)

        # Processing Label (hidden initially)
        self.processing_label = tk.Label(
            self.main_frame,
            text="Processing...",
            font=("Segoe UI", 10, "italic"),
            bg="#f0f2f5",
            fg="#e74c3c",
            justify="center"
        )
        self.processing_label.pack(pady=5)
        self.processing_label.pack_forget()  # Hide initially

        # Footer Label
        self.footer_label = tk.Label(
            self.main_frame,
            text="Made by Swet",
            font=("Segoe UI", 8, "italic"),
            bg="#f0f2f5",
            fg="#7f8c8d"
        )
        self.footer_label.pack(side="bottom", pady=10)

        self.selected_file = None

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.selected_file = Path(file_path)
            self.status_label.config(text=f"Selected: {self.selected_file.name}\nOutput directory: {self.download_dir}")
            self.check_process_button()

    def check_process_button(self):
        if self.selected_file:
            self.process_btn.config(state="normal")
        else:
            self.process_btn.config(state="disabled")

    def process_file(self):
        try:
            # Show processing label
            self.processing_label.pack()
            self.root.update()

            # Read the file
            with open(self.selected_file, "r", encoding="utf-8", errors="ignore") as file:
                lines = file.readlines()

            # Extract relevant lines with data entries using regex pattern matching
            data_lines = []
            pattern = re.compile(r'^\d{5},\d+ *,O,\d+')
            for line in lines:
                line = line.strip()
                if pattern.match(line):
                    data_lines.append(line)

            # Convert data into a DataFrame
            data = [line.split(',') for line in data_lines]
            df = pd.DataFrame(data, columns=["ID", "Code", "Type", "Timestamp"])

            # Remove duplicates based on all columns
            df_unique = df.drop_duplicates()

            # Reconstruct the lines
            cleaned_lines = [",".join(row) for row in df_unique.to_records(index=False)]

            # Create output filename with _updated
            output_filename = f"{self.selected_file.stem}_updated{self.selected_file.suffix}"
            output_path = self.download_dir / output_filename

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save the cleaned data to a new file
            with open(output_path, "w", encoding="utf-8") as file:
                file.write("\n".join(cleaned_lines))

            # Hide processing label
            self.processing_label.pack_forget()
            messagebox.showinfo("Success", f"File processed and saved as {output_filename}")
            self.status_label.config(text="File processed successfully\nOutput directory: {self.download_dir}")
            # Reset file selection
            self.selected_file = None
            self.process_btn.config(state="disabled")
            self.status_label.config(text=f"Select another file to process\nOutput directory: {self.download_dir}")

        except Exception as e:
            self.processing_label.pack_forget()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessorApp(root)
    root.mainloop()