import tkinter as tk
from tkinter import messagebox
import math

class QuadDividerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuadDivider - জমি বিভাজন সফটওয়্যার")
        self.root.geometry("500x400")

        tk.Label(root, text="QuadDivider (Windows Edition)", font=("Arial", 16, "bold"), fg="green").pack(pady=10)

        self.length_var = tk.DoubleVar()
        self.width_var = tk.DoubleVar()

        tk.Label(root, text="জমির দৈর্ঘ্য (মিটার):").pack()
        tk.Entry(root, textvariable=self.length_var).pack(pady=5)

        tk.Label(root, text="জমির প্রস্থ (মিটার):").pack()
        tk.Entry(root, textvariable=self.width_var).pack(pady=5)

        tk.Label(root, text="কতটি ভাগ করতে চান?").pack()
        self.parts_var = tk.IntVar()
        tk.Entry(root, textvariable=self.parts_var).pack(pady=5)

        tk.Button(root, text="হিসাব করুন", command=self.calculate).pack(pady=10)

        self.result_label = tk.Label(root, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)

    def calculate(self):
        try:
            length = self.length_var.get()
            width = self.width_var.get()
            parts = self.parts_var.get()

            if length <= 0 or width <= 0 or parts <= 0:
                raise ValueError

            total_area = length * width
            divided_area = total_area / parts
            self.result_label.config(text=f"মোট এলাকা: {total_area:.2f} স্কয়ার মিটার\nপ্রতিটি ভাগ: {divided_area:.2f} স্কয়ার মিটার")
        except:
            messagebox.showerror("ত্রুটি", "অনুগ্রহ করে সঠিক মান প্রবেশ করুন।")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuadDividerApp(root)
    root.mainloop()