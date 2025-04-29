import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import pyperclip

# Generate key (for simplicity, stored internally – in production this should be secured)
# Only regenerate this once; the same key is needed for both encryption and decryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_text():
    text = input_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "Please enter text to encrypt.")
        return
    encrypted = cipher_suite.encrypt(text.encode())
    encrypted_text.delete("1.0", tk.END)
    encrypted_text.insert(tk.END, encrypted.decode())

def decrypt_text():
    text = encrypted_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "Please enter encrypted text to decrypt.")
        return
    try:
        decrypted = cipher_suite.decrypt(text.encode())
        decrypted_text.delete("1.0", tk.END)
        decrypted_text.insert(tk.END, decrypted.decode())
    except Exception as e:
        messagebox.showerror("Error", "Decryption failed. Invalid encrypted data.")

def copy_encrypted():
    pyperclip.copy(encrypted_text.get("1.0", tk.END).strip())
    messagebox.showinfo("Copied", "Encrypted text copied to clipboard.")

def copy_decrypted():
    pyperclip.copy(decrypted_text.get("1.0", tk.END).strip())
    messagebox.showinfo("Copied", "Decrypted text copied to clipboard.")

def clear_fields():
    input_text.delete("1.0", tk.END)
    encrypted_text.delete("1.0", tk.END)
    decrypted_text.delete("1.0", tk.END)

# GUI setup
root = tk.Tk()
root.title("🔐 Secure Text Encryptor & Decryptor")
root.geometry("600x600")
root.config(bg="#2c3e50")

# Style configuration
style = {
    "bg": "#ecf0f1",
    "fg": "#2c3e50",
    "font": ("Helvetica", 12),
    "relief": "groove",
    "bd": 2,
    "padx": 10,
    "pady": 10
}

tk.Label(root, text="Enter Text to Encrypt", bg="#2c3e50", fg="white", font=("Arial", 14, "bold")).pack(pady=(10, 0))
input_text = tk.Text(root, height=5, **style)
input_text.pack(fill=tk.X, padx=20)

tk.Button(root, text="🔒 Encrypt", command=encrypt_text, bg="#3498db", fg="white", font=("Arial", 12, "bold")).pack(pady=5)

tk.Label(root, text="Encrypted Text", bg="#2c3e50", fg="white", font=("Arial", 14, "bold")).pack()
encrypted_text = tk.Text(root, height=5, **style)
encrypted_text.pack(fill=tk.X, padx=20)

tk.Button(root, text="📋 Copy Encrypted", command=copy_encrypted, bg="#1abc9c", fg="white", font=("Arial", 12)).pack(pady=5)

tk.Button(root, text="🔓 Decrypt", command=decrypt_text, bg="#e67e22", fg="white", font=("Arial", 12, "bold")).pack(pady=5)

tk.Label(root, text="Decrypted Text", bg="#2c3e50", fg="white", font=("Arial", 14, "bold")).pack()
decrypted_text = tk.Text(root, height=5, **style)
decrypted_text.pack(fill=tk.X, padx=20)

tk.Button(root, text="📋 Copy Decrypted", command=copy_decrypted, bg="#9b59b6", fg="white", font=("Arial", 12)).pack(pady=5)

tk.Button(root, text="🧹 Clear All", command=clear_fields, bg="#e74c3c", fg="white", font=("Arial", 12)).pack(pady=(10, 20))

root.mainloop()
