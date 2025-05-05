import customtkinter as ctk
from tkinter import filedialog
import json

# App window setup
ctk.set_appearance_mode("light")  # Options: "dark" or "light"
ctk.set_default_color_theme("blue")  # You can also try "green" or "dark-blue"

app = ctk.CTk()  # Create main window
app.geometry("500x600")
app.title("My Daily Idea Planner")

# ---------- UI Elements ----------

# Title label
title_label = ctk.CTkLabel(app, text="Write Your Ideas 💡", font=("Arial", 20, "bold"))
title_label.pack(pady=20)

# Input field
input_field = ctk.CTkEntry(app, width=300, placeholder_text="Type your idea, thought, or goal...")
input_field.pack(pady=10)

# Submit button
def add_item():
    item = input_field.get().strip()
    if item:
        display_item(item)
        input_field.delete(0, ctk.END)

add_button = ctk.CTkButton(app, text="+ Add", command=add_item)
add_button.pack(pady=5)

# Frame to display list items
list_frame = ctk.CTkFrame(app, width=400)
list_frame.pack(pady=20, fill="both", expand=True)

# Displayed list storage
item_widgets = []
item_labels = []  # List to store references to item labels

def display_item(text):
    item_row = ctk.CTkFrame(list_frame)
    item_row.pack(fill="x", pady=5, padx=10)

    item_label = ctk.CTkLabel(item_row, text=text, anchor="w")
    item_label.pack(side="left", expand=True, fill="x")

    def delete_item():
        item_row.destroy()
        item_widgets.remove(item_row)
        item_labels.remove(item_label)  # Remove the label from the list when deleted

    def edit_item():
        input_field.delete(0, ctk.END)
        input_field.insert(0, item_label.cget("text"))
        delete_item()

    edit_btn = ctk.CTkButton(item_row, text="✏️", width=40, command=edit_item)
    edit_btn.pack(side="right", padx=5)

    del_btn = ctk.CTkButton(item_row, text="🗑️", width=40, command=delete_item)
    del_btn.pack(side="right", padx=5)

    item_widgets.append(item_row)
    item_labels.append(item_label)  # Add the label to the list

# ---------- Save and Open functionality ----------

def save_to_file():
    # Ask for the file path
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    
    if file_path:
        # Collect all the items (text from the labels)
        items = [label.cget("text") for label in item_labels]
        
        # Save the items as JSON
        with open(file_path, "w") as f:
            json.dump(items, f, indent=4)

def open_from_file():
    # Ask for the file to open
    file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    
    if file_path:
        # Load the items from the selected file
        with open(file_path, "r") as f:
            items = json.load(f)
        
        # Clear existing items
        for item in item_widgets:
            item.destroy()
        item_widgets.clear()
        item_labels.clear()  # Clear the label references as well
        
        # Display the loaded items
        for item in items:
            display_item(item)

# Save and Open buttons
save_button = ctk.CTkButton(app, text="Save", command=save_to_file)
save_button.pack(pady=5)

open_button = ctk.CTkButton(app, text="Open", command=open_from_file)
open_button.pack(pady=5)

# Run app
app.mainloop()
