
import json
import os
from tkinter import Tk, filedialog, messagebox

def convert_cookies(file_path):
    try:
        with open(file_path, "r") as f:
            original_cookies = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read JSON: {e}")
        return

    converted_cookies = []
    for cookie in original_cookies:
        converted_cookies.append({
            "domain": cookie.get("host", "").lstrip("."),
            "name": cookie.get("name", ""),
            "value": cookie.get("value", ""),
            "path": "/",
            "secure": True,
            "httpOnly": False,
            "hostOnly": False,
            "session": False
        })

    output_path = os.path.splitext(file_path)[0] + "_converted.json"
    try:
        with open(output_path, "w") as f:
            json.dump(converted_cookies, f, indent=2)
        messagebox.showinfo("Success", f"Converted file saved as:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write file: {e}")

def main():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select cookies.txt JSON file", filetypes=[("JSON files", "*.txt *.json")])
    if file_path:
        convert_cookies(file_path)

if __name__ == "__main__":
    main()
