import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import random
from datetime import datetime, timedelta

# Mapping grade to age range
grade_age = {
   1: (6, 7), 2: (7, 8), 3: (8, 9), 4: (9, 10), 5: (10, 11),
   6: (11, 12), 7: (12, 13), 8: (13, 14), 9: (14, 15), 10: (15, 16),
   11: (16, 17), 12: (17, 18)
}

def generate_random_dob(grade):
    age_range = grade_age.get(grade, (10, 12))
    age = random.randint(*age_range)
    today = datetime.today()
    dob = today - timedelta(days=age * 365 + random.randint(0, 364))
    return dob.strftime('%d-%m-%Y')

class GradeEntry:
    def __init__(self, parent, row):
        self.grade_var = tk.StringVar()
        self.count_var = tk.IntVar()
        self.admin_code_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="Male")
        self.is_learning_var = tk.StringVar(value="1")

        grade_options = [f"Grade {i}" for i in range(1, 13)]
        gender_options = ["Male", "Female"]
        is_learning_options = ["1", "0"]

        self.grade_dropdown = tk.OptionMenu(parent, self.grade_var, *grade_options)
        self.count_entry = tk.Entry(parent, textvariable=self.count_var, width=5)
        self.admin_entry = tk.Entry(parent, textvariable=self.admin_code_var, width=10)
        self.gender_dropdown = tk.OptionMenu(parent, self.gender_var, *gender_options)
        self.is_learning_dropdown = tk.OptionMenu(parent, self.is_learning_var, *is_learning_options)

        self.grade_dropdown.grid(row=row, column=0)
        self.count_entry.grid(row=row, column=1)
        self.admin_entry.grid(row=row, column=2)
        self.gender_dropdown.grid(row=row, column=3)
        self.is_learning_dropdown.grid(row=row, column=4)

class App:
    def __init__(self, root):
        self.root = root
        root.title("Demo ID Generator")

        # Start roll number
        tk.Label(root, text="Start Roll No:").grid(row=0, column=0, sticky='e')
        self.start_roll_var = tk.StringVar()
        tk.Entry(root, textvariable=self.start_roll_var).grid(row=0, column=1, columnspan=4, sticky='w')

        # Labels
        tk.Label(root, text="Grade").grid(row=1, column=0)
        tk.Label(root, text="Count").grid(row=1, column=1)
        tk.Label(root, text="Teacher Code").grid(row=1, column=2)
        tk.Label(root, text="Gender").grid(row=1, column=3)
        tk.Label(root, text="Is Learning").grid(row=1, column=4)

        # Grade entry rows
        self.grade_entries = []
        self.add_grade_entry(row=2)

        tk.Button(root, text="+ Add Grade", command=self.add_grade_entry).grid(row=999, column=0, sticky='w')

        self.format_var = tk.StringVar(value='v1')
        tk.Radiobutton(root, text='v1 Format', variable=self.format_var, value='v1').grid(row=999, column=1, sticky='w')
        tk.Radiobutton(root, text='v2 Format', variable=self.format_var, value='v2').grid(row=999, column=2, sticky='w')

        tk.Button(root, text="Generate & Export", command=self.generate_data).grid(row=1000, column=0, columnspan=5, pady=10)

    def add_grade_entry(self, row=None):
        if row is None:
            row = len(self.grade_entries) + 2
        entry = GradeEntry(self.root, row)
        self.grade_entries.append(entry)

    def generate_data(self):
        start_roll = self.start_roll_var.get()
        if not start_roll:
            messagebox.showerror("Input Error", "Please enter a valid roll number.")
            return

        all_data = []
        current_roll_number = start_roll

        def increment_roll(roll):
            if roll.isdigit():
                return str(int(roll) + 1).zfill(len(roll))
            else:
                prefix = ''.join(filter(str.isalpha, roll))
                number = ''.join(filter(str.isdigit, roll))
                incremented = str(int(number) + 1).zfill(len(number))
                return prefix + incremented

        for entry in self.grade_entries:
            try:
                grade_text = entry.grade_var.get()
                if not grade_text:
                    continue
                grade = int(grade_text.split()[1])
                grade_full_text = grade_text
                count = entry.count_var.get()
                admin = entry.admin_code_var.get()
                gender = entry.gender_var.get()
                is_learning = entry.is_learning_var.get()

                for _ in range(count):
                    if self.format_var.get() == 'v1':
                        student = {
                            'Roll Number': current_roll_number,
                            'Is Learning': is_learning,
                            'Grade': grade_full_text,
                            'Name': f"Demo {current_roll_number[-2:]}",
                            'Gender': gender.lower(),
                            'DOB': generate_random_dob(grade),
                            'Teacher Code': admin,
                            'Subscription ID': '',
                            'Pin': '1234',
                            'Extra Col 1': '',
                            'Extra Col 2': '',
                            'Extra Col 3': '',
                            'Extra Col 4': ''
                        }
                    else:  # v2 format
                        student = {
                            'Student Code': current_roll_number,
                            'Name': f"Demo {current_roll_number[-2:]}",
                            'Center Code': admin,
                            'Grade': grade_full_text,
                            'Section (Optional)': '',
                            'Gender': gender.lower(),
                            'Medium': 'English',
                            'Streaming': is_learning,
                            'Streaming Password': 'hello',
                            'PIN': '',
                            'Local Access': '1',
                            'Secondary Medium': ''
                        }

                    all_data.append(student)
                    current_roll_number = increment_roll(current_roll_number)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

        df = pd.DataFrame(all_data)

        file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Data exported successfully to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()


















