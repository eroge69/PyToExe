import os
import base64
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken
import random
import string

def derive_key(passphrase: str, salt: bytes, iterations: int = 100_000) -> bytes:
    """Derive a Fernet-compatible key from a passphrase and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

def encrypt_file(file_name, passphrase=None):
    try:
        with open(file_name, "rb") as file:
            message = file.read()

        if passphrase is None:
            passphrase = passphrase_entry.get()
        
        #save passphrase to "pass" file
        with open("pass", "a") as pass_file:
            pass_file.write(passphrase + "\n")

        salt = os.urandom(16)
        key = derive_key(passphrase, salt)
        fernet = Fernet(key)
        encrypted_message = fernet.encrypt(message)

        payload = salt + encrypted_message
        enc_payload_b64 = base64.urlsafe_b64encode(payload)

        base_name = os.path.basename(file_name)
        output_filename = f"output-{base_name}"

        with open(output_filename, "wb") as output_file:
            output_file.write(enc_payload_b64)

        messagebox.showinfo("Success", f"File '{file_name}' has been encrypted and saved to '{output_filename}'.")
    except FileNotFoundError:
        messagebox.showerror("Error", f"The file '{file_name}' was not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def decrypt_file(input_file, passphrase=None):
    try:
        with open(input_file, "rb") as f:
            payload = base64.urlsafe_b64decode(f.read())

        salt = payload[:16]
        encrypted_data = payload[16:]

        if passphrase is None:
            passphrase = passphrase_entry.get()

        key = derive_key(passphrase, salt)
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)

        base_name = os.path.basename(input_file)
        if base_name.endswith(".txt"):
            base_name = base_name[:-4]
        output_filename = f"{base_name}_decrypted.txt"

        with open(output_filename, "wb") as f:
            f.write(decrypted_data)

        messagebox.showinfo("Success", f"Decryption successful. File saved as '{output_filename}'.")
    except InvalidToken:
        messagebox.showerror("Error", "Incorrect passphrase or corrupted data.")
    except FileNotFoundError:
        messagebox.showerror("Error", f"Encrypted file '{input_file}' not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def open_file_for_encryption():
    file_path = filedialog.askopenfilename(title="Select File to Encrypt/Decrypt")
    if file_path:
        file_name_entry.delete(0, tk.END)
        file_name_entry.insert(0, file_path)

def on_encrypt():
    file_name = file_name_entry.get()
    passphrase = passphrase_entry.get()
    if not file_name or not passphrase:
        messagebox.showerror("Error", "Please provide both file and passphrase.")
        return
    encrypt_file(file_name, passphrase)

def on_decrypt():
    file_name = file_name_entry.get()
    passphrase = passphrase_entry.get()
    if not file_name or not passphrase:
        messagebox.showerror("Error", "Please provide both file and passphrase.")
        return
    decrypt_file(file_name, passphrase)

def clear():
    passphrase_entry.delete(0, tk.END)
    file_name_entry.delete(0, tk.END)

def generate():
    length = random.randrange(15, 20)  #length of passphrase
    characters = string.ascii_letters + string.digits + string.punctuation
    passphrase = ''.join(random.SystemRandom().choice(characters) for _ in range(length))
    passphrase_entry.delete(0, tk.END)
    passphrase_entry.insert(0, passphrase)

def show_passphrase():
    show = passphrase_entry.cget('show')
    if show == '':
        passphrase_entry.config(show='*')
    else:
        passphrase_entry.config(show='')

root = tk.Tk()
root.title("Encryption/Decryption")
root.configure(bg="black")  #set background early

# Define style variables for consistency
label_bg = "black"
label_fg = "white"
entry_bg = "gray20"
entry_fg = "white"
button_bg = "gray30"
button_fg = "white"

#buttons
tk.Label(root, text="File:", bg=label_bg, fg=label_fg).grid(row=0, column=0, padx=10, pady=10)
file_name_entry = tk.Entry(root, width=40, bg=entry_bg, fg=entry_fg)
file_name_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=open_file_for_encryption, bg=button_bg, fg=button_fg).grid(row=0, column=2, padx=10, pady=10)
tk.Button(root, text="generate", command=generate, bg=button_bg, fg=button_fg).grid(row=1, column=2, padx=10, pady=10)

# Passphrase Section
tk.Label(root, text="Passphrase:", bg=label_bg, fg=label_fg).grid(row=1, column=0, padx=10, pady=10)
passphrase_entry = tk.Entry(root, show="*", width=40, bg=entry_bg, fg=entry_fg)
passphrase_entry.grid(row=1, column=1, padx=10, pady=10)



#buttons for Encrypt/Decrypt
button_frame = tk.Frame(root, bg=label_bg)
button_frame.grid(row=2, column=0, columnspan=3, pady=20)
clear_button = tk.Button(button_frame, text="clear", command=clear, bg=button_bg, fg=button_fg)
encrypt_button = tk.Button(button_frame, text="Encrypt", command=on_encrypt, bg=button_bg, fg=button_fg)
decrypt_button = tk.Button(button_frame, text="Decrypt", command=on_decrypt, bg=button_bg, fg=button_fg)
encrypt_button.pack(side=tk.LEFT, padx=10)
decrypt_button.pack(side=tk.LEFT, padx=10)
clear_button.pack(side=tk.LEFT, padx=10)
showpassphrase = tk.Button(button_frame, text=("show passphrase"), command=show_passphrase,bg=button_bg, fg=button_fg)
showpassphrase.pack(side=tk.LEFT, padx=10)


#made by:
tk.Label(root, text="\nmpampis", bg=label_bg, fg=label_fg).grid(row=3, column=0, padx=10, pady=10)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

root.mainloop()