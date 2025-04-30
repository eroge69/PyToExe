import tkinter as tk
from tkinter import filedialog, messagebox
import folium
import webbrowser
import os

class EarthCloneApp:
    def __init__(self, master):
        self.master = master
        master.title("Google Earth Clone")
        master.geometry("400x300")
        self.label = tk.Label(master, text="Google Earth Clone (Simplified)", font=("Arial", 14))
        self.label.pack(pady=10)

        self.add_layer_button = tk.Button(master, text="عرض خريطة تفاعلية", command=self.show_map)
        self.add_layer_button.pack(pady=10)

        self.import_gpx_button = tk.Button(master, text="استيراد GPX", command=self.import_gpx)
        self.import_gpx_button.pack(pady=10)

        self.import_kml_button = tk.Button(master, text="استيراد KML", command=self.import_kml)
        self.import_kml_button.pack(pady=10)

    def show_map(self):
        self.map = folium.Map(location=[30.0444, 31.2357], zoom_start=6)
        map_path = os.path.join(os.getcwd(), "map.html")
        self.map.save(map_path)
        webbrowser.open(map_path)

    def import_gpx(self):
        filepath = filedialog.askopenfilename(filetypes=[("GPX files", "*.gpx")])
        if filepath:
            messagebox.showinfo("نجاح", f"تم استيراد ملف GPX:
{filepath}")

    def import_kml(self):
        filepath = filedialog.askopenfilename(filetypes=[("KML files", "*.kml")])
        if filepath:
            messagebox.showinfo("نجاح", f"تم استيراد ملف KML:
{filepath}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EarthCloneApp(root)
    root.mainloop()