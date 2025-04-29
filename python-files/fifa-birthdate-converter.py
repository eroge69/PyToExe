import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pyperclip

class FifaDate:
    def __init__(self, days=None):
        if days is not None:
            self.set(days)
        else:
            self.day = 1
            self.month = 1
            self.year = 2000

    def get_days(self):
        a = (14 - self.month) // 12
        y = self.year + 4800 - a
        m = self.month + 12 * a - 3
        return self.day + (153 * m + 2) // 5 + y * 365 + y // 4 - y // 100 + y // 400 - 32045 - 2299160

    def set(self, days):
        a = days + 32044 + 2299160
        b = (4 * a + 3) // 146097
        c = a - (b * 146097) // 4
        d = (4 * c + 3) // 1461
        e = c - (1461 * d) // 4
        m = (5 * e + 2) // 153
        self.day = e - (153 * m + 2) // 5 + 1
        self.month = m + 3 - 12 * (m // 10)
        self.year = b * 100 + d - 4800 + m // 10

def date_to_fifa():
    global date_copy_button
    try:
        day = int(day_entry.get())
        month = months.index(month_combo.get()) + 1
        year = int(year_entry.get())
        
        if day < 1 or day > 31:
            raise ValueError("Day must be between 1 and 31")
        
        datetime(year, month, day)  # Validate date
        
        fifa_date = FifaDate()
        fifa_date.day = day
        fifa_date.month = month
        fifa_date.year = year
        fifa_days = fifa_date.get_days()
        
        date_result_label.config(text=f"FIFA DB Birthdate: {fifa_days}", foreground="green")
        if 'date_copy_button' not in globals() or not date_copy_button.winfo_exists():
            date_copy_button = ttk.Button(date_result_frame, text="Copy", command=copy_date_result)
            date_copy_button.pack(side="left", padx=5)
    except ValueError as e:
        date_result_label.config(text=f"Error: {str(e)}", foreground="red")
        if 'date_copy_button' in globals() and date_copy_button.winfo_exists():
            date_copy_button.destroy()

def fifa_to_date():
    global fifa_copy_button
    try:
        fifa_days = int(fifa_entry.get())
        fifa_date = FifaDate(fifa_days)
        date_str = f"{fifa_date.day:02d} {months[fifa_date.month-1]} {fifa_date.year}"
        fifa_result_label.config(text=f"Gregorian Birthdate: {date_str}", foreground="green")
        if 'fifa_copy_button' not in globals() or not fifa_copy_button.winfo_exists():
            fifa_copy_button = ttk.Button(fifa_result_frame, text="Copy", command=copy_fifa_result)
            fifa_copy_button.pack(side="left", padx=5)
    except ValueError:
        fifa_result_label.config(text="Invalid FIFA days number!", foreground="red")
        if 'fifa_copy_button' in globals() and fifa_copy_button.winfo_exists():
            fifa_copy_button.destroy()

def copy_date_result():
    result_text = date_result_label.cget("text").split(": ")[1]
    pyperclip.copy(result_text)

def copy_fifa_result():
    result_text = fifa_result_label.cget("text").split(": ")[1]
    pyperclip.copy(result_text)

def show_info():
    # Create a custom Toplevel window for the info popup
    info_window = tk.Toplevel(root)
    info_window.title("About")
    info_window.geometry("300x150")
    info_window.resizable(False, False)
    info_window.transient(root)  # Ties it to the main window
    info_window.grab_set()  # Makes it modal

    # Frame to hold the content
    info_frame = ttk.Frame(info_window)
    info_frame.pack(expand=True)

    # Labels with centered text
    ttk.Label(info_frame, text="FIFA Birthdate Converter (Version 1.0)", justify="center").pack(pady=5)
    ttk.Label(info_frame, text="© 2025 FIFA Legacy Project. All Rights Reserved.", justify="center").pack(pady=5)
    
    # Frame for the author line
    author_frame = ttk.Frame(info_frame)
    author_frame.pack(pady=5)
    
    # Combine text with bold names in the same line
    ttk.Label(author_frame, text="Designed & Developed by ", justify="center").pack(side="left")
    bold_font = ("TkDefaultFont", 9, "bold")
    ttk.Label(author_frame, text="Emran_Ahm3d & Dmitri.", font=bold_font, justify="center").pack(side="left")

    # Center the window relative to the main window
    info_window.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() - info_window.winfo_width()) // 2
    y = root.winfo_y() + (root.winfo_height() - info_window.winfo_height()) // 2
    info_window.geometry(f"+{x}+{y}")

# Create GUI window
root = tk.Tk()
root.title("FIFA Birthdate Converter")
root.geometry("500x300")
root.resizable(False, False)  # Make window non-resizable

# Months list
months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

# Date to FIFA section
date_frame = ttk.LabelFrame(root, text="Convert Gregorian Date to FIFA Date")
date_frame.pack(padx=10, pady=5, fill="x")

input_frame = ttk.Frame(date_frame)
input_frame.pack(padx=5, pady=5)

ttk.Label(input_frame, text="Day:").pack(side="left", padx=2)
day_entry = ttk.Entry(input_frame, width=5)
day_entry.pack(side="left", padx=2)
day_entry.insert(0, "01")

ttk.Label(input_frame, text="Month:").pack(side="left", padx=2)
month_combo = ttk.Combobox(input_frame, values=months, state="readonly", width=10)
month_combo.pack(side="left", padx=2)
month_combo.set("January")

ttk.Label(input_frame, text="Year:").pack(side="left", padx=2)
year_entry = ttk.Entry(input_frame, width=10)
year_entry.pack(side="left", padx=2)
year_entry.insert(0, "2000")

ttk.Button(date_frame, text="Convert to FIFA", command=date_to_fifa).pack(pady=5)

# Date result area
date_result_frame = ttk.Frame(date_frame)
date_result_frame.pack(pady=5)
date_result_label = ttk.Label(date_result_frame, text="")
date_result_label.pack(side="left", padx=5)

# FIFA to Date section
fifa_frame = ttk.LabelFrame(root, text="Convert FIFA Date to Gregorian Date")
fifa_frame.pack(padx=10, pady=5, fill="x")

ttk.Label(fifa_frame, text="Enter FIFA days:").pack(padx=5, pady=5)
fifa_entry = ttk.Entry(fifa_frame)
fifa_entry.pack(padx=5, pady=5)

ttk.Button(fifa_frame, text="Convert to Date", command=fifa_to_date).pack(pady=5)

# FIFA result area
fifa_result_frame = ttk.Frame(fifa_frame)
fifa_result_frame.pack(pady=5)
fifa_result_label = ttk.Label(fifa_result_frame, text="")
fifa_result_label.pack(side="left", padx=5)

# Info button with (i) icon in bottom-right corner
info_button = ttk.Button(root, text="🛈", command=show_info, width=3)
info_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-8)

# Day validation
def validate_day(P):
    if len(P) == 0:
        return True
    if len(P) > 2:
        return False
    if not P.isdigit():
        return False
    if int(P) > 31:
        return False
    return True

vcmd = (root.register(validate_day), '%P')
day_entry.config(validate="key", validatecommand=vcmd)

root.mainloop()