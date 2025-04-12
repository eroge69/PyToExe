import tkinter as tk
from tkinter import filedialog
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class DataVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Visualizer")
        self.root.geometry("800x600")
        
        self.df = None
        self.filtered_df = None
        
        self.create_widgets()

    def create_widgets(self):
        # File upload button
        self.upload_btn = tk.Button(self.root, text="Upload Excel File", command=self.upload_file)
        self.upload_btn.pack(pady=10)
        
        # Data Filter Frame
        self.filter_frame = tk.Frame(self.root)
        self.filter_frame.pack(pady=10)
        
        self.filter_label = tk.Label(self.filter_frame, text="Select Column for Filtering:")
        self.filter_label.pack(side=tk.LEFT, padx=5)
        
        self.column_menu = tk.OptionMenu(self.filter_frame, tk.StringVar(), '')
        self.column_menu.pack(side=tk.LEFT, padx=5)
        
        self.filter_value_entry = tk.Entry(self.filter_frame)
        self.filter_value_entry.pack(side=tk.LEFT, padx=5)
        
        self.filter_btn = tk.Button(self.filter_frame, text="Apply Filter", command=self.apply_filter)
        self.filter_btn.pack(side=tk.LEFT, padx=5)

        # Visualization Buttons
        self.visualize_btn = tk.Button(self.root, text="Visualize Data", command=self.visualize_data)
        self.visualize_btn.pack(pady=20)

    def upload_file(self):
        # Upload Excel file and read it
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.df = pd.read_excel(file_path)
            self.filtered_df = self.df.copy()  # Initially, no filter applied
            
            # Update filter options based on columns in the dataset
            columns = self.df.columns.tolist()
            self.column_menu['menu'].delete(0, 'end')
            for col in columns:
                self.column_menu['menu'].add_command(label=col, command=tk._setit(self.column_menu.variable, col))
            
            print(f"Data loaded successfully from {file_path}")

    def apply_filter(self):
        # Apply filter to the DataFrame based on user input
        column = self.column_menu.variable.get()
        filter_value = self.filter_value_entry.get()

        if column and filter_value:
            try:
                self.filtered_df = self.df[self.df[column] == filter_value]
                print(f"Applied filter on {column} with value {filter_value}")
            except Exception as e:
                print(f"Error applying filter: {e}")
    
    def visualize_data(self):
        if self.filtered_df is None or self.filtered_df.empty:
            print("No data to visualize. Please upload data and apply filter if necessary.")
            return
        
        # Create a Plotly figure
        fig = make_subplots(rows=1, cols=1)
        
        # Create a plot based on the available columns in the filtered dataset
        columns = self.filtered_df.columns.tolist()
        
        # Simple example: Create a bar chart with the first two columns (you can customize this)
        fig.add_trace(
            go.Bar(x=self.filtered_df[columns[0]], y=self.filtered_df[columns[1]], name=columns[1]),
            row=1, col=1
        )
        
        # Show the figure
        fig.show()

# Create the main window
root = tk.Tk()

# Create and run the application
app = DataVisualizerApp(root)
root.mainloop()
