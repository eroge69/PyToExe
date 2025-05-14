import pandas as pd
import tkinter as tk
from tkinter import messagebox
import datetime

# Load the Excel file
file_path = "C:/Users/9zhanwah_yap/Downloads/test.xlsx"  # Change this to your actual file path
staff_sheet = "Staff Info"  # Sheet containing ID and Names
wrench_sheet = "Torque Wrench Data"  # Sheet containing torque values
save_sheet = "Test Results"  # Sheet where entries will be saved

font_style = ("Arial", 16, "bold")  # Larger, bold font

# Read sheets into Pandas
user_data = pd.read_excel(file_path, sheet_name=staff_sheet)
wrench_data = pd.read_excel(file_path, sheet_name=wrench_sheet)

# Function to reset the app back to the initial state
def reset_app():
    id_entry.delete(0, tk.END)
    torque_id_entry.delete(0, tk.END)
    num1_entry.delete(0, tk.END)
    num2_entry.delete(0, tk.END)
    num3_entry.delete(0, tk.END)

    name_label.grid_remove()
    torque_id_label.grid_remove()
    torque_id_entry_frame.grid_remove()
    verify_torque_id_button.grid_remove()
    torque_label.grid_remove()
    num1_label.grid_remove()
    num1_entry.grid_remove()
    num2_label.grid_remove()
    num2_entry.grid_remove()
    num3_label.grid_remove()
    num3_entry.grid_remove()
    validate_button.grid_remove()
    result_label.grid_remove()

def show_large_popup(title, message, passed=None, error=False):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry("400x200")

    # Ensure pop-up gets focus immediately
    popup.focus_force()  # Force focus to the pop-up window
    popup.grab_set()  # Prevent interaction with the main window until pop-up is closed

    # Determine text color
    if error:
        text_color = "black"  # Orange for errors
    elif passed is not None:
        text_color = "green" if passed else "red"  # Green for pass, red for fail
    else:
        text_color = "black"  # Default text color

    label = tk.Label(popup, text=message, font=("Arial", 18, "bold"), wraplength=350, fg=text_color)
    label.pack(pady=20)

    # Bind Enter key to close the pop-up
    popup.bind("<Return>", lambda event: popup.destroy())
    
    tk.Button(popup, text="OK", command=popup.destroy, font=("Arial", 14, "bold"), width=10, fg = text_color, activeforeground=text_color).pack(pady=10)

    # Center the pop-up window
    popup.update_idletasks()
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x_position = (screen_width // 2) - (400 // 2)
    y_position = (screen_height // 2) - (200 // 2)
    popup.geometry(f"400x200+{x_position}+{y_position}")

    # Center the pop-up window
    popup.update_idletasks()
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x_position = (screen_width // 2) - (400 // 2)
    y_position = (screen_height // 2) - (200 // 2)
    popup.geometry(f"400x200+{x_position}+{y_position}")

def validate_and_submit(event):
    if num1_entry.get() and num2_entry.get() and num3_entry.get():  # Ensures all fields are filled
        check_and_save()

# Function to verify ID
def verify_id():
    user_id = id_entry.get()
    
    if not user_id.isdigit():
        show_large_popup("Error", "Staff ID not found. Please input a valid ID.", error=True)
        return

    if user_id in user_data['Staff ID'].astype(str).values:
        name = user_data.loc[user_data['Staff ID'].astype(str) == user_id, 'Staff Name'].values[0]
        name_label.config(text=f"Name: {name}")
        name_label.grid(row=1, column=1)
        torque_id_label.grid(row=2, column=0)
        torque_id_entry_frame.grid(row=2, column=1)
        ae_label.pack(side="left")
        torque_id_entry.pack(side="right")
        verify_torque_id_button.grid(row=2, column=2)
        torque_id_entry.focus()
    else:
        show_large_popup("Error", "Staff ID not found. Please input a valid ID.", error=True)

# Function to validate Torque ID and reveal torque entries
def validate_torque_id():
    torque_id = torque_id_entry.get()
    
    if not torque_id.isdigit():
        show_large_popup("Error", "Torque Wrench ID not found. Please input a valid ID.", error=True)
        return

    if int(torque_id) in wrench_data['Torque Wrench ID'].values:
        row = wrench_data.loc[wrench_data['Torque Wrench ID'] == int(torque_id)].values[0]

        torque_label.grid(row=3, column=1)
        num1_label.grid(row=4, column=0)
        num1_entry.grid(row=4, column=1)
        num2_label.grid(row=5, column=0)
        num2_entry.grid(row=5, column=1)
        num3_label.grid(row=6, column=0)
        num3_entry.grid(row=6, column=1)
        validate_button.grid(row=5, column=2)

        num1_entry.focus()
    
    else:
        show_large_popup("Error", "Torque ID not found. Please input a valid ID.", error=True)

# Function to validate torque values and save entries
def check_and_save():
    try:
        inputs = [float(num1_entry.get()), float(num2_entry.get()), float(num3_entry.get())]
    except ValueError:
        show_large_popup("Error", "Please enter valid numbers.", error=True)
        return  # Stops execution if invalid input is detected
    
    torque_id = torque_id_entry.get()
    row = wrench_data.loc[wrench_data['Torque Wrench ID'] == int(torque_id)].values[0]
    ranges = [(float(row[2]), float(row[3])), (float(row[4]), float(row[5])), (float(row[6]), float(row[7]))]

    passed = all(low <= val <= high for val, (low, high) in zip(inputs, ranges))

    show_large_popup("Result", "Torque wrench passed! Torque wrench can be used!" if passed else "Torque wrench FAILED! Do NOT use. Please inform the tool store administrator immediately.", passed)
    
    save_entries(id_entry.get(), torque_id, inputs)
    reset_app()

# Function to save entries with server-based Date & Time
def save_entries(user_id, torque_id, torque_values):
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Server time
    
    # Create new entry row
    df_new_entry = pd.DataFrame([[timestamp, user_id, int(torque_id), *torque_values]], 
                                columns=["Date & Time", "Staff ID", "Torque Wrench ID", "Value 1", "Value 2", "Value 3"])
    
    try:
        existing_data = pd.read_excel(file_path, sheet_name=save_sheet)
        df_new_entry = pd.concat([existing_data, df_new_entry], ignore_index=True)
    except Exception:
        pass  # Ignore if file doesn't exist yet

    with pd.ExcelWriter(file_path, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
        df_new_entry.to_excel(writer, sheet_name=save_sheet, index=False)

# Create Tkinter UI
root = tk.Tk()
root.title("Torque Test Station")
root.state("zoomed")  # Enables windowed fullscreen mode

# Configure layout for centered elements
for i in range(20):  # Reserve 20 rows for layout spacing
    root.rowconfigure(i, weight=1)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

font_style = ("Arial", 16, "bold")  # Larger font for better visibility

# User ID Input
tk.Label(root, text="Please enter your 8 digit Staff ID:", font=font_style).grid(row=0, column=0, sticky="ew")
id_entry = tk.Entry(root, font=font_style)
id_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
id_entry.focus()
tk.Button(root, text="Verify Staff ID", command=verify_id, font=font_style, height=2).grid(row=0, column=2)

name_label = tk.Label(root, text="Name:", font=font_style)
torque_id_label = tk.Label(root, text="Enter 4 digit Torque Wrench ID:", font=font_style)
torque_id_entry_frame = tk.Frame(root)
torque_id_entry_frame.grid()
ae_label = tk.Label(torque_id_entry_frame, text='AE', font=font_style)
torque_id_entry = tk.Entry(torque_id_entry_frame, font=font_style)
verify_torque_id_button = tk.Button(root, text="Verify Torque Wrench ID", command=validate_torque_id, font=font_style, height=2)

torque_label = tk.Label(root, text="Enter Torque Values:", font=font_style)
num1_label = tk.Label(root, text="Torque Value 1:", font=font_style)
num1_entry = tk.Entry(root, font=font_style)
num2_label = tk.Label(root, text="Torque Value 2:", font=font_style)
num2_entry = tk.Entry(root, font=font_style)
num3_label = tk.Label(root, text="Torque Value 3:", font=font_style)
num3_entry = tk.Entry(root, font=font_style)
validate_button = tk.Button(root, text="Check Values", command=check_and_save, font=font_style, height=2)

result_label = tk.Label(root, text="", font=font_style)

# Hide elements initially
reset_app()

# Bind Enter key for validation
id_entry.bind("<Return>", lambda event: verify_id())
torque_id_entry.bind("<Return>", lambda event: validate_torque_id())
num1_entry.bind("<Return>", validate_and_submit)
num2_entry.bind("<Return>", validate_and_submit)
num3_entry.bind("<Return>", validate_and_submit)

root.mainloop()