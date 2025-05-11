import tkinter as tk from tkinter import messagebox import base64 import hmac import hashlib

Secret key used for key generation (keep this safe and private)

SECRET_KEY = b'my_super_secret_key_12345'

Function to generate license key

def generate_license_key(hardware_id): # Create HMAC-SHA256 using the secret key and hardware ID hmac_obj = hmac.new(SECRET_KEY, hardware_id.encode('utf-8'), hashlib.sha256) license_bytes = hmac_obj.digest()

# Encode the license bytes into base64 for readability
license_key = base64.encodebytes(license_bytes).decode('utf-8')
return license_key

GUI application

def create_gui(): def on_generate(): hw_id = entry_hw.get().strip() if not hw_id: messagebox.showerror("Error", "Please enter a hardware ID.") return license_key = generate_license_key(hw_id) text_output.delete("1.0", tk.END) text_output.insert(tk.END, license_key)

# Window
root = tk.Tk()
root.title("Hardware ID Key Generator")
root.geometry("600x400")

# Label
label_hw = tk.Label(root, text="Enter Hardware ID:", font=("Arial", 12))
label_hw.pack(pady=10)

# Entry
entry_hw = tk.Entry(root, width=50, font=("Arial", 12))
entry_hw.pack(pady=5)

# Button
btn_generate = tk.Button(root, text="Generate Key", command=on_generate, font=("Arial", 12))
btn_generate.pack(pady=10)

# Output Text
text_output = tk.Text(root, height=10, width=70, font=("Arial", 10))
text_output.pack(pady=10)

root.mainloop()

Run the GUI

if name == "main": create_gui()

