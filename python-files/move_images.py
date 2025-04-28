import os
import shutil
from tkinter import filedialog
import tkinter as tk

def get_folder_path(title="Select folder"):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_selected = filedialog.askdirectory(title=title)
    return folder_selected

def move_image_files(source_folder, output_folder):
    if not os.path.exists(source_folder):
        print(f"Source folder does not exist: {source_folder}")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    # Loop through all subfolders and files in the source folder
    for root_dir, _, files in os.walk(source_folder):
        for filename in files:
            # Check if file is an image
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
                file_path = os.path.join(root_dir, filename)
                # Move file to the output folder
                shutil.move(file_path, output_folder)
                print(f"Moved {filename} to {output_folder}")

def main():
    print("Select the Source Folder:")
    source_folder = get_folder_path("Select the Source Folder")

    print("Select the Output Folder:")
    output_folder = get_folder_path("Select the Output Folder")

    move_image_files(source_folder, output_folder)
    print("All image files moved successfully!")

if __name__ == "__main__":
    main()
