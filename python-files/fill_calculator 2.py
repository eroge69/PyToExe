
import tkinter as tk
from tkinter import messagebox

# Data extracted from the Excel file
standard_target_fill_ratio = 0.425
blown_target_fill_ratio_min = 0.50
blown_target_fill_ratio_max = 0.65

# Function to calculate fill ratio for standard cables
def calculate_fill_ratio(duct_id, cable_data):
    duct_area = 3.14159 * (duct_id / 2) ** 2
    total_cable_area = 0
    for cable_od, num_cables in cable_data:
        if cable_od > 0 and num_cables > 0:
            cable_area = 3.14159 * (cable_od / 2) ** 2
            total_cable_area += cable_area * num_cables
    fill_ratio = total_cable_area / duct_area
    return fill_ratio

# Function to check fill ratio for standard cables
def check_fill_ratio():
    try:
        duct_id = float(entry_duct_id.get())
        cable_data = []
        for i in range(10):
            cable_od = float(cable_entries[i][0].get() or 0)
            num_cables = int(cable_entries[i][1].get() or 0)
            cable_data.append((cable_od, num_cables))
        
        # Adjust target fill ratio based on Step 2 answers
        adjusted_target_fill_ratio = standard_target_fill_ratio
        if dropdown_conduit_id_greater_70.get().upper() == "YES":
            adjusted_target_fill_ratio += 0.025
        if dropdown_pull_length_less_125.get().upper() == "YES":
            adjusted_target_fill_ratio += 0.025
        if dropdown_pull_length_greater_300.get().upper() == "YES":
            adjusted_target_fill_ratio -= 0.025
        if dropdown_total_sweeps_greater_135.get().upper() == "YES":
            adjusted_target_fill_ratio -= 0.025
        
        fill_ratio = calculate_fill_ratio(duct_id, cable_data)
        if fill_ratio <= adjusted_target_fill_ratio:
            result_label.config(text=f"Fill ratio is OK: {fill_ratio*100:.2f}%\nTarget fill ratio: {adjusted_target_fill_ratio*100:.3f}%", fg="green", font=("Helvetica", 12, "bold"))
        elif fill_ratio <= adjusted_target_fill_ratio * 1.05:
            result_label.config(text=f"Fill ratio is within 5% over the target: {fill_ratio*100:.2f}%\nTarget fill ratio: {adjusted_target_fill_ratio*100:.3f}%", fg="orange", font=("Helvetica", 12, "bold"))
        else:
            result_label.config(text=f"Fill ratio exceeds target by more than 5%: {fill_ratio*100:.2f}%\nTarget fill ratio: {adjusted_target_fill_ratio*100:.3f}%", fg="red", font=("Helvetica", 12, "bold"))
    except ValueError:
        result_label.config(text="Please enter valid numeric values.", fg="red", font=("Helvetica", 12, "bold"))

# Function to handle Step 2 questions for standard cables
def handle_step2_questions():
    try:
        conduit_id_greater_70 = dropdown_conduit_id_greater_70.get().upper()
        pull_length_less_125 = dropdown_pull_length_less_125.get().upper()
        pull_length_greater_300 = dropdown_pull_length_greater_300.get().upper()
        total_sweeps_greater_135 = dropdown_total_sweeps_greater_135.get().upper()
        if conduit_id_greater_70 not in ["YES", "NO"] or pull_length_less_125 not in ["YES", "NO"] or pull_length_greater_300 not in ["YES", "NO"] or total_sweeps_greater_135 not in ["YES", "NO"]:
            result_label.config(text="Please select 'YES' or 'NO' for Step 2 questions.", fg="red", font=("Helvetica", 12, "bold"))
            return
        # Proceed to calculate fill ratio if all answers are valid
        check_fill_ratio()
    except ValueError:
        result_label.config(text="Please select valid values for Step 2 questions.", fg="red", font=("Helvetica", 12, "bold"))

# Function to calculate fill ratio for blown cables
def calculate_blown_cable_fill_ratio(duct_id, blown_cable_od):
    duct_area = 3.14159 * (duct_id / 2) ** 2
    blown_cable_area = 3.14159 * (blown_cable_od / 2) ** 2
    fill_ratio = blown_cable_area / duct_area
    return fill_ratio

# Function to check fill ratio for blown cables
def check_blown_cable_fill_ratio():
    try:
        duct_id = float(entry_blown_duct_id.get())
        blown_cable_od = float(entry_blown_cable_od.get())
        fill_ratio = calculate_blown_cable_fill_ratio(duct_id, blown_cable_od)
        if blown_target_fill_ratio_min <= fill_ratio <= blown_target_fill_ratio_max:
            blown_result_label.config(text=f"Blown Cable Fill ratio is OK: {fill_ratio*100:.2f}%\nTarget fill ratio range: {blown_target_fill_ratio_min*100:.3f}% - {blown_target_fill_ratio_max*100:.3f}%", fg="green", font=("Helvetica", 12, "bold"))
        else:
            blown_result_label.config(text=f"Blown Cable Fill ratio is outside the target range: {fill_ratio*100:.2f}%\nTarget fill ratio range: {blown_target_fill_ratio_min*100:.3f}% - {blown_target_fill_ratio_max*100:.3f}%", fg="red", font=("Helvetica", 12, "bold"))
    except ValueError:
        blown_result_label.config(text="Please enter valid numeric values.", fg="red", font=("Helvetica", 12, "bold"))

# Function to save results to a text file
def save_results():
    try:
        with open('fill_ratio_results.txt', 'w') as f:
            f.write(result_label.cget("text") + "\n")
            f.write(blown_result_label.cget("text") + "\n")
        messagebox.showinfo("Save Results", "Results saved to fill_ratio_results.txt")
    except Exception as e:
        messagebox.showerror("Save Results", f"Error saving results: {e}")

# Create the GUI application
app = tk.Tk()
app.title("Fill Ratio Calculator")

# Create and place labels and entry widgets for standard cables section
tk.Label(app, text="Standard Cables Section", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=4, padx=10, pady=10)
tk.Label(app, text="Internal Duct ID (mm):").grid(row=1, column=0, padx=10, pady=10)
entry_duct_id = tk.Entry(app)
entry_duct_id.grid(row=1, column=1, padx=10, pady=10)

# Create and place labels and dropdown menus for Step 2
tk.Label(app, text="Conduit ID greater than 70 mm (YES/NO):").grid(row=2, column=0, padx=10, pady=10)
dropdown_conduit_id_greater_70 = tk.StringVar(app)
dropdown_conduit_id_greater_70.set("NO")
tk.OptionMenu(app, dropdown_conduit_id_greater_70, "YES", "NO").grid(row=2, column=1, padx=10, pady=10)

tk.Label(app, text="Pull Length less than 125 m (YES/NO):").grid(row=3, column=0, padx=10, pady=10)
dropdown_pull_length_less_125 = tk.StringVar(app)
dropdown_pull_length_less_125.set("NO")
tk.OptionMenu(app, dropdown_pull_length_less_125, "YES", "NO").grid(row=3, column=1, padx=10, pady=10)

tk.Label(app, text="Pull Length greater than 300 m (YES/NO):").grid(row=4, column=0, padx=10, pady=10)
dropdown_pull_length_greater_300 = tk.StringVar(app)
dropdown_pull_length_greater_300.set("NO")
tk.OptionMenu(app, dropdown_pull_length_greater_300, "YES", "NO").grid(row=4, column=1, padx=10, pady=10)

tk.Label(app, text="Total Sweeps greater than 135 deg (YES/NO):").grid(row=5, column=0, padx=10, pady=10)
dropdown_total_sweeps_greater_135 = tk.StringVar(app)
dropdown_total_sweeps_greater_135.set("NO")
tk.OptionMenu(app, dropdown_total_sweeps_greater_135, "YES", "NO").grid(row=5, column=1, padx=10, pady=10)

# Create and place labels and entry widgets for Step 3 and Step 4
cable_entries = []
for i in range(10):
    tk.Label(app, text=f"Cable/Subduct OD {i+1} (mm):").grid(row=6+i, column=0, padx=10, pady=10)
    entry_cable_od = tk.Entry(app)
    entry_cable_od.grid(row=6+i, column=1, padx=10, pady=10)
    tk.Label(app, text=f"Number of Cables/Subducts {i+1}:").grid(row=6+i, column=2, padx=10, pady=10)
    entry_num_cables = tk.Entry(app)
    entry_num_cables.grid(row=6+i, column=3, padx=10, pady=10)
    cable_entries.append((entry_cable_od, entry_num_cables))

# Create and place the calculate button for standard cables
calculate_button = tk.Button(app, text="Calculate Fill Ratio", command=handle_step2_questions)
calculate_button.grid(row=16, column=0, columnspan=4, padx=10, pady=10)

# Create and place the result label for standard cables
result_label = tk.Label(app, text="", font=("Helvetica", 12, "bold"))
result_label.grid(row=17, column=0, columnspan=4, padx=10, pady=10)

# Create and place the disclaimer label for standard cables
disclaimer_label = tk.Label(app, text="Disclaimer: This does not include overpulls and is a guide only.", font=("Helvetica", 10))
disclaimer_label.grid(row=18, column=0, columnspan=4, padx=10, pady=10)

# Create and place labels and entry widgets for blown cables section
tk.Label(app, text="Blown Cables Section", font=("Helvetica", 14,"bold")).grid(row=19, column=0, columnspan=4, padx=10, pady=10)
tk.Label(app, text="Internal Duct ID (mm):").grid(row=20, column=0, padx=10, pady=10)
entry_blown_duct_id = tk.Entry(app)
entry_blown_duct_id.grid(row=20, column=1, padx=10, pady=10)

tk.Label(app, text="Blown Cable Diameter (mm):").grid(row=21, column=0, padx=10, pady=10)
entry_blown_cable_od = tk.Entry(app)
entry_blown_cable_od.grid(row=21, column=1, padx=10, pady=10)

# Create and place the calculate button for blown cables
calculate_blown_button = tk.Button(app, text="Calculate Blown Cable Fill Ratio", command=check_blown_cable_fill_ratio)
calculate_blown_button.grid(row=22, column=0, columnspan=4, padx=10, pady=10)

# Create and place the result label for blown cables
blown_result_label = tk.Label(app, text="", font=("Helvetica", 12, "bold"))
blown_result_label.grid(row=23, column=0, columnspan=4, padx=10, pady=10)

# Create and place the save results button
save_button = tk.Button(app, text="Save Results", command=save_results)
save_button.grid(row=24, column=0, columnspan=4, padx=10, pady=10)

# Run the application
app.mainloop()
