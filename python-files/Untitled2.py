import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from datetime import datetime

class AVGCExcel:
    def __init__(self, root):
        self.root = root
        self.root.title("AVGC Excel")
        self.root.geometry("1000x600")
        
        self.filename = None
        self.df = pd.DataFrame(np.nan, index=range(100), columns=[chr(65+i) for i in range(26)])
        
        self.create_menu()
        self.create_toolbar()
        self.create_spreadsheet()
        self.create_statusbar()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Formulas", command=self.toggle_formulas)
        menubar.add_cascade(label="View", menu=view_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Formatting buttons
        bold_btn = ttk.Button(toolbar, text="B", command=self.set_bold)
        bold_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        italic_btn = ttk.Button(toolbar, text="I", command=self.set_italic)
        italic_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Font size
        font_size = ttk.Combobox(toolbar, values=[8, 10, 12, 14, 16, 18, 20], width=3)
        font_size.set(12)
        font_size.pack(side=tk.LEFT, padx=2, pady=2)
        font_size.bind("<<ComboboxSelected>>", lambda e: self.set_font_size(font_size.get()))
        
        # Font family
        font_family = ttk.Combobox(toolbar, values=["Arial", "Times New Roman", "Courier New"], width=12)
        font_family.set("Arial")
        font_family.pack(side=tk.LEFT, padx=2, pady=2)
        font_family.bind("<<ComboboxSelected>>", lambda e: self.set_font_family(font_family.get()))
        
        # Formula bar
        formula_frame = ttk.Frame(toolbar)
        formula_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        ttk.Label(formula_frame, text="fx:").pack(side=tk.LEFT)
        self.formula_entry = ttk.Entry(formula_frame)
        self.formula_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.formula_entry.bind("<Return>", self.apply_formula)
    
    def create_spreadsheet(self):
        # Create a frame for the spreadsheet
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas and scrollbars
        self.canvas = tk.Canvas(container)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scroll = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scroll = ttk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Create the spreadsheet frame inside the canvas
        self.spreadsheet = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.spreadsheet, anchor="nw")
        
        # Create headers
        for j, col in enumerate(self.df.columns):
            header = ttk.Label(self.spreadsheet, text=col, relief=tk.RIDGE, width=10, anchor=tk.CENTER)
            header.grid(row=0, column=j+1, sticky="nsew")
        
        for i in range(1, 101):
            # Row numbers
            row_header = ttk.Label(self.spreadsheet, text=str(i), relief=tk.RIDGE, width=4, anchor=tk.CENTER)
            row_header.grid(row=i, column=0, sticky="nsew")
            
            # Cells
            for j, col in enumerate(self.df.columns):
                cell_var = tk.StringVar()
                cell_var.trace("w", lambda name, index, mode, var=cell_var, r=i-1, c=col: self.update_cell(var, r, c))
                
                cell = ttk.Entry(self.spreadsheet, textvariable=cell_var, width=10)
                cell.grid(row=i, column=j+1, sticky="nsew")
                cell.bind("<FocusIn>", lambda e, r=i-1, c=col: self.update_formula_bar(r, c))
                
                # Store cell widgets for later reference
                if not hasattr(self, 'cell_widgets'):
                    self.cell_widgets = {}
                self.cell_widgets[(i-1, col)] = cell
    
    def create_statusbar(self):
        self.status = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message):
        self.status.config(text=message)
        self.root.after(3000, lambda: self.status.config(text="Ready"))
    
    def update_cell(self, var, row, col):
        value = var.get()
        try:
            # Try to evaluate as formula if starts with =
            if value.startswith('='):
                result = eval(value[1:], {'__builtins__': None}, self.df.to_dict('list'))
                self.df.at[row, col] = result
            else:
                self.df.at[row, col] = value
        except:
            self.df.at[row, col] = value
    
    def update_formula_bar(self, row, col):
        value = self.df.at[row, col]
        if pd.isna(value):
            value = ""
        self.formula_entry.delete(0, tk.END)
        self.formula_entry.insert(0, str(value))
    
    def apply_formula(self, event):
        current_focus = self.root.focus_get()
        if hasattr(current_focus, 'grid_info'):
            info = current_focus.grid_info()
            row = info['row'] - 1
            col = chr(64 + info['column'])
            if row >= 0 and col in self.df.columns:
                self.df.at[row, col] = self.formula_entry.get()
                self.cell_widgets[(row, col)].delete(0, tk.END)
                self.cell_widgets[(row, col)].insert(0, self.formula_entry.get())
    
    def new_file(self):
        self.df = pd.DataFrame(np.nan, index=range(100), columns=[chr(65+i) for i in range(26)])
        self.filename = None
        self.update_status("New file created")
    
    def open_file(self):
        filetypes = [('CSV files', '*.csv'), ('Excel files', '*.xlsx'), ('All files', '*.*')]
        filename = filedialog.askopenfilename(filetypes=filetypes)