import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime
import os
from tkcalendar import DateEntry
import re

class DataEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Entry Application")
        self.root.geometry("700x650")
        self.root.configure(bg="#2f7a78")
        
        # Excel file path
        self.excel_path = None
        
        # Initialize variables
        self.customer_name_var = tk.StringVar()
        self.job_card_var = tk.StringVar()
        self.technician_var = tk.StringVar()
        self.machine_sl_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.comments_var = tk.StringVar()
        self.department_var = tk.StringVar()
        
        # Service types checkboxes variables
        self.service_types = {
            "Breakdown": tk.BooleanVar(),
            "Service": tk.BooleanVar(),
            "New Installation": tk.BooleanVar(),
            "Chargeable": tk.BooleanVar(),
            "Delivery": tk.BooleanVar()
        }
        
        # Machine serial numbers list
        self.machine_serials = []
        
        # Technicians list for autocomplete
        self.technicians = ["Dilshan", "Ahmad", "Yasin", "Jerome", "Varghese", "Amir Khan", "Abdul Qayyum", "Abdul Rehman", "Alauthin Alpitchai", "Imran", "Rafakath", "Shahul", "Baiju", "Bijoy", "Ismail", "Rahamathullah", "Ashraf"]
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#2f7a78", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header_label = tk.Label(main_frame, text="Data Entry Application", font=("Arial", 16, "bold"), 
                               bg="#2f7a78", fg="white")
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        # File selection button
        file_button = tk.Button(main_frame, text="Select Excel File", command=self.select_file, 
                              bg="#1565c0", fg="white", font=("Arial", 10), padx=10)
        file_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
        
        # Display selected file
        self.file_label = tk.Label(main_frame, text="No file selected", fg="white", bg="#2f7a78")
        self.file_label.grid(row=3, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Form fields
        # Date
        date_label = tk.Label(main_frame, text="Date", fg="white", bg="#2f7a78", font=("Arial", 11))
        date_label.grid(row=4, column=0, sticky="w", pady=5)
        
        date_frame = tk.Frame(main_frame, bg="#2f7a78")
        date_frame.grid(row=4, column=1, sticky="ew", pady=5)
        
        self.date_entry = DateEntry(date_frame, width=30, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='dd-mm-yy')
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Calendar icon button
        calendar_icon = tk.Label(date_frame, text="📅", bg="#2f7a78", fg="white", font=("Arial", 12))
        calendar_icon.pack(side=tk.LEFT)
        
        # Customer Name
        customer_label = tk.Label(main_frame, text="Customer Name", fg="white", bg="#2f7a78", font=("Arial", 11))
        customer_label.grid(row=5, column=0, sticky="w", pady=5)
        
        customer_entry = tk.Entry(main_frame, textvariable=self.customer_name_var, width=35, font=("Arial", 11))
        customer_entry.grid(row=5, column=1, sticky="ew", pady=5)
        
        # Job Card No
        job_label = tk.Label(main_frame, text="Job Card No", fg="white", bg="#2f7a78", font=("Arial", 11))
        job_label.grid(row=6, column=0, sticky="w", pady=5)
        
        job_entry = tk.Entry(main_frame, textvariable=self.job_card_var, width=35, font=("Arial", 11))
        job_entry.grid(row=6, column=1, sticky="ew", pady=5)
        # Validate job card to accept only numbers
        job_entry.config(validate="key", validatecommand=(job_entry.register(self.validate_number), '%P'))
        
        # Technician
        tech_label = tk.Label(main_frame, text="Technician", fg="white", bg="#2f7a78", font=("Arial", 11))
        tech_label.grid(row=7, column=0, sticky="w", pady=5)
        
        tech_entry = tk.Entry(main_frame, textvariable=self.technician_var, width=35, font=("Arial", 11))
        tech_entry.grid(row=7, column=1, sticky="ew", pady=5)
        tech_entry.bind('<KeyRelease>', self.update_technician_list)
        
        # Technician dropdown list
        self.tech_listbox = tk.Listbox(main_frame, width=35, height=0, font=("Arial", 11))
        self.tech_listbox.grid(row=8, column=1, sticky="ew", pady=(0, 5))
        self.tech_listbox.grid_remove()  # Initially hidden
        self.tech_listbox.bind('<<ListboxSelect>>', self.on_tech_select)
        
        # Machine Serial No
        machine_label = tk.Label(main_frame, text="Machine Sl No:", fg="white", bg="#2f7a78", font=("Arial", 11))
        machine_label.grid(row=9, column=0, sticky="w", pady=5)
        
        machine_frame = tk.Frame(main_frame, bg="#2f7a78")
        machine_frame.grid(row=9, column=1, sticky="ew", pady=5)
        
        machine_entry = tk.Entry(machine_frame, textvariable=self.machine_sl_var, width=35, font=("Arial", 11))
        machine_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Plus button for adding more machine serials
        plus_button = tk.Button(machine_frame, text="+", command=self.add_machine_serial, 
                              bg="white", font=("Arial", 11, "bold"), width=2)
        plus_button.pack(side=tk.LEFT)
        
        # Machine serials list display
        self.machine_list_frame = tk.Frame(main_frame, bg="#2f7a78")
        self.machine_list_frame.grid(row=10, column=1, sticky="ew", pady=(0, 5))
        
        self.machine_list_label = tk.Label(self.machine_list_frame, text="", fg="white", bg="#2f7a78", 
                                          font=("Arial", 10), justify=tk.LEFT, wraplength=350)
        self.machine_list_label.pack(fill=tk.X)
        
        # Model
        model_label = tk.Label(main_frame, text="Model", fg="white", bg="#2f7a78", font=("Arial", 11))
        model_label.grid(row=11, column=0, sticky="w", pady=5)
        
        model_entry = tk.Entry(main_frame, textvariable=self.model_var, width=35, font=("Arial", 11))
        model_entry.grid(row=11, column=1, sticky="ew", pady=5)
        
        # Comments
        comments_label = tk.Label(main_frame, text="Comments", fg="white", bg="#2f7a78", font=("Arial", 11))
        comments_label.grid(row=12, column=0, sticky="w", pady=5)
        
        comments_entry = tk.Entry(main_frame, textvariable=self.comments_var, width=35, font=("Arial", 11))
        comments_entry.grid(row=12, column=1, sticky="ew", pady=5)
        
        # Type of Service - Checkboxes
        service_label = tk.Label(main_frame, text="Type of Service", fg="white", bg="#2f7a78", font=("Arial", 11))
        service_label.grid(row=13, column=0, sticky="nw", pady=5)
        
        service_frame = tk.Frame(main_frame, bg="#2f7a78")
        service_frame.grid(row=13, column=1, sticky="w", pady=5)
        
        row_idx = 0
        for service, var in self.service_types.items():
            cb = tk.Checkbutton(service_frame, text=service, variable=var, 
                              bg="#2f7a78", fg="white", selectcolor="#2f7a78", 
                              activebackground="#2f7a78", activeforeground="white",
                              font=("Arial", 11))
            cb.grid(row=row_idx, column=0, sticky="w")
            row_idx += 1
        
        # Department dropdown
        dept_label = tk.Label(main_frame, text="Department", fg="white", bg="#2f7a78", font=("Arial", 11))
        dept_label.grid(row=14, column=0, sticky="w", pady=5)
        
        departments = ["Digi", "Banking", "Triveni", "Nemo Q"]
        dept_dropdown = ttk.Combobox(main_frame, textvariable=self.department_var, 
                                   values=departments, width=33, font=("Arial", 11))
        dept_dropdown.grid(row=14, column=1, sticky="ew", pady=5)
        dept_dropdown.current(0)
        
        # Submit button
        submit_btn = tk.Button(main_frame, text="SUBMIT", command=self.submit_data, 
                             bg="#1565c0", fg="white", font=("Arial", 12, "bold"), 
                             width=15, height=2)
        submit_btn.grid(row=15, column=0, columnspan=2, pady=20)
        
        # Configure the grid
        main_frame.grid_columnconfigure(1, weight=1)
        
    def select_file(self):
        """Open file dialog to select Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.excel_path = file_path
            self.file_label.config(text=f"Selected file: {os.path.basename(file_path)}")
            
    def validate_number(self, value):
        """Validate input to only allow numbers"""
        if value == "" or value.isdigit():
            return True
        return False
            
    def add_machine_serial(self):
        """Add machine serial number to the list"""
        serial = self.machine_sl_var.get().strip()
        if serial:
            self.machine_serials.append(serial)
            self.machine_sl_var.set("")
            self.update_machine_list_display()
            
    def update_machine_list_display(self):
        """Update the display of machine serial numbers"""
        if self.machine_serials:
            text = "Added: " + ", ".join(self.machine_serials)
            self.machine_list_label.config(text=text)
        else:
            self.machine_list_label.config(text="")
            
    def update_technician_list(self, event):
        """Update technician dropdown based on input"""
        typed_text = self.technician_var.get().lower()
        
        if typed_text:
            matching_techs = [tech for tech in self.technicians if typed_text in tech.lower()]
            
            if matching_techs:
                self.tech_listbox.delete(0, tk.END)
                for tech in matching_techs:
                    self.tech_listbox.insert(tk.END, tech)
                self.tech_listbox.grid()
            else:
                self.tech_listbox.grid_remove()
        else:
            self.tech_listbox.grid_remove()
            
    def on_tech_select(self, event):
        """Handle technician selection from dropdown"""
        if self.tech_listbox.curselection():
            selected_idx = self.tech_listbox.curselection()[0]
            selected_tech = self.tech_listbox.get(selected_idx)
            self.technician_var.set(selected_tech)
            self.tech_listbox.grid_remove()
            
    def submit_data(self):
        """Submit the form data to Excel"""
        # Validate fields
        if not self.excel_path:
            messagebox.showerror("Error", "Please select an Excel file first")
            return
            
        if not self.customer_name_var.get().strip():
            messagebox.showerror("Error", "Customer Name is required")
            return
            
        if not self.job_card_var.get().strip():
            messagebox.showerror("Error", "Job Card No is required")
            return
            
        if not self.technician_var.get().strip():
            messagebox.showerror("Error", "Technician is required")
            return
            
        # Machine serial - use list if available, otherwise use text field
        machine_serial = ", ".join(self.machine_serials) if self.machine_serials else self.machine_sl_var.get().strip()
        
        if not machine_serial:
            messagebox.showerror("Error", "Machine Serial Number is required")
            return
            
        if not self.model_var.get().strip():
            messagebox.showerror("Error", "Model is required")
            return
            
        # Get selected service types
        service_types = []
        for service, var in self.service_types.items():
            if var.get():
                service_types.append(service)
                
        if not service_types:
            messagebox.showerror("Error", "Please select at least one Type of Service")
            return
        
        service_types_str = ", ".join(service_types)
        
        # Get department
        department = self.department_var.get()
        if not department:
            messagebox.showerror("Error", "Please select a Department")
            return
            
        # Prepare data
        data = {
            "Date": self.date_entry.get_date().strftime("%d-%m-%y"),
            "Customer Name": self.customer_name_var.get().strip(),
            "Job Card No:": self.job_card_var.get().strip(),
            "Type of Service": service_types_str,
            "Comments": self.comments_var.get().strip(),
            "Technician": self.technician_var.get().strip(),
            "Machine Sl No:": machine_serial,
            "Model": self.model_var.get().strip(),
            "Department": department
        }
        
        try:
            # Load Excel file
            try:
                workbook = pd.ExcelFile(self.excel_path)
                sheets = workbook.sheet_names
                
                # Check if all required sheets exist
                required_sheets = ["Digi", "Banking", "Triveni", "Nemo Q", "Master"]
                missing_sheets = [sheet for sheet in required_sheets if sheet not in sheets]
                
                if missing_sheets:
                    messagebox.showerror("Error", f"Missing sheets in Excel file: {', '.join(missing_sheets)}")
                    return
                    
                # Read all sheets
                dfs = {sheet: pd.read_excel(workbook, sheet) for sheet in sheets}
                
            except Exception as e:
                # If file doesn't exist or is empty, create new DataFrames
                dfs = {
                    "Digi": pd.DataFrame(columns=["Date", "Customer Name", "Job Card No:", "Type of Service", 
                                                "Comments", "Technician", "Machine Sl No:", "Model"]),
                    "Banking": pd.DataFrame(columns=["Date", "Customer Name", "Job Card No:", "Type of Service", 
                                                   "Comments", "Technician", "Machine Sl No:", "Model"]),
                    "Triveni": pd.DataFrame(columns=["Date", "Customer Name", "Job Card No:", "Type of Service", 
                                                    "Comments", "Technician", "Machine Sl No:", "Model"]),
                    "Nemo Q": pd.DataFrame(columns=["Date", "Customer Name", "Job Card No:", "Type of Service", 
                                                  "Comments", "Technician", "Machine Sl No:", "Model"]),
                    "Master": pd.DataFrame(columns=["Date", "Customer Name", "Job Card No:", "Type of Service", 
                                                  "Comments", "Technician", "Machine Sl No:", "Model", "Department"])
                }
            
            # Create data for specific department sheet (without Department column)
            dept_data = {k: v for k, v in data.items() if k != "Department"}
            
            # Append data to department sheet
            dept_df = dfs[department].copy()
            dept_df = pd.concat([dept_df, pd.DataFrame([dept_data])], ignore_index=True)
            dfs[department] = dept_df
            
            # Append data to Master sheet (with Department column)
            master_df = dfs["Master"].copy()
            master_df = pd.concat([master_df, pd.DataFrame([data])], ignore_index=True)
            dfs["Master"] = master_df
            
            # Write all sheets back to Excel
            with pd.ExcelWriter(self.excel_path) as writer:
                for sheet_name, df in dfs.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            messagebox.showinfo("Success", "Data submitted successfully!")
            
            # Clear form fields
            self.customer_name_var.set("")
            self.job_card_var.set("")
            self.technician_var.set("")
            self.machine_sl_var.set("")
            self.machine_serials = []
            self.update_machine_list_display()
            self.model_var.set("")
            self.comments_var.set("")
            
            # Reset checkboxes
            for var in self.service_types.values():
                var.set(False)
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = DataEntryApp(root)
    root.mainloop()