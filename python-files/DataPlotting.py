# -*- coding: utf-8 -*-
"""
Created on Thu May  8 15:45:28 2025

@author: m.taekema
"""

import tkinter as tk
from tkinter import filedialog, ttk
import csv
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.io as pio
import webbrowser
import os

selected_file_path = None  # Will store the selected file path
current_fig = None  # Stores the last generated plot

def show_plot(fig):
    temp_file = "temp_plot.html"
    fig.write_html(temp_file, auto_open=False)
    webbrowser.open('file://' + os.path.realpath(temp_file))
    
def read_csv_file(filepath):
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)  # Skip the header row
        data = []
        for row in reader:
            try:
                float_row = list(map(float, row))
                data.append(float_row)
            except ValueError:
                continue  # Skip row if any value cannot be converted to float
    if not data:
        print("No data in file.")
        return []
    columns = list(zip(*data))  # Transpose to get columns
    return columns

def plot_data(columns, sensor_type):
    global current_fig
    if len(columns) < 6:
        print("Not enough columns in data.")
        return

    fig = make_subplots(
        rows=1, 
        cols=2, 
        subplot_titles=("Redundant Deviation", "Position Deviation"),
        horizontal_spacing = 0.075)

    # Plot 1: Column 2 vs Column 6
    fig.add_trace(go.Scattergl(
        x=columns[1],
        y=columns[5],
        mode='markers',
        marker=dict(size=3),
        name="Sensor dieA vs dieB"
    ), row=1, col=1)
    fig.update_xaxes(title_text="Sensor dieA", row=1, col=1)            #X axis label
    fig.update_yaxes(title_text="Sensor dieB", row=1, col=1)    	    #Y axis label
 
    # Plot 2: Column 4 vs Column 5
    fig.add_trace(go.Scattergl(
        x=columns[3],
        y=columns[4],
        mode='markers',
        marker=dict(size=3, color='orange'),
        name="RLS Encoder vs Sensor dieA"
    ), row=1, col=2)
    fig.update_xaxes(title_text="RLS Rotary Encoder", row=1, col=2)     # X axis label
    fig.update_yaxes(title_text="Sensor dieA", row=1, col=2)            #Y axis label

    # Set layout properties
    fig.update_layout(
        title_text=f"Sensor: {sensor_type}",
        height=900,
        width=2000,
        showlegend=True
    )

    # Fix Y-axis for both plots
    fig.update_yaxes(range=[-10, 10], row=1, col=1)
    fig.update_yaxes(range=[-10, 10], row=1, col=2)

    current_fig = fig       # Save the figure for potential export
    show_plot(fig)          # Show fig in browser.
    
def on_save():
    global current_fig
    if not current_fig:
        print("No plot to save.")
        return

    # Suggest a default filename based on the loaded data file (if available)
    default_name = "plot.html"
    if selected_file_path:
        base_filename = os.path.splitext(os.path.basename(selected_file_path))[0]
        default_name = f"{base_filename}_plot.html"

    # Open save dialog
    save_path = filedialog.asksaveasfilename(
        defaultextension=".html",
        filetypes=[("HTML files", "*.html")],
        initialfile=default_name,
        title="Save Plot As"
    )

    if save_path:
        current_fig.write_html(save_path)
        print(f"Plot saved to {save_path}")
    
    
def on_browse():
    global selected_file_path
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        selected_file_path = file_path
        file_entry_var.set(file_path)

def on_plot():
    if not selected_file_path:
        print("No file selected.")
        return
    sensor_type = sensor_var.get()
    columns = read_csv_file(selected_file_path)
    plot_data(columns, sensor_type)

def main():
    global sensor_var, file_entry_var

    root = tk.Tk()
    root.title("Sensor Data Plotter")
    root.geometry("500x250")

    # Sensor dropdown
    tk.Label(root, text="Select Sensor Type:", font=("Arial", 12)).pack(pady=5)
    sensor_var = tk.StringVar(value="MLX90316")
    sensor_dropdown = ttk.Combobox(root, textvariable=sensor_var, values=["MLX90316", "MLX90333"], state="readonly", font=("Arial", 11))
    sensor_dropdown.pack(pady=5)

    # File browser
    browse_button = tk.Button(root, text="Browse for CSV File", command=on_browse, font=("Arial", 11), width=25)
    browse_button.pack(pady=5)

    # File path entry
    file_entry_var = tk.StringVar()
    file_entry = tk.Entry(root, textvariable=file_entry_var, font=("Arial", 10), width=180, state='readonly')
    file_entry.pack(pady=5)

    # Plot button
    plot_button = tk.Button(root, text="Plot", command=on_plot, font=("Arial", 11), width=25)
    plot_button.pack(pady=10)
    
    # Save button
    save_button = tk.Button(root, text="Save Plot as HTML", command=on_save, font=("Arial", 11), width=25)
    save_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
