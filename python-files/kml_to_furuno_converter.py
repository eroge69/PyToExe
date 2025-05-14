
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, parse as ET_parse
import os

def parse_kml_file(file_path):
    tree = ET_parse(file_path)
    root = tree.getroot()
    lines = []
    for placemark in root.iter('Placemark'):
        name_el = placemark.find('name')
        name = name_el.text if name_el is not None else "Unnamed"
        for line_string in placemark.iter('LineString'):
            coords_el = line_string.find('coordinates')
            if coords_el is not None:
                coords_text = coords_el.text.strip()
                coords = [tuple(map(float, coord.split(',')[:2])) for coord in coords_text.split()]
                lines.append({'name': name, 'coords': coords})
    return lines

def create_user_chart_csv(lines, out_path):
    data = []
    for line in lines:
        for lat, lon in line['coords']:
            data.append({
                'TYPE': 'LINE',
                'LAT': lat,
                'LON': lon,
                'NAME': line['name'],
                'DETAIL': 'Cable Route'
            })
    df = pd.DataFrame(data)
    df.to_csv(out_path, index=False)

def create_rtz(lines, out_path, route_name="Cable Route"):
    root = Element("route", version="1.0", xmlns="http://www.cirm.org/RTZ/1/0")
    route_info = SubElement(root, "routeInfo")
    SubElement(route_info, "routeName").text = route_name
    SubElement(route_info, "startTime").text = "2025-01-01T00:00:00Z"
    SubElement(route_info, "status").text = "planned"
    SubElement(route_info, "routeType").text = "other"

    wp_index = 1
    for line in lines:
        for lat, lon in line["coords"]:
            wp = SubElement(root, "waypoint", id=str(wp_index))
            SubElement(wp, "position", lat=str(lat), lon=str(lon))
            SubElement(wp, "name").text = f"WP{wp_index}"
            SubElement(wp, "radius").text = "0.1"
            SubElement(wp, "leg")
            wp_index += 1

    xml_str = minidom.parseString(Element.tostring(root, 'utf-8')).toprettyxml(indent="  ")
    with open(out_path, "w") as file:
        file.write(xml_str)

def run_gui():
    def load_kml():
        file_path = filedialog.askopenfilename(filetypes=[("KML files", "*.kml")])
        if not file_path:
            return
        try:
            lines = parse_kml_file(file_path)
            if not lines:
                messagebox.showerror("Error", "No cable lines found.")
                return
            base = os.path.splitext(file_path)[0]
            create_user_chart_csv(lines, base + "_user_chart.csv")
            create_rtz(lines, base + "_route.rtz")
            messagebox.showinfo("Success", "Files created:
- " + base + "_user_chart.csv\n- " + base + "_route.rtz")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("KML to Furuno Converter")
    root.geometry("400x200")

    label = tk.Label(root, text="Convert KML Cable Routes to Furuno Format", font=("Arial", 12))
    label.pack(pady=20)

    btn = tk.Button(root, text="Select KML File", command=load_kml, width=20, height=2)
    btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
