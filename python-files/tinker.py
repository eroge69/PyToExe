import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

def calculate_and_write_remarks():
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not file_path:
        return  # User cancelled

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Error reading Excel file: {e}")
        return

    # --- Language Selection ---
    selected_language = language_var.get()
    if selected_language == "English":
        remarks_dict = {
            "Insufficient": "Insufficient job",
            "Do More": "Do more",
            "Good": "Good",
            "Very Good": "Very good",
            "Excellent": "Excellent",
        }
    elif selected_language == "French":
        remarks_dict = {
            "Insufficient": "Travail insuffisant",
            "Do More": "Faites plus",
            "Good": "Bon",
            "Very Good": "Très bon",
            "Excellent": "Excellent",
        }
    elif selected_language == "Arabic":
        remarks_dict = {
            "Insufficient": "عمل غير كاف",
            "Do More": "ابذل المزيد",
            "Good": "جيد",
            "Very Good": "جيد جدا",
            "Excellent": "ممتاز",
        }
    else:
        messagebox.showerror("Error", "Invalid language selected.")
        return

    # --- Number of Exams ---
    num_exams = exams_var.get()
    if num_exams not in [2, 3, 4]:
        messagebox.showerror("Error", "Please select 2, 3, or 4 exams.")
        return

    # --- Activity Weight ---
    activity_weight = activity_var.get()
    if activity_weight not in [0, 25, 33.33, 40]:
        messagebox.showerror("Error", "Please select a valid activity weight.")
        return

    # --- Calculate Exam Weight ---
    exam_weight = 100 - activity_weight

    def get_cell_value(df, cell):
        try:
            row_index, col_index = get_row_col_indices(cell)
            if row_index < len(df) and col_index < len(df.columns):
                value = df.iloc[row_index, col_index]
                if pd.isna(value):  # Handle empty cells
                    return 0
                return value
            else:
                return 0 #treat out of bound as 0
        except:
            return 0

    def get_row_col_indices(cell):
        col_str = ""
        row_str = ""
        for char in cell:
            if 'A' <= char <= 'Z':
                col_str += char
            elif '0' <= char <= '9':
                row_str += char
        col = 0
        for i, char in enumerate(reversed(col_str)):
            col += (ord(char) - ord('A') + 1) * (26 ** i)
        row = int(row_str)
        return row - 1, col - 1

    # --- Main Calculation and Remarks Logic ---
    for index, row in df.iterrows(): #Iterate through the rows.
        if num_exams == 2:
            exam1_grade = get_cell_value(df, 'G18')
            exam2_grade = get_cell_value(df, 'I18')
            total_exam_grade = (exam1_grade + exam2_grade) / 2
            final_grade = (exam_weight / 100) * total_exam_grade + (activity_weight / 100) * 0 #activity is zero

            if activity_weight == 0:
                remark_cell = 'K18'
            else:
                remark_cell = 'M18'

        elif num_exams == 3:
            exam1_grade = get_cell_value(df, 'G18')
            exam2_grade = get_cell_value(df, 'I18')
            exam3_grade = get_cell_value(df, 'K18')
            total_exam_grade = (exam1_grade + exam2_grade + exam3_grade) / 3
            final_grade = (exam_weight / 100) * total_exam_grade + (activity_weight / 100) * 0

            if activity_weight == 0:
                remark_cell = 'M18'
            else:
                remark_cell = 'O18'

        elif num_exams == 4:
            exam1_grade = get_cell_value(df, 'G18')
            exam2_grade = get_cell_value(df, 'I18')
            exam3_grade = get_cell_value(df, 'K18')
            exam4_grade = get_cell_value(df, 'M18')
            total_exam_grade = (exam1_grade + exam2_grade + exam3_grade + exam4_grade) / 4
            final_grade = (exam_weight / 100) * total_exam_grade + (activity_weight / 100) * 0
            remark_cell = 'Q18'

        if final_grade < 10:
            remark = remarks_dict["Insufficient"]
        elif 10 <= final_grade < 12:
            remark = remarks_dict["Do More"]
        elif 12 <= final_grade < 14:
            remark = remarks_dict["Good"]
        elif 14 <= final_grade < 16:
            remark = remarks_dict["Very Good"]
        else:
            remark = remarks_dict["Excellent"]

        # Write the remark to the appropriate cell
        try:
            row_index, col_index = get_row_col_indices(remark_cell)
            df.iloc[row_index, col_index] = remark
        except Exception as e:
            messagebox.showerror("Error", f"Error writing remark: {e}")
            return

    # --- Save the Modified Excel File ---
    try:
        save_path = filedialog.asksaveasfilename(
            title="Save Modified Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if save_path:
            df.to_excel(save_path, index=False)
            messagebox.showinfo("Success", "Results written to Excel file.")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving Excel file: {e}")

# --- GUI Setup ---
window = tk.Tk()
window.title("Grade Calculator with Remarks")
window.geometry("400x200")
window.resizable(False, False)

style = ttk.Style()
style.theme_use('clam')

# --- Language Selection ---
language_label = ttk.Label(window, text="Select Language:")
language_label.pack(pady=10)

languages = ["English", "French", "Arabic"]
language_var = tk.StringVar(value="English")  # Default language
language_combobox = ttk.Combobox(window, textvariable=language_var, values=languages, state="readonly")
language_combobox.pack(pady=5)

# --- Number of Exams ---
exams_label = ttk.Label(window, text="Number of Exams:")
exams_label.pack(pady=10)

exams_var = tk.IntVar(value=2)
exams_frame = ttk.Frame(window)
exams_frame.pack()
ttk.Radiobutton(exams_frame, text="2", variable=exams_var, value=2).pack(side=tk.LEFT)
ttk.Radiobutton(exams_frame, text="3", variable=exams_var, value=3).pack(side=tk.LEFT)
ttk.Radiobutton(exams_frame, text="4", variable=exams_var, value=4).pack(side=tk.LEFT)

# --- Activity Weight ---
activity_label = ttk.Label(window, text="Activity Weight (%):")
activity_label.pack(pady=10)

activity_var = tk.DoubleVar(value=25)  # Default activity weight
activity_frame = ttk.Frame(window)
activity_frame.pack()
ttk.Radiobutton(activity_frame, text="25%", variable=activity_var, value=25).pack(side=tk.LEFT)
ttk.Radiobutton(activity_frame, text="33.33%", variable=activity_var, value=33.33).pack(side=tk.LEFT)
ttk.Radiobutton(activity_frame, text="40%", variable=activity_var, value=40).pack(side=tk.LEFT)
ttk.Radiobutton(activity_frame, text="0%", variable=activity_var, value=0).pack(side=tk.LEFT)

# --- Process Button ---
process_button = ttk.Button(window, text="Process Excel", command=calculate_and_write_remarks)
process_button.pack(pady=15)

window.mainloop()
