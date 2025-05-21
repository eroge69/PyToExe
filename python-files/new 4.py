import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class FinalFolderCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Folder Creator")
        self.root.geometry("1000x850")
        
        # Project type settings
        self.project_types = {
            "Master Plan": {
                "building_disciplines": {
                    "ARC": "Architectural",
                    "ELE": "Electrical",
                    "FPR": "Fire Protection",
                    "ICT": "Information & Communication Technology",
                    "MEC": "Mechanical",
                    "PLD": "Drainage",
                    "PLW": "Plumbing",
                    "STR": "Structural"
                },
                "master_plan_disciplines": {
                    "CIV": {"name": "Civil", "sub_disciplines": ["Roads", "Bridges", "Utilities"]},
                    "INF": {"name": "Infrastructure", "sub_disciplines": ["Water", "Sewage", "Power"]},
                    "URB": {"name": "Urban Planning", "sub_disciplines": ["Zoning", "LandUse"]},
                    "ENV": {"name": "Environmental", "sub_disciplines": ["EIA", "Sustainability"]},
                    "TRA": {"name": "Transportation", "sub_disciplines": ["Traffic", "PublicTransit"]},
                    "LSC": {"name": "Landscape", "sub_disciplines": ["Hardscape", "Softscape"]},
                    "GEO": {"name": "Geotechnical", "sub_disciplines": ["Soil", "Foundations"]},
                    "SRV": {"name": "Survey", "sub_disciplines": ["Topographic", "Boundary"]}
                },
                "file_types": {
                    "building": {
                        "MDL": ["RVT", "NWC", "IFC"],
                        "SHT": ["PDF", "DWG"],
                        "TECH_DOC": ["SPECS", "REPORTS", "BODR", "CALCS"],
                        "DOC": ["DOCX", "PDF", "XLSX"]
                    },
                    "master_plan": {
                        "SUR": ["DWG", "PDF", "SHP"],
                        "SHT": ["PDF", "DWG"],
                        "GIS": ["SHP", "GDB", "KML"],
                        "TECH_DOC": ["SPECS", "REPORTS", "STUDIES"]
                    },
                    "DIG": {
                        "FDM": ["IFC", "RVT", "NWD"],
                        "DOC": ["DOCX", "PDF"]
                    }
                }
            },
            "Building Project": {
                "disciplines": {
                    "ARC": "Architectural",
                    "ELE": "Electrical",
                    "FPR": "Fire Protection",
                    "ICT": "Information & Communication Technology",
                    "MEC": "Mechanical",
                    "PLD": "Drainage",
                    "PLW": "Plumbing",
                    "STR": "Structural"
                },
                "file_types": {
                    "default": {
                        "MDL": ["RVT", "NWC", "IFC"],
                        "SHT": ["PDF", "DWG"],
                        "DOC": ["DOCX", "PDF", "XLSX"]
                    }
                }
            }
        }
        
        # Application variables
        self.project_name = tk.StringVar()
        self.project_path = tk.StringVar()
        self.project_type = tk.StringVar()
        self.num_assets = tk.IntVar(value=1)
        self.asset_entries_data = []
        self.discipline_vars = {}
        self.sub_discipline_vars = {}
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")
        
        # Project info section
        tk.Label(main_frame, text="Project Name/Number:").grid(row=0, column=0, sticky="e", pady=5)
        tk.Entry(main_frame, textvariable=self.project_name, width=40).grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(main_frame, text="Save Location:").grid(row=1, column=0, sticky="e", pady=5)
        path_frame = tk.Frame(main_frame)
        path_frame.grid(row=1, column=1, sticky="ew", pady=5)
        tk.Entry(path_frame, textvariable=self.project_path, width=35).pack(side="left", fill="x", expand=True)
        tk.Button(path_frame, text="Browse", command=self.browse_path).pack(side="left", padx=5)
        
        # Project type selection
        tk.Label(main_frame, text="Project Type:").grid(row=2, column=0, sticky="e", pady=5)
        type_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.project_type, 
            values=list(self.project_types.keys()), 
            state="readonly"
        )
        type_combo.grid(row=2, column=1, sticky="w", pady=5, padx=5)
        type_combo.bind("<<ComboboxSelected>>", self.update_disciplines)
        
        # Number of assets
        tk.Label(main_frame, text="Number of Assets:").grid(row=3, column=0, sticky="e", pady=5)
        tk.Spinbox(
            main_frame, 
            from_=1, 
            to=20, 
            textvariable=self.num_assets, 
            command=self.update_asset_entries
        ).grid(row=3, column=1, sticky="w", pady=5, padx=5)
        
        # Asset names section
        self.assets_frame = tk.LabelFrame(main_frame, text="Asset Names", pady=10)
        self.assets_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        self.asset_entries = []
        self.update_asset_entries()
        
        # Disciplines section with notebook
        self.discipline_notebook = ttk.Notebook(main_frame)
        self.discipline_notebook.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Create tabs
        self.create_discipline_tabs()
        
        # Create button
        tk.Button(
            main_frame, 
            text="Create Folder Structure", 
            command=self.create_folders,
            bg="#4CAF50", 
            fg="white", 
            font=("Arial", 12)
        ).grid(row=6, column=0, columnspan=2, pady=20)
    
    def create_discipline_tabs(self):
        # Building disciplines tab
        self.building_frame = ttk.Frame(self.discipline_notebook)
        self.discipline_notebook.add(self.building_frame, text="Building Disciplines")
        self.building_canvas = tk.Canvas(self.building_frame, borderwidth=0)
        self.building_scrollbar = tk.Scrollbar(self.building_frame, orient="vertical", command=self.building_canvas.yview)
        self.building_scrollable_frame = tk.Frame(self.building_canvas)
        
        self.building_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.building_canvas.configure(
                scrollregion=self.building_canvas.bbox("all")
            )
        )
        
        self.building_canvas.create_window((0, 0), window=self.building_scrollable_frame, anchor="nw")
        self.building_canvas.configure(yscrollcommand=self.building_scrollbar.set)
        
        self.building_canvas.pack(side="left", fill="both", expand=True)
        self.building_scrollbar.pack(side="right", fill="y")
        
        # Master Plan disciplines tab
        self.master_plan_frame = ttk.Frame(self.discipline_notebook)
        self.discipline_notebook.add(self.master_plan_frame, text="Master Plan Disciplines")
        self.master_plan_canvas = tk.Canvas(self.master_plan_frame, borderwidth=0)
        self.master_plan_scrollbar = tk.Scrollbar(self.master_plan_frame, orient="vertical", command=self.master_plan_canvas.yview)
        self.master_plan_scrollable_frame = tk.Frame(self.master_plan_canvas)
        
        self.master_plan_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.master_plan_canvas.configure(
                scrollregion=self.master_plan_canvas.bbox("all")
            )
        )
        
        self.master_plan_canvas.create_window((0, 0), window=self.master_plan_scrollable_frame, anchor="nw")
        self.master_plan_canvas.configure(yscrollcommand=self.master_plan_scrollbar.set)
        
        self.master_plan_canvas.pack(side="left", fill="both", expand=True)
        self.master_plan_scrollbar.pack(side="right", fill="y")
    
    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.project_path.set(path)
    
    def update_disciplines(self, event=None):
        # Clear existing checkboxes
        for widget in self.building_scrollable_frame.winfo_children():
            widget.destroy()
        for widget in self.master_plan_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.discipline_vars = {}
        self.sub_discipline_vars = {}
        
        # Update based on project type
        if self.project_type.get() == "Master Plan":
            self.discipline_notebook.tab(0, state="normal")
            self.discipline_notebook.tab(1, state="normal")
            
            # Building disciplines
            for i, (code, name) in enumerate(self.project_types["Master Plan"]["building_disciplines"].items()):
                var = tk.BooleanVar(value=(code == "ARC"))  # Architectural checked by default
                self.discipline_vars[code] = var
                
                cb = tk.Checkbutton(
                    self.building_scrollable_frame, 
                    text=f"{code} - {name}", 
                    variable=var,
                    anchor="w",
                    width=30,
                    justify="left"
                )
                cb.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            # Master Plan disciplines with sub-disciplines
            for i, (code, data) in enumerate(self.project_types["Master Plan"]["master_plan_disciplines"].items()):
                var = tk.BooleanVar(value=(code == "CIV"))  # Civil checked by default
                self.discipline_vars[code] = var
                
                # Main discipline checkbox
                cb = tk.Checkbutton(
                    self.master_plan_scrollable_frame, 
                    text=f"{code} - {data['name']}", 
                    variable=var,
                    anchor="w",
                    width=30,
                    justify="left"
                )
                cb.grid(row=i*2, column=0, sticky="w", padx=5, pady=2)
                
                # Sub-disciplines frame
                sub_frame = tk.Frame(self.master_plan_scrollable_frame)
                sub_frame.grid(row=i*2+1, column=0, sticky="w", padx=25)
                
                for j, sub_disc in enumerate(data["sub_disciplines"]):
                    sub_var = tk.BooleanVar(value=True)
                    self.sub_discipline_vars[f"{code}_{sub_disc}"] = sub_var
                    
                    sub_cb = tk.Checkbutton(
                        sub_frame, 
                        text=sub_disc, 
                        variable=sub_var,
                        anchor="w"
                    )
                    sub_cb.grid(row=0, column=j, sticky="w", padx=5, pady=2)
        
        elif self.project_type.get() == "Building Project":
            # Only disable the Master Plan tab, keep Building Disciplines tab enabled
            self.discipline_notebook.tab(0, state="normal")  # Building Disciplines
            self.discipline_notebook.tab(1, state="disabled")  # Master Plan Disciplines
            
            # Simple disciplines for Building Project
            for i, (code, name) in enumerate(self.project_types["Building Project"]["disciplines"].items()):
                var = tk.BooleanVar(value=(code == "ARC"))  # Architectural checked by default
                self.discipline_vars[code] = var
                
                cb = tk.Checkbutton(
                    self.building_scrollable_frame, 
                    text=f"{code} - {name}", 
                    variable=var,
                    anchor="w",
                    width=30,
                    justify="left"
                )
                cb.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            # Select the Building Disciplines tab by default
            self.discipline_notebook.select(0)
    
    def update_asset_entries(self):
        # Save current entries before clearing
        self.save_current_entries()
        
        # Clear the frame
        for widget in self.assets_frame.winfo_children():
            widget.destroy()
        
        self.asset_entries = []
        
        # Create new entries
        for i in range(self.num_assets.get()):
            frame = tk.Frame(self.assets_frame)
            frame.pack(fill="x", pady=2)
            
            # Label
            tk.Label(frame, text=f"Asset {i+1}:").pack(side="left", padx=5)
            
            # Entry field - restore previous value if available
            entry = tk.Entry(frame)
            if i < len(self.asset_entries_data):
                entry.insert(0, self.asset_entries_data[i])
            entry.pack(side="left", fill="x", expand=True, padx=5)
            self.asset_entries.append(entry)
    
    def save_current_entries(self):
        # Save current values before they're destroyed
        self.asset_entries_data = []
        for entry in self.asset_entries:
            self.asset_entries_data.append(entry.get())
    
    def create_folders(self):
        # Validate inputs
        if not self.project_name.get():
            messagebox.showerror("Error", "Please enter project name/number")
            return
        
        if not self.project_path.get():
            messagebox.showerror("Error", "Please select save location")
            return
        
        if not self.project_type.get():
            messagebox.showerror("Error", "Please select project type")
            return
        
        # Save current entries before processing
        self.save_current_entries()
        
        # Check asset names
        for i, name in enumerate(self.asset_entries_data):
            if not name:
                messagebox.showerror("Error", f"Please enter name for Asset {i+1}")
                return
        
        # Create project directory
        project_dir = os.path.join(self.project_path.get(), f"Project_{self.project_name.get()}")
        
        try:
            if self.project_type.get() == "Master Plan":
                self.create_master_plan_folders(project_dir)
            else:
                self.create_building_project_folders(project_dir)
            
            messagebox.showinfo("Success", f"Folder structure created successfully at:\n{project_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Error creating folders:\n{str(e)}")
    
    def create_master_plan_folders(self, project_dir):
        # Create building disciplines with assets inside
        for code, var in self.discipline_vars.items():
            if code in self.project_types["Master Plan"]["building_disciplines"] and var.get():
                disc_dir = os.path.join(project_dir, code)
                
                # Create asset folders under discipline
                for asset_name in self.asset_entries_data:
                    asset_dir = os.path.join(disc_dir, asset_name)
                    
                    # Create building file types
                    for file_type, formats in self.project_types["Master Plan"]["file_types"]["building"].items():
                        file_type_dir = os.path.join(asset_dir, file_type)
                        
                        for fmt in formats:
                            os.makedirs(os.path.join(file_type_dir, fmt), exist_ok=True)
        
        # Create master plan disciplines with sub-disciplines
        for code, var in self.discipline_vars.items():
            if code in self.project_types["Master Plan"]["master_plan_disciplines"] and var.get():
                disc_data = self.project_types["Master Plan"]["master_plan_disciplines"][code]
                disc_dir = os.path.join(project_dir, code)
                
                # Create sub-disciplines
                for sub_disc in disc_data["sub_disciplines"]:
                    if self.sub_discipline_vars.get(f"{code}_{sub_disc}", tk.BooleanVar(value=True)).get():
                        sub_disc_dir = os.path.join(disc_dir, sub_disc)
                        
                        # Create master plan file types
                        for file_type, formats in self.project_types["Master Plan"]["file_types"]["master_plan"].items():
                            file_type_dir = os.path.join(sub_disc_dir, file_type)
                            
                            for fmt in formats:
                                os.makedirs(os.path.join(file_type_dir, fmt), exist_ok=True)
    
    def create_building_project_folders(self, project_dir):
        # Create assets with disciplines inside (standard structure)
        for asset_name in self.asset_entries_data:
            asset_dir = os.path.join(project_dir, asset_name)
            
            # Create discipline folders
            for code, var in self.discipline_vars.items():
                if var.get():
                    disc_dir = os.path.join(asset_dir, code)
                    
                    # Create file type folders
                    for file_type, formats in self.project_types["Building Project"]["file_types"]["default"].items():
                        file_type_dir = os.path.join(disc_dir, file_type)
                        
                        for fmt in formats:
                            os.makedirs(os.path.join(file_type_dir, fmt), exist_ok=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinalFolderCreatorApp(root)
    root.mainloop()