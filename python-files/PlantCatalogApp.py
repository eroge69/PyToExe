import tkinter as tk
from tkinter import filedialog
import os

LOGO_PATH = "logo.png"

plant_data = [
    {
        "name": "plant1",
        "date_found": "01/01/2020",
        "location": "Blah Street",
        "notes": "",
        "image_path": "plant1.png"
    },
    {
        "name": "plant2",
        "date_found": "02/02/2021",
        "location": "Somewhere Else",
        "notes": "Grows fast",
        "image_path": "plant2.png"
    }
]

class PlantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plant Viewer")
        self.current_index = 0
        self.tk_image = None
        self.logo_image = None

        self.left_frame = tk.Frame(root, width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Logo
        if os.path.exists(LOGO_PATH):
            try:
                self.logo_image = tk.PhotoImage(file=LOGO_PATH)
                self.logo_label = tk.Label(self.left_frame, image=self.logo_image)
                self.logo_label.pack(pady=10)
            except Exception:
                tk.Label(self.left_frame, text="Invalid Logo").pack(pady=10)

        # Scrollable button list
        self.canvas = tk.Canvas(self.left_frame)
        self.scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.buttons_frame = tk.Frame(self.canvas)

        self.buttons_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.buttons_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="y", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.plant_buttons = []
        self.update_plant_buttons()

        # Add plant button
        self.add_button = tk.Button(self.left_frame, text="Add Plant", command=self.add_plant)
        self.add_button.pack(pady=10)

        # Navigation arrows
        self.nav_frame = tk.Frame(self.right_frame)
        self.nav_frame.pack(anchor="ne", padx=20, pady=10)

        self.prev_button = tk.Button(self.nav_frame, text="←", command=self.prev_plant)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(self.nav_frame, text="→", command=self.next_plant)
        self.next_button.pack(side=tk.LEFT)

        # Display area
        self.display_frame = tk.Frame(self.right_frame)
        self.display_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.image_label = tk.Label(self.display_frame)
        self.image_label.grid(row=0, column=0, rowspan=4)

        self.info_text = tk.Text(self.display_frame, height=10, width=40)
        self.info_text.grid(row=0, column=1, padx=10)

        self.display_plant(self.current_index)

    def update_plant_buttons(self):
        for btn in self.plant_buttons:
            btn.destroy()
        self.plant_buttons.clear()
        for i, plant in enumerate(plant_data):
            btn = tk.Button(self.buttons_frame, text=plant["name"], width=20, command=lambda idx=i: self.display_plant(idx))
            btn.pack(pady=2, padx=2, anchor="w")
            self.plant_buttons.append(btn)

    def display_plant(self, index):
        self.current_index = index
        plant = plant_data[index]
        self.info_text.delete("1.0", tk.END)
        info = (
            f"Name: {plant['name']}\n"
            f"Date Found: {plant['date_found']}\n"
            f"Location: {plant['location']}\n"
            f"Notes: {plant['notes']}"
        )
        self.info_text.insert(tk.END, info)

        if plant["image_path"] and os.path.exists(plant["image_path"]):
            try:
                self.tk_image = tk.PhotoImage(file=plant["image_path"])
                self.image_label.config(image=self.tk_image, text="")
            except Exception:
                self.image_label.config(image="", text="Unsupported image")
        else:
            self.image_label.config(image="", text="No image found")

    def prev_plant(self):
        self.current_index = (self.current_index - 1) % len(plant_data)
        self.display_plant(self.current_index)

    def next_plant(self):
        self.current_index = (self.current_index + 1) % len(plant_data)
        self.display_plant(self.current_index)

    def add_plant(self):
        def browse_image():
            file = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.gif")])
            if file:
                img_path.set(file)

        def clear_image():
            img_path.set("")

        def save_plant():
            name = name_entry.get().strip()
            date = date_entry.get().strip()
            location = location_entry.get().strip()
            notes = notes_entry.get("1.0", tk.END).strip()
            image = img_path.get().strip()

            plant_data.append({
                "name": name if name else "Unnamed",
                "date_found": date,
                "location": location,
                "notes": notes,
                "image_path": image
            })
            self.update_plant_buttons()
            self.display_plant(len(plant_data) - 1)
            add_window.destroy()

        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Plant")

        tk.Label(add_window, text="Name:").pack()
        name_entry = tk.Entry(add_window)
        name_entry.pack()

        tk.Label(add_window, text="Date Found:").pack()
        date_entry = tk.Entry(add_window)
        date_entry.pack()

        tk.Label(add_window, text="Location:").pack()
        location_entry = tk.Entry(add_window)
        location_entry.pack()

        tk.Label(add_window, text="Notes:").pack()
        notes_entry = tk.Text(add_window, height=5, width=30)
        notes_entry.pack()

        tk.Label(add_window, text="Image Path:").pack()
        img_path = tk.StringVar()
        img_display = tk.Entry(add_window, textvariable=img_path, width=40)
        img_display.pack()

        tk.Button(add_window, text="Browse Image", command=browse_image).pack(pady=2)
        tk.Button(add_window, text="No Image", command=clear_image).pack(pady=2)

        tk.Button(add_window, text="Save", command=save_plant).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = PlantApp(root)
    root.mainloop()
