# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 14:40:27 2025

@author: Lab-4
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from pyproj import Transformer, CRS
import os

class DLTMToWGS84UTMConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("DLTM 2 WGS84 ")
        self.root.geometry("450x250")

        # GUI Elements
        self.label = tk.Label(root, text="DLTM to WGS84", font=("Arial", 14))
        self.label.pack(pady=10)

        # Input File Selection
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=5)

        self.input_label = tk.Label(self.input_frame, text="Select Input Excel File:")
        self.input_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(self.input_frame, width=30)
        self.input_entry.pack(side=tk.LEFT, padx=5)

        self.input_button = tk.Button(self.input_frame, text="Browse", command=self.browse_input)
        self.input_button.pack(side=tk.LEFT)

        # Output File Selection
        self.output_frame = tk.Frame(root)
        self.output_frame.pack(pady=5)

        self.output_label = tk.Label(self.output_frame, text="Select Output Excel File:")
        self.output_label.pack(side=tk.LEFT)

        self.output_entry = tk.Entry(self.output_frame, width=30)
        self.output_entry.pack(side=tk.LEFT, padx=5)

        self.output_button = tk.Button(self.output_frame, text="Browse", command=self.browse_output)
        self.output_button.pack(side=tk.LEFT)

        # UTM Zone Input
        self.zone_frame = tk.Frame(root)
        self.zone_frame.pack(pady=5)

        self.zone_label = tk.Label(self.zone_frame, text="Enter Target UTM Zone (e.g., 40 for Dubai):")
        self.zone_label.pack(side=tk.LEFT)

        self.zone_entry = tk.Entry(self.zone_frame, width=10)
        self.zone_entry.insert(0, "40")  # Default to Zone 40, common for Dubai
        self.zone_entry.pack(side=tk.LEFT, padx=5)

        # Hemisphere Selection
        self.hemisphere_frame = tk.Frame(root)
        self.hemisphere_frame.pack(pady=5)

        self.hemisphere_label = tk.Label(self.hemisphere_frame, text="Select Hemisphere:")
        self.hemisphere_label.pack(side=tk.LEFT)

        self.hemisphere_var = tk.StringVar(value="Northern")
        self.hemisphere_menu = tk.OptionMenu(self.hemisphere_frame, self.hemisphere_var, "Northern", "Southern")
        self.hemisphere_menu.pack(side=tk.LEFT, padx=5)

        # Convert Button
        self.convert_button = tk.Button(root, text="Convert to WGS84 UTM", command=self.convert_coordinates)
        self.convert_button.pack(pady=10)

        # Add Watermark (@Joyal) in the bottom-right corner
        self.watermark = tk.Label(root, text="@Joyal", font=("Arial", 10), fg="black")
        self.watermark.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)  # Position in bottom-right

        self.input_file = None
        self.output_file = None

    def browse_input(self):
        self.input_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if self.input_file:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.input_file)

    def browse_output(self):
        self.output_file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if self.output_file:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_file)

    def convert_coordinates(self):
        if not self.input_file or not self.output_file:
            messagebox.showerror("Error", "Please select both input and output Excel files.")
            return

        try:
            # Read the Excel file
            df = pd.read_excel(self.input_file, header=None)
            if df.shape[1] < 3:
                raise ValueError("Excel file must have at least 3 columns (Point No, Easting, Northing).")

            # Extract columns
            point_nos = df.iloc[:, 0].astype(str)
            eastings = df.iloc[:, 1].astype(float)
            northings = df.iloc[:, 2].astype(float)

            # Get UTM zone and hemisphere
            try:
                utm_zone = int(self.zone_entry.get())
                if not 1 <= utm_zone <= 60:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid UTM zone number (1-60).")
                return

            hemisphere = self.hemisphere_var.get()

            # Define DLTM CRS (EPSG:3997)
            dltm_crs = CRS.from_epsg(3997)  # Dubai Local Transverse Mercator

            # Define target WGS84 UTM CRS based on zone and hemisphere
            utm_epsg = 32600 + utm_zone if hemisphere == "Northern" else 32700 + utm_zone  # 326xx for Northern, 327xx for Southern
            wgs84_utm_crs = CRS.from_epsg(utm_epsg)

            # Create transformer for DLTM to WGS84 UTM
            transformer = Transformer.from_crs(dltm_crs, wgs84_utm_crs, always_xy=True)

            # Convert coordinates
            utm_eastings = []
            utm_northings = []
            for easting, northing in zip(eastings, northings):
                utm_easting, utm_northing = transformer.transform(easting, northing)
                utm_eastings.append(utm_easting)
                utm_northings.append(utm_northing)

            # Create output DataFrame
            output_df = pd.DataFrame({
                "Point No": point_nos,
                "Easting (WGS84 UTM)": utm_eastings,
                "Northing (WGS84 UTM)": utm_northings,
                "UTM Zone": [utm_zone] * len(point_nos),
                "Hemisphere": [hemisphere] * len(point_nos)
            })

            # Save to Excel
            output_df.to_excel(self.output_file, index=False)
            messagebox.showinfo("Success", f"Converted coordinates saved to:\n{self.output_file}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert coordinates:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DLTMToWGS84UTMConverter(root)
    root.mainloop()