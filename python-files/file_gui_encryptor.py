import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet
import os

def generate_key():
    return Fernet.generate_key()

def save_key(key):
    with open("secret.key", "wb") as f:
        f.write(key)

def load_key():
    if os.path.exists("secret.key"):
        with open("secret.key", "rb") as f:
            return f.read()
    else:
        key = generate_key()
        save_key(key)
        return key

def encrypt_file(path):
    try:
        key = load_key()
        fernet = Fernet(key)
        with open(path, "rb") as file:
            data = file.read()
        encrypted = fernet.encrypt(data)
        with open(path + ".enc", "wb") as file:
            file.write(encrypted)
        messagebox.showinfo("Success", f"Encrypted to: {path}.enc")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def decrypt_file(path):
    try:
        key = load_key()
        fernet = Fernet(key)
        with open(path, "rb") as file:
            data = file.read()
        decrypted = fernet.decrypt(data)
        output_path = path.replace(".enc", ".dec")
        with open(output_path, "wb") as file:
            file.write(decrypted)
        messagebox.showinfo("Success", f"Decrypted to: {output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def browse_file():
    filename = filedialog.askopenfilename()
    file_path.set(filename)

def run_encrypt():
    if file_path.get():
        encrypt_file(file_path.get())
    else:
        messagebox.showwarning("Select a file", "Please choose a file first.")

def run_decrypt():
    if file_path.get():
        decrypt_file(file_path.get())
    else:
        messagebox.showwarning("Select a file", "Please choose a file first.")

# GUI Setup
app = tk.Tk()
app.title("File Encryptor & Decryptor")
app.geometry("400x200")
file_path = tk.StringVar()

tk.Label(app, text="Select a file:").pack(pady=10)
tk.Entry(app, textvariable=file_path, width=40).pack()
tk.Button(app, text="Browse", command=browse_file).pack(pady=5)

tk.Button(app, text="Encrypt File", command=run_encrypt, bg="#4CAF50", fg="white").pack(pady=5)
tk.Button(app, text="Decrypt File", command=run_decrypt, bg="#2196F3", fg="white").pack(pady=5)

app.mainloop()
