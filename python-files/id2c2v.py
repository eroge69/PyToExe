import tkinter as tk
from tkinter import filedialog, messagebox
import re

def extract_host_fingerprint(xml_text):
    match = re.search(r"<host_fingerprint.*?</host_fingerprint>", xml_text, re.DOTALL)
    if not match:
        raise ValueError("host_fingerprint block not found in ID file")
    return f"<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<hasp_info>\n  {match.group(0)}\n</hasp_info>\n"

def load_and_process_file():
    id_file_path = filedialog.askopenfilename(
        title="Select ID File",
        filetypes=[("ID files", "*.id"), ("All files", "*.*")]
    )

    if not id_file_path:
        return

    with open(id_file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    try:
        modified_content = extract_host_fingerprint(original_content)
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    c2v_file_path = filedialog.asksaveasfilename(
        title="Save .c2v File As",
        defaultextension=".c2v",
        filetypes=[("C2V files", "*.c2v"), ("All files", "*.*")]
    )

    if not c2v_file_path:
        return

    with open(c2v_file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    messagebox.showinfo("Success", f"C2V file saved to: {c2v_file_path}")

def main():
    root = tk.Tk()
    root.title("ID to C2V Converter")
    root.geometry("300x100")

    button = tk.Button(root, text="Select ID File and Convert", command=load_and_process_file)
    button.pack(pady=30)

    root.mainloop()

if __name__ == "__main__":
    main()
