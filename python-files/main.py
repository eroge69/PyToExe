import os
import time
import sys
import tkinter as tk
import progressbar
from tkinter import filedialog

CHAR_MAP = {
        'a': 'Æ', 'á': 'Œ', 'à': '‰', 'ả': 'Ž', 'ã': 'þ', 'ạ': 'ÿ',
        'A': '⊘', 'B': '©', 'C': '⊚', 'D': '‹', 'E': '¦', 'F': '⊝', 'G': '⊞', 'H': '⊟', 'I': '⊠',
        'J': '⊡', 'K': '⊢', 'L': '⊣', 'M': '⊤', 'N': '⊥', 'O': '⊦',
        'P': '⊧', 'Q': '⊨', 'R': '⊩', 'S': '⊪', 'T': '⊫', 'U': '⊬',
        'V': '⊭', 'W': '⊮', 'X': '⊯', 'Y': '⊰', 'Z': '⊱',
        '0': 'Æ', '1': 'Œ', '2': '‰', '3': 'Ž', '4': 'ã', '5': 'þ',
        '6': '⁁', '7': 'ạ', '8': '$', '9': 'ÿ',
        '.': '⟉'
    }

DECRYPT_MAP = {v: k for k, v in CHAR_MAP.items()}

def decrypt_text(encrypted_text, decrypt_map):
        return ''.join(decrypt_map.get(char, char) for char in encrypted_text)

def decrypt_file(file_path, decrypt_map):
        with open(file_path, 'r', encoding='utf-8') as file:
            encrypted_text = file.read()
        decrypted_text = decrypt_text(encrypted_text, decrypt_map)
        return decrypted_text

def save_decrypted_file(decrypted_text, original_file_path):
        decrypted_file_path = original_file_path.replace('.txt', '_decrypted.txt')
        with open(decrypted_file_path, 'w', encoding='utf-8') as file:
            file.write(decrypted_text)
        return decrypted_file_path

def show_progress():
        bar = progressbar.ProgressBar(maxval=100, widgets=[
        progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()
                ])
        bar.start()
        for i in range(100):
                time.sleep(0.02)
                bar.update(i + 1)
        bar.finish()

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select the file to decrypt", filetypes=[("Text Files", "*.txt")])

if not file_path:
        print("No file selected. Exiting program...")
        sys.exit()

print("Decrypting file...")
try:
        show_progress()
        decrypted_text = decrypt_file(file_path, DECRYPT_MAP)
        decrypted_file_path = save_decrypted_file(decrypted_text, file_path)
        print('Done!')
except Exception as e:
        print(f"An error occurred during decryption: {e}")
