import os
import time
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import logging

try:
    from tkcalendar import DateEntry
except ImportError as e:
    print(f"Error: tkcalendar not installed. Please run 'pip install tkcalendar'. {e}")
    exit(1)

# Set up logging
# Near the top of the script, replace the logging.basicConfig line with:
logging.basicConfig(
    filename='script.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, item_path, folder_path):
        super().__init__(parent)
        try:
            logging.debug(f"Initializing dialog for {item_path}")
            relative_path = os.path.relpath(item_path, folder_path)
            self.title(f"Rename: {relative_path}")
            self.resizable(False, False)
            self.attributes('-topmost', True)
            self.geometry("800x800")
            self.overrideredirect(True)

            self.result = None

            main_frame = tk.Frame(self)
            main_frame.pack(expand=True, padx=30, pady=30)
            main_frame.columnconfigure(0, weight=1)

            bold_font = ("TkDefaultFont", 12, "bold")

            tk.Label(main_frame, text=f"Renaming: {relative_path}", font=bold_font).grid(row=0, column=0, pady=10, sticky="ew")

            tk.Label(main_frame, text="Select date:", font=bold_font).grid(row=1, column=0, pady=10, sticky="ew")
            self.date_entry = DateEntry(main_frame, date_pattern='dd/mm/yy', font=("TkDefaultFont", 12))
            self.date_entry.grid(row=2, column=0, pady=10, sticky="ew")

            # Main Name Section
            tk.Label(main_frame, text="Select Main Name:", font=bold_font).grid(row=3, column=0, pady=10, sticky="ew")
            self.main_name_var = tk.StringVar()
            self.main_name_combobox = ttk.Combobox(main_frame, textvariable=self.main_name_var, font=("TkDefaultFont", 12), state="readonly")
            self.main_name_combobox['values'] = ("MTW", "BVEN", "CLDJ", "NAGAD", "JSDF", "FFDJ")
            self.main_name_combobox.set("MTW")  # Default selection
            self.main_name_combobox.grid(row=4, column=0, pady=10, sticky="ew")

            # Custom Name Checkbox and Entry
            self.use_custom_name = tk.BooleanVar(value=False)
            self.custom_name_check = tk.Checkbutton(
                main_frame,
                text="Use Custom Name",
                variable=self.use_custom_name,
                font=("TkDefaultFont", 12),
                command=self.toggle_custom_name
            )
            self.custom_name_check.grid(row=5, column=0, pady=5, sticky="w")

            self.custom_name_entry = tk.Entry(main_frame, font=("TkDefaultFont", 12), state="disabled")
            self.custom_name_entry.grid(row=6, column=0, pady=10, sticky="ew")

            tk.Label(main_frame, text="Enter Sub Name (optional):", font=bold_font).grid(row=7, column=0, pady=10, sticky="ew")
            self.sub_name_entry = tk.Entry(main_frame, font=("TkDefaultFont", 12))
            self.sub_name_entry.grid(row=8, column=0, pady=10, sticky="ew")

            tk.Label(main_frame, text="Enter Child Name (optional):", font=bold_font).grid(row=9, column=0, pady=10, sticky="ew")
            self.child_name_entry = tk.Entry(main_frame, font=("TkDefaultFont", 12))
            self.child_name_entry.grid(row=10, column=0, pady=10, sticky="ew")

            # Button frame for Submit and Skip
            button_frame = tk.Frame(main_frame)
            button_frame.grid(row=11, column=0, pady=20, sticky="ew")
            button_frame.columnconfigure(0, weight=1)
            button_frame.columnconfigure(1, weight=1)

            ttk.Button(button_frame, text="Submit", command=self.validate_and_submit).grid(row=0, column=0, padx=10, sticky="ew")
            ttk.Button(button_frame, text="Skip", command=self.skip).grid(row=0, column=1, padx=10, sticky="ew")

            self.bind('<Return>', lambda event: self.validate_and_submit())

            # Center the dialog on screen
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            self.geometry(f'{width}x{height}+{x}+{y}')
            logging.debug(f"Dialog initialized successfully for {item_path}")
        except Exception as e:
            logging.error(f"Error initializing dialog for {item_path}: {e}")
            self.destroy()
            raise

    def toggle_custom_name(self):
        """Enable/disable custom name entry based on checkbox state."""
        if self.use_custom_name.get():
            self.custom_name_entry.config(state="normal")
            self.main_name_combobox.config(state="disabled")
        else:
            self.custom_name_entry.config(state="disabled")
            self.main_name_combobox.config(state="readonly")

    def validate_and_submit(self):
        try:
            raw_date = self.date_entry.get().strip()
            parsed_date = datetime.strptime(raw_date, '%d/%m/%y')
            date_input = parsed_date.strftime('%y%m%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use calendar dropdown.", parent=self)
            return

        if self.use_custom_name.get():
            main_name_input = self.custom_name_entry.get().strip()
        else:
            main_name_input = self.main_name_var.get().strip()

        if not date_input or not main_name_input:
            messagebox.showwarning("Warning", "Date and Main Name are required.", parent=self)
            return

        self.result = {
            'date': date_input,
            'main_name': main_name_input,
            'sub_name': self.sub_name_entry.get().strip(),
            'child_name': self.child_name_entry.get().strip()
        }
        self.destroy()

    def skip(self):
        logging.debug("Skip button clicked")
        self.result = None
        self.destroy()

def get_directory_snapshot(folder_path):
    try:
        snapshot = set()
        for root, dirs, files in os.walk(folder_path):
            for name in dirs + files:
                full_path = os.path.join(root, name)
                snapshot.add(full_path)
        return snapshot
    except (OSError, PermissionError) as e:
        logging.error(f"Error scanning {folder_path}: {e}")
        return set()

def prompt_and_rename(path, processed_items, folder_path):
    logging.debug(f"Prompting rename for: {path}")
    root = tk.Tk()
    root.withdraw()

    try:
        dialog = CustomDialog(root, path, folder_path)
        root.wait_window(dialog)

        if not dialog.result:
            logging.debug(f"Skipped or cancelled for: {path}")
            messagebox.showinfo("Skipped", f"Skipped renaming: {os.path.basename(path)}")
            processed_items.add(path)
            return path

        date_input = dialog.result['date']
        main_name_input = dialog.result['main_name']
        sub_name_input = dialog.result['sub_name']
        child_name_input = dialog.result['child_name']

        new_name_parts = [date_input, main_name_input]
        if sub_name_input:
            new_name_parts.append(sub_name_input)
        if child_name_input:
            new_name_parts.append(child_name_input)
        new_name = "_".join(new_name_parts)
        file_ext = os.path.splitext(path)[1] if os.path.isfile(path) else ""
        new_path = os.path.join(os.path.dirname(path), new_name + file_ext)

        try:
            os.rename(path, new_path)
            logging.debug(f"Renamed {path} to {new_path}")
            messagebox.showinfo("Success", f"Renamed to: {new_name + file_ext}")
            processed_items.add(new_path)
            return new_path
        except (OSError, PermissionError) as e:
            logging.error(f"Error renaming {path}: {e}")
            messagebox.showerror("Error", f"Could not rename: {e}")
            return path
    except Exception as e:
        logging.error(f"Unexpected error for {path}: {e}")
        messagebox.showerror("Error", f"Unexpected error: {e}")
        return path
    finally:
        root.destroy()

def process_item_depth_first(item, processed_items, folder_path):
    """Process a single item (file or folder) and its contents depth-first."""
    if item.endswith('.tmp') or os.path.basename(item).lower() in ['desktop.ini', 'thumbs.db']:
        logging.debug(f"Skipping system/temp file: {item}")
        processed_items.add(item)
        return item

    new_path = prompt_and_rename(item, processed_items, folder_path)

    if os.path.isdir(new_path):
        try:
            items = []
            for root, dirs, files in os.walk(new_path, topdown=True):
                for name in dirs + files:
                    items.append(os.path.join(root, name))
                break

            items.sort(key=lambda x: (not os.path.isdir(x), x.lower()))

            for sub_item in items:
                process_item_depth_first(sub_item, processed_items, folder_path)
        except (OSError, PermissionError) as e:
            logging.error(f"Error processing contents of {new_path}: {e}")

    return new_path

def start_monitoring(folder_path):
    try:
        if not os.path.exists(folder_path):
            logging.error(f"Folder {folder_path} does not exist or is inaccessible.")
            return
        if not os.access(folder_path, os.R_OK | os.W_OK):
            logging.error(f"No read/write permissions for {folder_path}")
            return
    except (OSError, PermissionError) as e:
        logging.error(f"Error accessing {folder_path}: {e}")
        return

    logging.info(f"Monitoring Tresorit Drive: {folder_path} and all subfolders (using polling). Press Ctrl+C to stop.")
    previous_snapshot = get_directory_snapshot(folder_path)
    processed_items = set()

    try:
        while True:
            time.sleep(10)
            current_snapshot = get_directory_snapshot(folder_path)
            new_items = current_snapshot - previous_snapshot - processed_items

            new_items = [
                item for item in new_items
                if not item.endswith('.tmp') and
                os.path.basename(item).lower() not in ['desktop.ini', 'thumbs.db']
            ]

            new_items.sort(key=lambda x: (not os.path.isdir(x), x.lower()))

            for item in new_items:
                try:
                    if os.path.exists(item):
                        logging.debug(f"Detected new item: {item}")
                        process_item_depth_first(item, processed_items, folder_path)
                        processed_items.add(item)
                except (OSError, PermissionError) as e:
                    logging.error(f"Error processing {item}: {e}")

            previous_snapshot = current_snapshot
    except KeyboardInterrupt:
        logging.info("Monitoring stopped.")
    except Exception as e:
        logging.error(f"Unexpected error in monitoring loop: {e}")

def main():
    watch_folder = r"T:\dhanesh"
    try:
        logging.debug("Starting script")
        start_monitoring(watch_folder)
    except Exception as e:
        logging.error(f"Script crashed: {e}")
    finally:
        logging.debug("Script terminated")

if __name__ == "__main__":
    main()