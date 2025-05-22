import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import re

plt.style.use('dark_background')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(BASE_DIR, "speed_profiles.json")

class ProfileEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tracking Profile Editor")
        self.geometry("1000x640")
        self.configure(bg="#1e1e1e")

        self.profiles = {}
        self.current_name = ""
        self.dragging_index = None
        self.default_profile = [1.0] * 10

        self.load_profiles_from_file()
        self.create_widgets()
        self.update_dropdown()

        if self.profiles:
            self.set_profile(list(self.profiles.keys())[0])
        else:
            self.new_curve()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("TButton", background="#333", foreground="white")
        style.configure("TEntry", fieldbackground="#333", foreground="white")

        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=12)

        ttk.Label(left, text="Profile Name:").pack(anchor='w')
        self.name_entry = ttk.Entry(left)
        self.name_entry.pack(fill='x', pady=(0, 10))

        ttk.Button(left, text="New Curve", command=self.new_curve).pack(fill='x')
        ttk.Button(left, text="Save Curve", command=self.save_curve).pack(fill='x', pady=(5, 10))

        self.profile_combo = ttk.Combobox(left, state='readonly')
        self.profile_combo.pack(fill='x')
        self.profile_combo.bind("<<ComboboxSelected>>", self.profile_selected)

        ttk.Button(left, text="Export to C# File", command=self.export_profiles).pack(fill='x', pady=(10, 0))
        ttk.Button(left, text="Import Profiles", command=self.import_profiles).pack(fill='x')
        ttk.Button(left, text="Clear All", command=self.clear_all).pack(fill='x', pady=(5, 0))

        self.figure, self.ax = plt.subplots(figsize=(6.8, 5), facecolor="#1e1e1e")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("motion_notify_event", self.on_drag)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("motion_notify_event", self.show_tooltip)

        self.tooltip = tk.Label(self.canvas_widget, bg="#000", fg="#fff", font=("Segoe UI", 9),
                                bd=1, relief=tk.SOLID, padx=5, pady=1)
        self.tooltip.place_forget()

    def load_profiles_from_file(self):
        if os.path.exists(PROFILE_PATH):
            try:
                with open(PROFILE_PATH, "r") as f:
                    self.profiles = json.load(f)
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load speed_profiles.json:\n{e}")

    def save_profiles_to_file(self):
        try:
            with open(PROFILE_PATH, "w") as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Failed", str(e))

    def new_curve(self):
        self.current_name = ""
        self.name_entry.delete(0, tk.END)
        self.current_curve = self.default_profile.copy()
        self.draw_graph()

    def save_curve(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Name Required", "Please enter a profile name.")
            return
        if len(self.current_curve) != 10:
            messagebox.showerror("Invalid Curve", "Profile must have exactly 10 points.")
            return
        self.profiles[name] = [self.current_curve.copy()]  # Store as nested list
        self.current_name = name
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)
        self.update_dropdown()
        self.profile_combo.set(name)
        self.save_profiles_to_file()
        messagebox.showinfo("Saved", f'"{name}" saved to speed_profiles.json.')

    def profile_selected(self, event):
        selected = self.profile_combo.get()
        if selected in self.profiles:
            self.set_profile(selected)

    def set_profile(self, name):
        self.current_name = name
        curve = self.profiles[name]
        self.current_curve = curve[0] if isinstance(curve[0], list) else curve
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)
        self.profile_combo.set(name)
        self.draw_graph()

    def update_dropdown(self):
        self.profile_combo['values'] = list(self.profiles.keys())

    def clear_all(self):
        self.profiles = {}
        self.current_name = ""
        self.current_curve = self.default_profile.copy()
        self.name_entry.delete(0, tk.END)
        self.profile_combo.set("")
        self.update_dropdown()
        self.draw_graph()
        self.save_profiles_to_file()

    def export_profiles(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not path:
            return
        try:
            with open(path, "w") as f:
                f.write("public static volatile Dictionary<string, List<List<double>>> SpeedProfiles = new Dictionary<string, List<List<double>>>()\n{\n")
                for name, values in self.profiles.items():
                    values_list = values[0] if isinstance(values[0], list) else values
                    values_str = ", ".join(f"{v:.3f}" for v in values_list)
                    f.write(f'    {{ "{name}", new List<List<double>> {{ new List<double> {{ {values_str} }} }} }},\n')
                f.write("};\n")
            messagebox.showinfo("Exported", f"Profiles exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def import_profiles(self):
        path = filedialog.askopenfilename(filetypes=[("Text or JSON Files", "*.txt *.json")])
        if not path:
            return
        try:
            with open(path, "r") as f:
                content = f.read()

            matches = re.findall(r'"(.*?)"\s*,\s*new List<List<double>>\s*{[^}]*{([^}]*)}', content)
            if not matches:
                raise ValueError("No valid profiles found.")

            for name, data in matches:
                values = [float(v.strip()) for v in data.strip().split(',')]
                if len(values) == 10:
                    self.profiles[name] = [values]  # Store as nested list

            self.update_dropdown()
            self.set_profile(list(self.profiles.keys())[0])
            self.save_profiles_to_file()
        except Exception as e:
            messagebox.showerror("Import Failed", str(e))

    def draw_graph(self):
        self.ax.clear()
        x = list(range(1, 11))
        y = self.current_curve
        self.ax.plot(x, y, color="cyan", linewidth=2)
        self.ax.scatter(x, y, color='red', s=40)
        self.ax.set_title(f"{self.current_name or 'New Curve'}", fontsize=12)
        self.ax.set_xlabel("Point (Outer ➡ Inner)", fontsize=10)
        self.ax.set_ylabel("Multiplier", fontsize=10)
        self.ax.set_xlim(1, 10)
        self.ax.set_ylim(0, 5.5)
        self.ax.grid(True, linestyle="--", color="#555", linewidth=0.6)
        self.canvas.draw()

    def on_click(self, event):
        if not event.inaxes:
            return
        x, y = event.xdata, event.ydata
        index = int(round(x)) - 1
        if 0 <= index < 10 and 0.1 <= y <= 5.0:
            self.dragging_index = index
            self.current_curve[index] = round(y, 3)
            self.draw_graph()

    def on_drag(self, event):
        if self.dragging_index is not None and event.inaxes:
            y = event.ydata
            if y is not None and 0.1 <= y <= 5.0:
                self.current_curve[self.dragging_index] = round(y, 3)
                self.draw_graph()

    def on_release(self, event):
        self.dragging_index = None

    def show_tooltip(self, event):
        if not event.inaxes:
            self.tooltip.place_forget()
            return
        x, y = event.xdata, event.ydata
        index = int(round(x)) - 1
        if 0 <= index < 10:
            actual_y = self.current_curve[index]
            if abs(actual_y - y) < 0.2:
                self.tooltip.config(text=f"Point {index+1}: {actual_y:.3f}")
                self.tooltip.place(x=event.guiEvent.x + 15, y=event.guiEvent.y - 10)
                return
        self.tooltip.place_forget()


if __name__ == "__main__":
    app = ProfileEditor()
    app.mainloop()
