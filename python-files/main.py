import os
import secrets
import hashlib
from tkinter import *
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# ----------------- Encryption Logic -----------------

def generate_key():
    parts = [str(secrets.randbelow(10000)).zfill(4) for _ in range(4)]
    key_str = "-".join(parts)
    key_bytes = hashlib.sha256(key_str.encode()).digest()
    return key_str, key_bytes

def encrypt_file(filepath):
    key_str, key = generate_key()
    iv = os.urandom(16)

    with open(filepath, "rb") as f:
        data = f.read()
    pad_len = 16 - (len(data) % 16)
    padded = data + bytes([pad_len]) * pad_len

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    enc = cipher.encryptor().update(padded) + cipher.encryptor().finalize()

    out_path = filepath + ".senc"
    with open(out_path, "wb") as f:
        f.write(iv + enc)

    return out_path, key_str

def decrypt_file(filepath, key_str):
    try:
        key = hashlib.sha256(key_str.encode()).digest()
        with open(filepath, "rb") as f:
            iv = f.read(16)
            enc = f.read()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        dec = cipher.decryptor().update(enc) + cipher.decryptor().finalize()

        pad_len = dec[-1]
        dec = dec[:-pad_len]

        out_path = filepath.replace(".senc", "")
        with open(out_path, "wb") as f:
            f.write(dec)

        return out_path
    except Exception as e:
        return None

# ----------------- GUI -----------------

class FileEncryptorApp:
    def __init__(self, master):
        self.master = master
        master.title("🔐 File Encrypter / Decrypter")

        self.filepath = ""
        
        Label(master, text="Datei auswählen:").pack(pady=5)
        Button(master, text="📂 Durchsuchen", command=self.browse_file).pack()

        self.file_label = Label(master, text="Keine Datei gewählt", fg="gray")
        self.file_label.pack(pady=5)

        self.encrypt_btn = Button(master, text="🔒 Verschlüsseln", command=self.encrypt_action)
        self.encrypt_btn.pack(pady=5)

        self.key_entry = Entry(master, width=25, justify='center')
        self.key_entry.pack(pady=5)
        self.key_entry.insert(0, "####-####-####-####")

        self.decrypt_btn = Button(master, text="🔓 Entschlüsseln", command=self.decrypt_action)
        self.decrypt_btn.pack(pady=5)

        self.status = Label(master, text="", fg="blue")
        self.status.pack(pady=10)

    def browse_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.filepath = path
            self.file_label.config(text=os.path.basename(path), fg="black")
            self.status.config(text="")

    def encrypt_action(self):
        if not self.filepath:
            messagebox.showwarning("Keine Datei", "Bitte wähle eine Datei aus.")
            return
        out_file, key = encrypt_file(self.filepath)
        self.status.config(text=f"Datei verschlüsselt:\n{os.path.basename(out_file)}\nKey: {key}", fg="green")
        self.key_entry.delete(0, END)
        self.key_entry.insert(0, key)

    def decrypt_action(self):
        if not self.filepath:
            messagebox.showwarning("Keine Datei", "Bitte wähle eine verschlüsselte Datei aus.")
            return
        key = self.key_entry.get().strip()
        if not key or len(key) != 19:
            messagebox.showwarning("Ungültiger Schlüssel", "Bitte gib einen gültigen Schlüssel ein.")
            return
        result = decrypt_file(self.filepath, key)
        if result:
            self.status.config(text=f"Datei entschlüsselt:\n{os.path.basename(result)}", fg="green")
        else:
            self.status.config(text="Entschlüsselung fehlgeschlagen! Falscher Schlüssel?", fg="red")

# ----------------- Run App -----------------

if __name__ == "__main__":
    root = Tk()
    root.geometry("400x300")
    root.resizable(False, False)
    app = FileEncryptorApp(root)
    root.mainloop()
