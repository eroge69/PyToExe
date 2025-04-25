import os
from tkinter import (
    Tk, filedialog, Checkbutton, Button, Label, IntVar,
    StringVar, ttk, Entry
)
from PIL import Image
import threading

def convert_images(input_dir, output_dir, delete_originals):
    image_files = []
    for dirpath, _, filenames in os.walk(input_dir):
        for file in filenames:
            if file.lower().endswith((".webp", ".avif")):
                image_files.append(os.path.join(dirpath, file))

    total = len(image_files)
    progress["maximum"] = total
    progress["value"] = 0

    for idx, filepath in enumerate(image_files):
        try:
            rel_path = os.path.relpath(filepath, input_dir)
            output_path = os.path.join(output_dir, os.path.splitext(rel_path)[0] + ".jpg")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            img = Image.open(filepath).convert("RGB")
            img.save(output_path, "JPEG")
            if delete_originals and os.path.exists(output_path):
                os.remove(filepath)

            status.set(f"Converted: {os.path.basename(filepath)}")
        except Exception as e:
            status.set(f"Failed: {os.path.basename(filepath)} - {e}")

        progress["value"] = idx + 1
        root.update_idletasks()

    status.set("✅ All done!")


def browse_input():
    folder = filedialog.askdirectory()
    if folder:
        input_folder.set(folder)
        status.set("")

def browse_output():
    folder = filedialog.askdirectory()
    if folder:
        output_folder.set(folder)

def start_conversion():
    if not input_folder.get():
        status.set("⚠️ Please select an input folder.")
        return
    if not output_folder.get():
        output_folder.set(input_folder.get())  # Default output = input

    threading.Thread(
        target=convert_images,
        args=(input_folder.get(), output_folder.get(), delete_var.get()),
        daemon=True
    ).start()
    status.set("🔄 Converting...")


# GUI setup
root = Tk()
root.title("WebP/AVIF to JPG Batch Converter")
root.geometry("500x340")
root.resizable(False, False)

input_folder = StringVar()
output_folder = StringVar()
delete_var = IntVar()
status = StringVar()

Label(root, text="1. Select Input Folder:").pack(anchor="w", padx=20, pady=(10, 0))
Entry(root, textvariable=input_folder, width=50).pack(padx=20)
Button(root, text="Browse", command=browse_input).pack(pady=5)

Label(root, text="2. Select Output Folder (optional):").pack(anchor="w", padx=20, pady=(10, 0))
Entry(root, textvariable=output_folder, width=50).pack(padx=20)
Button(root, text="Browse", command=browse_output).pack(pady=5)

Checkbutton(
    root,
    text="Delete original .webp/.avif files after conversion",
    variable=delete_var
).pack(pady=5)

Button(root, text="Start Conversion", command=start_conversion).pack(pady=10)

progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=(5, 5))

Label(root, textvariable=status, fg="blue").pack(pady=5)

# --- Footer ---
footer = Label(
    root,
    text="Made by Muhammad Waqas (Bravewiki) — All rights reserved © 2025",
    fg="gray", font=("Arial", 8)
)
footer.pack(side="bottom", pady=(10, 5))

root.mainloop()
