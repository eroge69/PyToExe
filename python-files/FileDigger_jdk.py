# -*- coding: utf-8 -*-
"""
FileDigger_jdk – mass spectrometry file processor with GUI.

This tool allows users to load and transform text-based spectral data
files generated from mass spectrometry experiments on Thermo instruments.
It supports automated renaming, header removal, decimal formatting,
and unit scaling for downstream processing.

Features:
- batch and single-file transformation
- suffix-based file versioning
- tooltip-enhanced tkinter interface
- structured output for data pipelines

Author: Janine-Denise Kopicki (J.D.K.)
Created: April 3, 2025
License: GPLv3
"""
# ─────────────────────────────────────────────────────────────────────────────
# 📦 standard library
import os

# 🪟 Tkinter GUI
import tkinter as tk
from tkinter import Tk, filedialog, Button, Label, Entry, Listbox, Scrollbar
from tkinter import messagebox, Frame, SINGLE, RIGHT, LEFT, BOTH, Y

# ─────────────────────────────────────────────────────────────────────────────
# 🪟 root setup
root = Tk()
root.title("FileDigger_jdk")
root.geometry("600x470")  # set initial size; adjust as needed
# root.state("zoomed")
print("🖼️ GUI initialized")

# ─────────────────────────────────────────────────────────────────────────────
# variables
file_paths = []


# ─────────────────────────────────────────────────────────────────────────────
# functions
def select_files():
    """
    Open a file dialog to select one or more .txt files.

    This function allows the user to browse and select multiple text-based
    mass spectrometry files. Selected file paths are appended to the global
    file list and displayed in the listbox for processing.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global file_paths
    print("📂 opening file dialog to select .txt files...")
    files = filedialog.askopenfilenames(
        title="browse files",
        filetypes=[("Text Files", "*.txt")]
    )
    if files:
        print(f"✅ {len(files)} file(s) selected")
        file_paths.extend(files)
        update_listbox()
    else:
        print("⚠️ no files selected")
        messagebox.showinfo("Info", "No files were selected.")


def update_listbox():
    """
    Refresh the listbox with the current list of selected file paths.

    Clears the listbox widget and repopulates it with the contents of the
    global file list to reflect the current selection state.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    listbox.delete(0, "end")
    for path in file_paths:
        listbox.insert("end", path)
    print(f"📃 listbox updated: {len(file_paths)} file(s) shown")


def remove_selected_file():
    """
    Remove the currently selected file from the list of loaded file paths.

    Deletes the file entry selected in the listbox from the global file list.
    Updates the listbox display to reflect the removal. If no file is selected,
    a warning is shown to the user.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global file_paths
    selected = listbox.curselection()
    if not selected:
        print("⚠️ no file selected for removal")
        messagebox.showwarning("Warning", "No file selected.")
        return
    index = selected[0]
    removed_file = file_paths[index]
    del file_paths[index]
    update_listbox()
    print(f"🗑️ removed file: {removed_file}")
    messagebox.showinfo("Info", "Selected file removed successfully.")


def remove_all_files():
    """
    Remove all loaded files from the current file list.

    Clears the global list of selected file paths and refreshes the listbox
    to reflect an empty state. If the list is already empty, a warning is
    shown to the user.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    global file_paths
    if not file_paths:
        print("⚠️ no files to remove")
        messagebox.showwarning("Warning", "No files to remove.")
        return
    file_paths = []
    update_listbox()
    print("🗑️ all files removed from list")
    messagebox.showinfo("Info", "All files removed successfully.")


def extract_new_filename(file_path, suffix=""):
    """
    Extract a new base filename from the input file.

    Use metadata and optional suffix.
    Return four filenames and the content without the first 8 header lines.
    """
    with open(file_path, "r") as file:
        lines = file.readlines()
    part1 = lines[1].strip().split(".")[0].replace(" ", "_")
    part2 = lines[3].strip().split("Scan #: ")[1].replace(" ", "_")
    if suffix:
        suffix = suffix.replace(" ", "_")
        new_filename = f"{part1}_{part2}_{suffix}.txt"
        new_filename_nohead = f"{part1}_{part2}_{suffix}_nohead.txt"
        new_filename_massign = f"{part1}_{part2}_{suffix}_massign.txt"
        new_filename_masslynx = f"{part1}_{part2}_{suffix}_masslynx.txt"
    else:
        new_filename = f"{part1}_{part2}.txt"
        new_filename_nohead = f"{part1}_{part2}_nohead.txt"
        new_filename_massign = f"{part1}_{part2}_massign.txt"
        new_filename_masslynx = f"{part1}_{part2}_masslynx.txt"
    print(f"🧾 extracted filenames from: {os.path.basename(file_path)}")
    return (
        new_filename,
        new_filename_nohead,
        new_filename_massign,
        new_filename_masslynx,
        lines[8:]
    )


def process_file(file_path, suffix=""):
    """
    Process a single Thermo .TXT file and generate multiple output variants.

    Parses the input file to extract metadata for renaming and generates
    three derivative versions:
    - a no-header file with metadata lines removed,
    - a 'massign' version with decimal points converted to commas,
    - a 'masslynx' version with intensities scaled by a factor of 1000.

    If any of the output files already exist, the user is prompted to confirm
    overwriting. The original file is renamed based on extracted metadata and
    optional user-provided suffix.

    Parameters
    ----------
    file_path : str
        Path to the input .txt file generated by Thermo software.
    suffix : str, optional
        Optional suffix to be added to all generated filenames (default is "").

    Returns
    -------
    None
    """
    try:
        (
            new_filename,
            new_filename_nohead,
            new_filename_massign,
            new_filename_masslynx,
            new_content
        ) = extract_new_filename(file_path, suffix)
        directory = os.path.dirname(file_path)
        # 🧪 check for existing output files
        existing_files = []
        for filename in (new_filename, new_filename_nohead,
                         new_filename_massign, new_filename_masslynx):
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                existing_files.append(path)
        if existing_files:
            files_list = "\n".join(os.path.basename(f) for f in existing_files)
            if not messagebox.askyesno(
                "Overwrite files?",
                f"The following file(s) already exist:\n\n{files_list}\n\n"
                "Do you want to overwrite them?"
            ):
                print("🛑 transformation canceled by user – overwrite denied")
                return
        # rename original file
        new_file_path = os.path.join(directory, new_filename)
        os.rename(file_path, new_file_path)
        print(f"📝 renamed file: {
              os.path.basename(file_path)} → {new_filename}")
        # write _nohead version (removes header generated by Thermo software)
        new_file_nohead_path = os.path.join(directory, new_filename_nohead)
        with open(new_file_nohead_path, "w") as f:
            f.writelines(new_content)
        print(f"📄 created: {new_filename_nohead}")
        # write _massign version (replace . with ,)
        new_content_massign = [line.replace(".", ",") for line in new_content]
        new_file_massign_path = os.path.join(directory, new_filename_massign)
        with open(new_file_massign_path, "w") as f:
            f.writelines(new_content_massign)
        print(f"🧪 created: {new_filename_massign}")
        # write _masslynx version (multiply y-values by 1000)
        new_content_masslynx = []
        for line in new_content:
            if line.strip():
                parts = line.split()
                if len(parts) == 2:
                    try:
                        x = parts[0]
                        y = float(parts[1]) * 1000
                        new_content_masslynx.append(f"{x} {y}\n")
                    except ValueError:
                        new_content_masslynx.append(line)
                else:
                    new_content_masslynx.append(line)
            else:
                new_content_masslynx.append(line)
        new_file_masslynx_path = os.path.join(directory, new_filename_masslynx)
        with open(new_file_masslynx_path, "w") as f:
            f.writelines(new_content_masslynx)
        print(f"🔬 created: {new_filename_masslynx}")
        print("✅ processing complete")
    except Exception as e:
        print(f"❌ error while processing file: {file_path}")
        print(f"   ↪︎ {e}")


def transform_selected_file():
    """
    Process the currently selected file using the specified filename suffix.

    Retrieves the selected file path from the listbox and applies
    the processing pipeline to generate renamed and reformatted output files.
    The suffix entered by the user is appended to all output filenames.
    If no file is selected, a warning is shown.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    selected = listbox.curselection()
    if not selected:
        print("⚠️ no file selected for processing")
        messagebox.showwarning("Warning", "No file selected.")
        return
    file_path = file_paths[selected[0]]
    suffix = suffix_entry.get()
    print(f"🔄 processing selected file: {os.path.basename(file_path)}")
    process_file(file_path, suffix)
    print("✅ selected file processed successfully")
    messagebox.showinfo("Info", "Selected file processed successfully.")


def transform_all_files():
    """
    Process all loaded files using the specified filename suffix.

    Iterates over all file paths currently loaded in the application and
    applies the processing routine to each file. A user-defined suffix is
    appended to all generated output filenames. If no files are loaded,
    the user is notified with a warning message.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    if not file_paths:
        print("⚠️ no files to process")
        messagebox.showwarning("Warning", "No files to process.")
        return
    suffix = suffix_entry.get()
    print(f"🔄 processing all files ({len(file_paths)} total)...")
    for path in file_paths:
        process_file(path, suffix)
    print("✅ all files processed successfully")
    messagebox.showinfo("Info", "All files processed successfully.")


def create_tooltip(widget, text):
    """
    Attach a simple tooltip to a widget that appears on mouse hover.

    Bind events to show a yellow popup with the given text when the mouse
    enters the widget, and hide it again when the mouse leaves.

    Parameters
    ----------
    widget : tkinter.Widget
        The widget to which the tooltip will be attached.
    text : str
        The text content to display in the tooltip.

    Returns
    -------
    None
    """
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw()
    tooltip.overrideredirect(True)
    label = tk.Label(
        tooltip,
        text=text,
        background="yellow",
        relief="solid",
        borderwidth=1,
        font=("TkDefaultFont", 9)
    )
    label.pack()

    def enter(event):
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + 20
        tooltip.geometry(f"+{x}+{y}")
        tooltip.deiconify()
        # print(f"ℹ️ tooltip shown: '{text}'")

    def leave(event):
        tooltip.withdraw()
        # print("ℹ️ tooltip hidden")

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)


def show_about():
    """
    Open the About window with credits, version, license, contact information.

    Display a modal, non-resizable window with project metadata and center it
    on the screen.

    Returns
    -------
    None
    """
    print("ℹ️ opening about window")
    about = tk.Toplevel()
    about.title("About FileDigger_jdk")
    about.resizable(False, False)
    about.grab_set()
    text = (
        "SpecDigger_jdk – native mass spectrometry analysis\n\n"
        "Version: 1.0.0\n"
        "Author: Janine-Denise Kopicki (J.D.K.)\n"
        "Institution: Centre for Structural Systems Biology (CSSB),"
        "University of Lübeck\n"
        "Contact: janine-denise.kopicki@cssb-hamburg.de\n"
        "GitHub: github.com/dubbelstokje/FileDigger-jdk\n"
        "License: GPLv3 License\n\n"
        "© 2025 Janine-Denise Kopicki. All rights reserved."
    )
    tk.Label(about, text=text, justify="left", padx=20, pady=20).pack()
    # center the window on screen
    about.update_idletasks()
    w, h = about.winfo_width(), about.winfo_height()
    x = (about.winfo_screenwidth() // 2) - (w // 2)
    y = (about.winfo_screenheight() // 2) - (h // 2)
    about.geometry(f"{w}x{h}+{x}+{y}")


# ─────────────────────────────────────────────────────────────────────────────
# 🪟 GUI/layout
# left panel
left_frame = Frame(root, width=600)
left_frame.pack(side=LEFT, fill=BOTH, expand=True)

right_frame = Frame(root, width=30)
right_frame.pack(side=RIGHT, fill=BOTH, expand=False)

# listbox and scrollbar
listbox_frame = Frame(left_frame)
listbox_frame.pack(fill=BOTH, expand=True, padx=(10, 0), pady=5)

scrollbar = Scrollbar(listbox_frame)
scrollbar.pack(side=RIGHT, fill=Y)

listbox = Listbox(listbox_frame, selectmode=SINGLE,
                  yscrollcommand=scrollbar.set)
listbox.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=listbox.yview)

create_tooltip(listbox, "list of selected files to be processed")

# ---------- right panel buttons ----------
# open files
Label(right_frame, text="open file(s):").pack(anchor="w", padx=10, pady=5)
btn_open = Button(right_frame, command=select_files,
                  width=20, anchor="center", text="📁")
btn_open.pack(padx=10, pady=5, anchor="center")
create_tooltip(btn_open, "open one or more .txt files for processing")

# remove selected
Label(right_frame, text="remove selected file:").pack(
    anchor="w", padx=10, pady=5)
btn_remove_selected = Button(right_frame, command=remove_selected_file,
                             width=20, anchor="center", text="➖")
btn_remove_selected.pack(padx=10, pady=5, anchor="center")
create_tooltip(btn_remove_selected, "remove the selected file from the list")

# remove all
Label(right_frame, text="remove all files:").pack(anchor="w", padx=10, pady=5)
btn_remove_all = Button(right_frame, command=remove_all_files,
                        width=20, anchor="center", text="➖")
btn_remove_all.pack(padx=10, pady=5, anchor="center")
create_tooltip(btn_remove_all, "remove all files from the list")

# suffix entry
Label(right_frame, text="add suffix (e.g., replicate01):").pack(
    anchor="w", padx=10, pady=5)
suffix_entry = Entry(right_frame, width=23)
suffix_entry.pack(padx=10, pady=5, anchor="center")
create_tooltip(suffix_entry, "optional suffix added to output filenames")

# transform selected
Label(right_frame, text="transform selected file:").pack(
    anchor="w", padx=10, pady=5)
btn_transform_selected = Button(
    right_frame, command=transform_selected_file, width=20, anchor="center",
    text="🔄")
btn_transform_selected.pack(padx=10, pady=5, anchor="center")
create_tooltip(btn_transform_selected, "process only the selected file")

# transform all
Label(right_frame, text="transform all files:").pack(
    anchor="w", padx=10, pady=5)
btn_transform_all = Button(
    right_frame, command=transform_all_files, width=20, anchor="center",
    text="🔄")
btn_transform_all.pack(padx=10, pady=5, anchor="center")
create_tooltip(btn_transform_all, "process all listed files")

# about
Label(right_frame, text="about:").pack(anchor="w", padx=10, pady=5)
btn_about = Button(right_frame, command=show_about,
                   width=20, anchor="center", text="ℹ️")
btn_about.pack(padx=10, pady=5, anchor="center")
create_tooltip(btn_about, "information about FileDigger_jdk and contact")

# ─────────────────────────────────────────────────────────────────────────────
# 🚀 start mainloop
print("🚀 launching application...")
root.mainloop()
