import tkinter as tk
from tkinter import filedialog, messagebox
import difflib
import os

class FileCompareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text File Compare")

        self.file1 = None
        self.file2 = None

        tk.Button(root, text="Browse File 1", command=self.load_file1).pack(pady=5)
        tk.Button(root, text="Browse File 2", command=self.load_file2).pack(pady=5)
        tk.Button(root, text="Compare Files", command=self.compare_files).pack(pady=10)

        self.output = tk.Text(root, height=20, width=100)
        self.output.pack()

    def load_file1(self):
        self.file1 = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.file1:
            os.chmod(self.file1, 0o444)  # Set read-only (basic protection)
            messagebox.showinfo("File 1 Loaded", f"{self.file1} is now read-only")

    def load_file2(self):
        self.file2 = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.file2:
            os.chmod(self.file2, 0o444)  # Set read-only (basic protection)
            messagebox.showinfo("File 2 Loaded", f"{self.file2} is now read-only")

    def compare_files(self):
        if not self.file1 or not self.file2:
            messagebox.showerror("Missing Files", "Please select both files.")
            return

        with open(self.file1) as f1, open(self.file2) as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()

        diff = difflib.unified_diff(lines1, lines2, fromfile="File1", tofile="File2", lineterm="")
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", ''.join(diff) or "No differences found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCompareApp(root)
    root.mainloop()
