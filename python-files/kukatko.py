"""Main module with GUI and button handlers"""

import json

import customtkinter as ctk
from tkinter import messagebox




current_theme = "System"
ctk.set_appearance_mode(current_theme)
ctk.set_default_color_theme("blue")


def show_output(result):
    output_window = ctk.CTkToplevel()
    output_window.title("Function Output")
    output_window.geometry("300x150")

    label = ctk.CTkLabel(output_window, text=result, font=("Helvetica", 16))
    label.pack(expand=True, pady=30, fill="both")


def function_one():
    show_output("Function One Output")


def function_two():
    show_output("Function Two Output")



def save_credentials(hostname, username, password, window):
    credentials = {
        "hostname": hostname.get(),
        "username": username.get(),
        "password": password.get()
    }
    with open("db_credentials.json", "w") as f:
        json.dump(credentials, f)

    messagebox.showinfo("Saved", "Credentials saved successfully.")
    window.destroy()


def open_credentials_window():
    cred_window = ctk.CTkToplevel()
    cred_window.title("Database Credentials")
    cred_window.geometry("350x300")

    frame = ctk.CTkFrame(cred_window)
    frame.pack(expand=True, fill='both', padx=20, pady=20)

    frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
    frame.grid_columnconfigure((0, 1), weight=1)

    ctk.CTkLabel(frame, text="Hostname").grid(row=0, column=0, padx=10, pady=10, sticky='w')
    hostname_entry = ctk.CTkEntry(frame)
    hostname_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

    ctk.CTkLabel(frame, text="Username").grid(row=1, column=0, padx=10, pady=10, sticky='w')
    username_entry = ctk.CTkEntry(frame)
    username_entry.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

    ctk.CTkLabel(frame, text="Password").grid(row=2, column=0, padx=10, pady=10, sticky='w')
    password_entry = ctk.CTkEntry(frame, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

    save_button = ctk.CTkButton(frame, text="Save",
        command=lambda: save_credentials(hostname_entry, username_entry, password_entry, cred_window)
    )
    save_button.grid(row=3, column=0, columnspan=2, pady=20)


def toggle_theme():
    global current_theme
    if current_theme == "Dark":
        ctk.set_appearance_mode("Light")
        theme_toggle_button.configure(text="Switch to Dark Mode")
        current_theme = "Light"
    else:
        ctk.set_appearance_mode("Dark")
        theme_toggle_button.configure(text="Switch to Light Mode")
        current_theme = "Dark"


root = ctk.CTk()
root.title("Milsoft - Kukátko")
root.geometry("500x450")

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

main_frame = ctk.CTkFrame(root)
main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

main_frame.grid_rowconfigure((1, 2, 3, 4), weight=1)
main_frame.grid_columnconfigure(0, weight=1)

title_label = ctk.CTkLabel(main_frame, text="Milsoft - Kukátko", font=("Helvetica", 20, "bold"))
title_label.grid(row=0, column=0, pady=(10, 20))

btn1 = ctk.CTkButton(main_frame, text="Run Function 1", command=function_one)
btn1.grid(row=1, column=0, pady=10, sticky="ew")

btn2 = ctk.CTkButton(main_frame, text="Run Function 2", command=function_two)
btn2.grid(row=2, column=0, pady=10, sticky="ew")

cred_btn = ctk.CTkButton(main_frame, text="Database Credentials", command=open_credentials_window)
cred_btn.grid(row=3, column=0, pady=10, sticky="ew")

# Theme toggle button
theme_toggle_button = ctk.CTkButton(main_frame, text="Switch to Dark Mode", command=toggle_theme)
theme_toggle_button.grid(row=4, column=0, pady=(20, 10), sticky="ew")

root.mainloop()
