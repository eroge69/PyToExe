"""Module with features"""

import customtkinter as ctk


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
