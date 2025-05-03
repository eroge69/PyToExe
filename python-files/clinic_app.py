import tkinter as tk
from tkinter import ttk, messagebox

class Medicine:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

class ClinicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clinic Medicine Management System")
        self.geometry("500x400")
        self.medicines = []

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for Page in (HomePage, AddMedicinePage, ViewMedicinePage):
            page_name = Page.__name__
            frame = Page(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Clinic Medicine Management", font=("Arial", 18)).pack(pady=20)

        ttk.Button(self, text="Add Medicine", width=30,
                   command=lambda: controller.show_frame("AddMedicinePage")).pack(pady=10)

        ttk.Button(self, text="View Medicines", width=30,
                   command=lambda: controller.show_frame("ViewMedicinePage")).pack(pady=10)

        ttk.Button(self, text="Exit", width=30, command=controller.quit).pack(pady=10)

class AddMedicinePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Add Medicine", font=("Arial", 16)).pack(pady=10)

        tk.Label(self, text="Medicine Name:").pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        tk.Label(self, text="Quantity:").pack()
        self.quantity_entry = tk.Entry(self)
        self.quantity_entry.pack()

        ttk.Button(self, text="Add", command=self.add_medicine).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("HomePage")).pack()

    def add_medicine(self):
        name = self.name_entry.get().strip()
        qty = self.quantity_entry.get().strip()

        if not name or not qty.isdigit():
            messagebox.showerror("Error", "Invalid input.")
            return

        self.controller.medicines.append(Medicine(name, int(qty)))
        messagebox.showinfo("Success", f"{name} added successfully!")
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

class ViewMedicinePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Medicine List", font=("Arial", 16)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Name", "Quantity"), show='headings')
        self.tree.heading("Name", text="Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        ttk.Button(self, text="Refresh", command=self.load_data).pack(pady=5)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("HomePage")).pack()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for med in self.controller.medicines:
            self.tree.insert("", "end", values=(med.name, med.quantity))

if __name__ == "__main__":
    app = ClinicApp()
    app.mainloop()
