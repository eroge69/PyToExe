import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess
subprocess.run([sys.executable, "-m", "ensurepip", "--default-pip"])
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.run([sys.executable, "-m", "pip", "install", "tk"])
# subprocess.run(["pip", "install", "pandas"])
# subprocess.run(["pip", "install", "pillow"])
# subprocess.run([sys.executable, "-m", "pip", "install", "pillow"])

from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from datetime import datetime

# ================== COORDINATE CONFIGURATION ==================
COORDS_CONFIG = {
    1: {  # 1CHD NAVAL UNIT - Merit
        'rank': (1601.7, 580),
        'cadet_name': (411.6, 647.8),
        'registration_no': (496.4, 718.8),
        'college_name': (1168.5, 720.5),
        'unit': (380.2, 788.3),
        'competition': (1152.1, 788.3),
        'camp_name': (429.8, 927.1),
        'camp_place': (892.6, 927.1),
        'cert_number': (391.7, 1064.3),
        'place': (335.5, 1138.7),
        'date': (337.2, 1213.1),
        'position': (469.2, 858.3)
    },
    2: {  # 1CHD NAVAL UNIT - Participation
        'rank': (848.0, 656.0),
        'cadet_name': (1118.0, 654.0),
        'registration_no': (462.0, 724),
        'college_name': (1206.0, 722.0),
        'unit': (400, 790),
        'from_date': (1044.0, 862.0),
        'camp_name': (1086, 792),
        'camp_place': (344.0, 860),
        'cert_number': (391.7, 1064.3),
        'place': (335.5, 1138.7),
        'date': (337.2, 1213.1),
        'to_date': (1436.0, 862),
        'performance': (1238, 928)
    },
    3: {  # 1 CHD GIRLS BN - Merit
        'rank': (1601.7, 580),
        'cadet_name': (411.6, 647.8),
        'registration_no': (496.4, 718.8),
        'college_name': (1168.5, 720.5),
        'unit': (380.2, 788.3),
        'competition': (1152.1, 788.3),
        'camp_name': (429.8, 927.1),
        'camp_place': (892.6, 927.1),
        'cert_number': (391.7, 1064.3),
        'place': (335.5, 1138.7),
        'date': (337.2, 1213.1),
        'position': (469.2, 858.3)
    }, 
    4: {  # 1 CHD GIRLS BN - Participation
        'rank': (1600, 600),
        'cadet_name': (410, 670),
        'registration_no': (495, 740),
        'college_name': (1180, 745),
        'unit': (380, 810),
        'from_date': (1150, 810),
        'camp_name': (430, 950),
        'camp_place': (895, 950),
        'cert_number': (390, 1085),
        'place': (335, 1160),
        'date': (340, 1235),
        'to_date': (1150, 880),
        'performance': (500, 880)
    },
    5: {  # 2CHD BN - Merit
        'rank': (1601.7, 580),
        'cadet_name': (411.6, 647.8),
        'registration_no': (496.4, 718.8),
        'college_name': (1168.5, 720.5),
        'unit': (380.2, 788.3),
        'competition': (1152.1, 788.3),
        'camp_name': (429.8, 927.1),
        'camp_place': (892.6, 927.1),
        'cert_number': (391.7, 1064.3),
        'place': (335.5, 1138.7),
        'date': (337.2, 1213.1),
        'position': (469.2, 858.3)
    },
    6: {  # 2CHD BN - Participation
        'rank': (1600, 600),
        'cadet_name': (410, 670),
        'registration_no': (495, 740),
        'college_name': (1180, 745),
        'unit': (380, 810),
        'from_date': (1150, 810),
        'camp_name': (430, 950),
        'camp_place': (895, 950),
        'cert_number': (390, 1085),
        'place': (335, 1160),
        'date': (340, 1235),
        'to_date': (1150, 880),
        'performance': (500, 880)
    },
    7: {  # 1 CHD AIR SQN - Merit
        'rank': (1601.7, 580),
        'cadet_name': (411.6, 647.8),
        'registration_no': (496.4, 718.8),
        'college_name': (1168.5, 720.5),
        'unit': (380.2, 788.3),
        'competition': (1152.1, 788.3),
        'camp_name': (429.8, 927.1),
        'camp_place': (892.6, 927.1),
        'cert_number': (391.7, 1064.3),
        'place': (335.5, 1138.7),
        'date': (337.2, 1213.1),
        'position': (469.2, 858.3)
    },
    8: {  # 1 CHD AIR SQN - Participation
        'rank': (1600, 600),
        'cadet_name': (410, 670),
        'registration_no': (495, 740),
        'college_name': (1180, 745),
        'unit': (380, 810),
        'from_date': (1150, 810),
        'camp_name': (430, 950),
        'camp_place': (895, 950),
        'cert_number': (390, 1085),
        'place': (335, 1160),
        'date': (340, 1235),
        'to_date': (1150, 880),
        'performance': (500, 880)
    },
}

# ================== TEMPLATE MAPPING ==================
TEMPLATE_MAP = {
    ("1CHD NAVAL UNIT", "Merit"): 1,
    ("1CHD NAVAL UNIT", "Participation"): 2,
    ("1 CHD GIRLS BN", "Merit"): 3,
    ("1 CHD GIRLS BN", "Participation"): 4,
    ("2 CHD BN", "Merit"): 5,
    ("2 CHD BN", "Participation"): 6,
    ("1 CHD AIR SQN", "Merit"): 7,
    ("1 CHD AIR SQN", "Participation"): 8
}

class CertificateGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("NCC Certificate Generator")
        
        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(padx=220, pady=90, fill='x')

        # Excel upload controls
        self.excel_controls_frame = ttk.Frame(root)
        self.excel_path_var = tk.StringVar()
        
        # Initial options
        self.create_initial_options()
        
        # Dynamic fields container
        self.fields_frame = ttk.Frame(root)
        
        # Generate button
        self.btn_generate = ttk.Button(root, text="Generate Certificates", command=self.generate)

    def create_initial_options(self):
        # Wing Selection
        ttk.Label(self.main_frame, text="Select Wing:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.wing_var = tk.StringVar()
        self.wing_combobox = ttk.Combobox(self.main_frame, textvariable=self.wing_var, 
                                        values=["1CHD NAVAL UNIT", "1 CHD GIRLS BN", "2 CHD BN", "1 CHD AIR SQN"])
        self.wing_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.wing_combobox.current(0)

        # Certificate Type
        ttk.Label(self.main_frame, text="Certificate Type:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.cert_type_var = tk.StringVar(value="Merit")
        self.type_combobox = ttk.Combobox(self.main_frame, textvariable=self.cert_type_var, 
                                        values=["Merit", "Participation"], state="readonly")
        self.type_combobox.grid(row=1, column=1, padx=5, pady=5)

        # Processing Mode
        ttk.Label(self.main_frame, text="Processing Mode:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.mode_var = tk.StringVar(value="Excel")
        self.mode_combobox = ttk.Combobox(self.main_frame, textvariable=self.mode_var, 
                                        values=["Excel", "Individual"], state="readonly")
        self.mode_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.mode_var.trace('w', self.toggle_interface)
        self.cert_type_var.trace('w', self.toggle_cert_fields)

        # Excel controls
        ttk.Button(self.excel_controls_frame, text="Upload Excel File", 
                 command=self.select_excel).grid(row=0, column=0, padx=5)
        ttk.Label(self.excel_controls_frame, textvariable=self.excel_path_var).grid(row=0, column=1, padx=5)

    def create_individual_fields(self):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        # Common fields for both certificate types
        common_fields = [
            ("Rank:", "rank"),
            ("Cadet Name:", "cadet_name"),
            ("Registration No:", "registration_no"),
            ("College Name:", "college_name"),
            ("Unit:", "unit"),
            ("Camp Name:", "camp_name"),
            ("Camp Place:", "camp_place"),
            ("Cert Number:", "cert_number"),
            ("Place:", "place"),
            ("Date (DD-MM-YYYY):", "date")
        ]

        self.entries = {}
        for idx, (label, key) in enumerate(common_fields):
            ttk.Label(self.fields_frame, text=label).grid(row=idx, column=0, padx=5, pady=2, sticky='e')
            entry = ttk.Entry(self.fields_frame)
            entry.grid(row=idx, column=1, padx=5, pady=2)
            self.entries[key] = entry

        # Special fields for Merit certificates
        self.competition_label = ttk.Label(self.fields_frame, text="Competition (Merit Only):")
        self.competition_entry = ttk.Entry(self.fields_frame)
        self.position_label = ttk.Label(self.fields_frame, text="Position (Merit Only):")
        self.position_entry = ttk.Entry(self.fields_frame)
        
        # Special fields for Participation certificates
        self.from_date_label = ttk.Label(self.fields_frame, text="From Date (DD-MM-YYYY):")
        self.from_date_entry = ttk.Entry(self.fields_frame)
        self.to_date_label = ttk.Label(self.fields_frame, text="To Date (DD-MM-YYYY):")
        self.to_date_entry = ttk.Entry(self.fields_frame)
        self.performance_label = ttk.Label(self.fields_frame, text="Performance (Participation Only):")
        self.performance_combobox = ttk.Combobox(self.fields_frame, 
                                               values=["Average", "Good", "Very Good"], state="readonly")
        
        self.toggle_cert_fields()

        self.fields_frame.pack(padx=10, pady=10, fill='x')
        self.btn_generate.pack(pady=10)

    def toggle_interface(self, *args):
        if self.mode_var.get() == "Individual":
            self.create_individual_fields()
            self.excel_controls_frame.pack_forget()
        else:
            self.fields_frame.pack_forget()
            self.excel_controls_frame.pack(pady=10)
            self.btn_generate.pack(pady=10)

    def toggle_cert_fields(self, *args):
        if self.cert_type_var.get() == "Merit":
            # Show Merit fields
            self.competition_label.grid(row=10, column=0, padx=5, pady=2, sticky='e')
            self.competition_entry.grid(row=10, column=1, padx=5, pady=2)
            self.position_label.grid(row=11, column=0, padx=5, pady=2, sticky='e')
            self.position_entry.grid(row=11, column=1, padx=5, pady=2)
            
            # Hide Participation fields
            self.from_date_label.grid_remove()
            self.from_date_entry.grid_remove()
            self.to_date_label.grid_remove()
            self.to_date_entry.grid_remove()
            self.performance_label.grid_remove()
            self.performance_combobox.grid_remove()
        else:
            # Show Participation fields
            self.from_date_label.grid(row=10, column=0, padx=5, pady=2, sticky='e')
            self.from_date_entry.grid(row=10, column=1, padx=5, pady=2)
            self.to_date_label.grid(row=11, column=0, padx=5, pady=2, sticky='e')
            self.to_date_entry.grid(row=11, column=1, padx=5, pady=2)
            self.performance_label.grid(row=12, column=0, padx=5, pady=2, sticky='e')
            self.performance_combobox.grid(row=12, column=1, padx=5, pady=2)
            
            # Hide Merit fields
            self.competition_label.grid_remove()
            self.competition_entry.grid_remove()
            self.position_label.grid_remove()
            self.position_entry.grid_remove()

    def select_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.excel_path_var.set(file_path)

    def generate(self):
        try:
            wing = self.wing_var.get()
            cert_type = self.cert_type_var.get()
            mode = self.mode_var.get()

            if mode == "Excel":
                self.generate_from_excel(wing, cert_type)
            else:
                self.generate_individual(wing, cert_type)

        except Exception as e:
            messagebox.showerror("Error", f"Generation failed:\n{str(e)}")

    def generate_from_excel(self, wing, cert_type):
        file_path = self.excel_path_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select an Excel file first!")
            return

        try:
            df = pd.read_excel(file_path)
            required_columns = ['Rank', 'Name', 'Regt. No.', 'College Name', 'Unit', 
                               'Camp Name', 'Held At', 'Cert Number', 'Place', 'Date']
            
            if cert_type == "Merit":
                required_columns.extend(['Competition', 'Position'])
            else:
                required_columns.extend(['From Date', 'To Date', 'Performance'])

            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                raise ValueError(f"Missing required columns: {', '.join(missing)}")

            font = ImageFont.truetype("fonts/arial.ttf", 48)
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)

            template_number = TEMPLATE_MAP[(wing, cert_type)]
            template_path = f"templates/{template_number}.png"

            for index, row in df.iterrows():
                # Format date fields to remove time portion
                date_value = row.get('Date', '')
                if pd.notna(date_value):
                    if hasattr(date_value, 'strftime'):
                        date_value = date_value.strftime('%d-%m-%Y')
                    else:
                        date_value = str(date_value)
                
                from_date_value = row.get('From Date', '')
                if pd.notna(from_date_value):
                    if hasattr(from_date_value, 'strftime'):
                        from_date_value = from_date_value.strftime('%d-%m-%Y')
                    else:
                        from_date_value = str(from_date_value)
                
                to_date_value = row.get('To Date', '')
                if pd.notna(to_date_value):
                    if hasattr(to_date_value, 'strftime'):
                        to_date_value = to_date_value.strftime('%d-%m-%Y')
                    else:
                        to_date_value = str(to_date_value)

                data = {
                    'rank': str(row.get('Rank', '')),
                    'cadet_name': str(row.get('Name', '')),
                    'registration_no': str(row.get('Regt. No.', '')),
                    'college_name': str(row.get('College Name', '')),
                    'unit': str(row.get('Unit', '')),
                    'competition': str(row.get('Competition', '')),
                    'camp_name': str(row.get('Camp Name', '')),
                    'camp_place': str(row.get('Held At', '')),
                    'cert_number': str(row.get('Cert Number', '')),
                    'place': str(row.get('Place', '')),
                    'date': date_value,
                    'position': str(row.get('Position', '')),
                    'from_date': from_date_value,
                    'to_date': to_date_value,
                    'performance': str(row.get('Performance', ''))
                }

                image = Image.open(template_path)
                draw = ImageDraw.Draw(image)
                
                for field, pos in COORDS_CONFIG[template_number].items():
                    value = data.get(field, '')
                    if value:
                        draw.text(pos, value, font=font, fill="black")

                output_path = f"{output_dir}/{data['cadet_name'].replace(' ', '_')}_{cert_type}_{index}.png"
                image.save(output_path)

            messagebox.showinfo("Success", f"Generated {len(df)} certificates!")

        except Exception as e:
            messagebox.showerror("Error", f"Excel processing failed:\n{str(e)}")

    def generate_individual(self, wing, cert_type):
        try:
            data = {key: entry.get() for key, entry in self.entries.items()}
            
            # Format date fields for individual entry
            if data.get('date'):
                try:
                    parsed_date = datetime.strptime(data['date'], '%d-%m-%Y')
                    data['date'] = parsed_date.strftime('%d-%m-%Y')
                except ValueError:
                    pass
            
            if cert_type == "Merit":
                data['competition'] = self.competition_entry.get()
                data['position'] = self.position_entry.get()
                required_fields = ['rank', 'cadet_name', 'registration_no', 'college_name', 
                                 'unit', 'camp_name', 'camp_place', 'cert_number', 
                                 'place', 'date', 'competition', 'position']
            else:
                data['from_date'] = self.from_date_entry.get()
                data['to_date'] = self.to_date_entry.get()
                data['performance'] = self.performance_combobox.get()
                
                for date_field in ['from_date', 'to_date']:
                    if data.get(date_field):
                        try:
                            parsed_date = datetime.strptime(data[date_field], '%d-%m-%Y')
                            data[date_field] = parsed_date.strftime('%d-%m-%Y')
                        except ValueError:
                            pass
                
                required_fields = ['rank', 'cadet_name', 'registration_no', 'college_name', 
                                 'unit', 'camp_name', 'camp_place', 'cert_number', 
                                 'place', 'date', 'from_date', 'to_date', 'performance']

            # Check required fields
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                raise ValueError(f"The following fields are required: {', '.join(missing_fields)}")

            template_number = TEMPLATE_MAP[(wing, cert_type)]
            template_path = f"templates/{template_number}.png"
            
            image = Image.open(template_path)
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype("fonts/arial.ttf", 48)

            coords = COORDS_CONFIG[template_number]
            for field, pos in coords.items():
                value = data.get(field, "")
                if value:
                    draw.text(pos, value, font=font, fill="black")

            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = f"{output_dir}/{data['cadet_name'].replace(' ', '_')}_{cert_type}.png"
            image.save(output_path)
            
            messagebox.showinfo("Success", f"Certificate generated:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("720x720") 
    app = CertificateGenerator(root)
    root.mainloop()