# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tkinter as tk 


from tkinter import filedialog, messagebox
import pandas as pd


def clear_entry(event, entry, default_text):
    if entry.get() == default_text: # or entry.get() == default_textA:
        entry.delete(0, tk.END)
        entry.config(fg="black", font=("Times New Roman", 10))

def restore_entry(event, entry, default_text):
    if entry.get() == "":
        entry.insert(0, default_text)
        entry.config(fg="grey", font=("Times New Roman", 10, "italic"))


def browse_file():
    # Open a file dialog and allow the user to select a file
    file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
    if file_path:
        # Display the selected file path in the label
        calib_input_filepath.set(f"{file_path}")

def generate_files():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if not file_path:
        return

    try:
        df = pd.read_excel(file_path)
        if df.shape[1] != 2:
            messagebox.showerror("Error", "The Excel file must have exactly 2 columns.")
            return

        c_content = ""
        h_content = ""

        for index, row in df.iterrows():
            c_content += f"// Row {index}\n"
            c_content += f"{row[0]} = {row[1]};\n"

            h_content += f"// Row {index}\n"
            h_content += f"extern int {row[0]};\n"

        with open("output.c", "w") as c_file:
            c_file.write(c_content)

        with open("output.h", "w") as h_file:
            h_file.write(h_content)

        messagebox.showinfo("Success", "Files generated successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


app = tk.Tk()
app.title("DCU Calibrator v1.0")
app.geometry("800x700")
app.iconbitmap("icons/icon.ico")

calib_input_filepath = tk.StringVar()
calib_VCC_PN = tk.StringVar()

default_textA = "Select input file"
default_textB = "Enter SW version no:"
calib_input_filepath.set(default_textA)
calib_VCC_PN.set(default_textB)

#Frame-1
frame1 = tk.Frame(app)
frame1.grid(row=0, column=0, padx=0, pady=10, sticky="w")


label1 = tk.Label(frame1, text="Software Calibration File * :")
label1.pack(side=tk.LEFT, padx = 10, pady = 5)

field1 = tk.Entry(frame1, textvariable=calib_input_filepath , width=80, font=("Times New Roman", 10, "italic"), fg="grey")
field1.pack(side=tk.LEFT, padx=1)
field1.bind("<FocusIn>", lambda event: clear_entry(event, field1, default_textA))
field1.bind("<FocusOut>", lambda event: restore_entry(event, field1, default_textA))

button1 = tk.Button(frame1, text="Browse", command=browse_file)
button1.pack(side=tk.LEFT, padx=1)

#end

#Frame2
frame2 = tk.Frame(app)
frame2.grid(row=1, column=0, padx=0, pady=1, sticky="w")


label2 = tk.Label(frame2, text="Software Version Number * :")
label2.pack(side=tk.LEFT, padx = 10, pady = 10)

field2 = tk.Entry(frame2, textvariable=calib_VCC_PN , width=20, font=("Times New Roman", 10, "italic"), fg="grey")
field2.pack(side=tk.LEFT, padx=1)
field2.bind("<FocusIn>", lambda event: clear_entry(event, field2, default_textB))
field2.bind("<FocusOut>", lambda event: restore_entry(event, field2, default_textB))

#end

#Frame3
frame3 = tk.Frame(app)
frame3.grid(row=3, column=0, padx=10, pady=20, sticky="w")

button3 = tk.Button(frame3, text="Generate", command=browse_file)
button3.pack(side=tk.BOTTOM, padx=1)

#end

app.mainloop()
