import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser


class FashionAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Персональный стилист - подбор одежды")
        self.root.geometry("1920x1080")
        self.root.resizable(False, False)

        self.measurements = {
            "height": tk.IntVar(value=170),
            "chest": tk.IntVar(value=90),
            "hips": tk.IntVar(value=95),
            "waist": tk.IntVar(value=70),
            "head": tk.IntVar(value=56),
            "leg": tk.IntVar(value=80),
            "foot": tk.IntVar(value=38)
        }

        self.gender = tk.StringVar(value="female")
        self.style_preference = tk.StringVar(value="------")

        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10), padding=5)
        self.style.configure("Header.TLabel", font=("Arial", 14, "bold"))

        self.create_ui()

    def create_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Введите параметры и выберите стиль", style="Header.TLabel") \
            .pack(pady=(0, 10))

        self.create_inputs(frame)

        ttk.Button(frame, text="Подобрать и открыть Wildberries", command=self.get_recommendations).pack(pady=10)

    def create_inputs(self, parent):
        input_frame = ttk.Frame(parent)
        input_frame.pack()

        for i, (label, key) in enumerate([
            ("Рост", "height"),
            ("Грудь", "chest"),
            ("Бёдра", "hips"),
            ("Талия", "waist"),
            ("Голова", "head"),
            ("Нога (длина)", "leg"),
            ("Размер ноги", "foot")
        ]):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            ttk.Entry(input_frame, textvariable=self.measurements[key], width=10).grid(row=i, column=1, sticky="w", pady=2)

        ttk.Label(input_frame, text="Пол").grid(row=7, column=0, sticky="e", padx=5, pady=2)
        gender_frame = ttk.Frame(input_frame)
        gender_frame.grid(row=7, column=1, sticky="w")
        ttk.Radiobutton(gender_frame, text="Женский", variable=self.gender, value="female").pack(side="left")
        ttk.Radiobutton(gender_frame, text="Мужской", variable=self.gender, value="male").pack(side="left")

        ttk.Label(input_frame, text="Стиль").grid(row=8, column=0, sticky="e", padx=5, pady=2)
        styles = ["повседневная", "Классическое", "спортивное", "бизнес", "вечернее"]
        ttk.OptionMenu(input_frame, self.style_preference, self.style_preference.get(), *styles).grid(row=8, column=1, sticky="w")

    def get_recommendations(self):
        if not self.validate_inputs():
            return

        gender = "женская" if self.gender.get() == "female" else "мужская"
        style = self.style_preference.get()
        top_size = self.calculate_sizes()["top"]

        query = f"{gender}+одежда+{style}+{top_size}"
        search_url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={query}"
        webbrowser.open(search_url)

    def validate_inputs(self):
        for key, var in self.measurements.items():
            try:
                val = var.get()
                if val <= 0:
                    messagebox.showerror("Ошибка", f"Неверное значение для: {key}")
                    return False
            except tk.TclError:
                messagebox.showerror("Ошибка", f"Введите число для: {key}")
                return False
        return True

    def calculate_sizes(self):
        chest = self.measurements['chest'].get()
        hips = self.measurements['hips'].get()
        waist = self.measurements['waist'].get()
        foot = self.measurements['foot'].get()
        head = self.measurements['head'].get()
        is_female = self.gender.get() == "female"

        if is_female:
            top = self.select_size(chest, [84, 88, 92, 96], ["XS", "S", "M", "L", "XL"])
            bottom = self.select_size(hips, [94, 98, 102, 106], ["XS", "S", "M", "L", "XL"])
        else:
            top = self.select_size(chest, [92, 100, 108, 116], ["S", "M", "L", "XL", "XXL"])
            bottom = self.select_size(waist, [76, 84, 92, 100], ["S", "M", "L", "XL", "XXL"])

        hat = self.select_size(head, [54, 56, 58, 60], ["XS", "S", "M", "L", "XL"])
        return {"top": top, "bottom": bottom, "foot": f"EU {foot}", "hat": hat}

    def select_size(self, val, thresholds, sizes):
        for i, threshold in enumerate(thresholds):
            if val < threshold:
                return sizes[i]
        return sizes[-1]


def main():
    root = tk.Tk()
    app = FashionAssistantApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()