import tkinter as tk
from tkinter import ttk, messagebox
import math

class ColumnarCipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Columnar Transposition Cipher")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Columnar Transposition Cipher", font=('Helvetica', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Text input
        ttk.Label(input_frame, text="Text:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.text_entry = tk.Text(input_frame, height=5, width=50, wrap=tk.WORD)
        self.text_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Key input
        ttk.Label(input_frame, text="Key:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.key_entry = ttk.Entry(input_frame, width=50)
        self.key_entry.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        self.encrypt_btn = ttk.Button(button_frame, text="Encrypt", command=self.encrypt)
        self.encrypt_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.decrypt_btn = ttk.Button(button_frame, text="Decrypt", command=self.decrypt)
        self.decrypt_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear)
        self.clear_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        # Result frame
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(result_frame, text="Result:").pack(anchor=tk.W, padx=5)
        self.result_text = tk.Text(result_frame, height=8, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, padx=5, pady=5)
        
        # Copy button
        self.copy_btn = ttk.Button(result_frame, text="Copy Result", command=self.copy_result)
        self.copy_btn.pack(pady=5)
    
    def encrypt(self):
        plaintext = self.text_entry.get("1.0", tk.END).strip()
        key = self.key_entry.get().strip()
        
        if not plaintext:
            messagebox.showerror("Error", "Please enter text to encrypt!")
            return
        if not key:
            messagebox.showerror("Error", "Please enter a key!")
            return
        
        try:
            ciphertext = self.columnar_encrypt(plaintext, key)
            self.display_result(ciphertext)
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed: {str(e)}")
    
    def decrypt(self):
        ciphertext = self.text_entry.get("1.0", tk.END).strip()
        key = self.key_entry.get().strip()
        
        if not ciphertext:
            messagebox.showerror("Error", "Please enter text to decrypt!")
            return
        if not key:
            messagebox.showerror("Error", "Please enter a key!")
            return
        
        try:
            plaintext = self.columnar_decrypt(ciphertext, key)
            self.display_result(plaintext)
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")
    
    def columnar_encrypt(self, plaintext, key):
        """Encrypts plaintext using columnar transposition cipher with the given key."""
        # Remove spaces and convert to uppercase
        plaintext = plaintext.replace(" ", "").upper()
        key = key.upper()
        
        # Determine number of columns and rows needed
        key_len = len(key)
        text_len = len(plaintext)
        num_rows = math.ceil(text_len / key_len)
        
        # Pad the plaintext if needed with 'X' to fill the grid
        pad_len = (key_len - (text_len % key_len)) % key_len
        plaintext += 'X' * pad_len
        
        # Create the grid
        grid = []
        for i in range(num_rows):
            start = i * key_len
            end = start + key_len
            grid.append(list(plaintext[start:end]))
        
        # Get the order of columns based on the key
        key_order = sorted([(char, i) for i, char in enumerate(key)])
        column_order = [i for (char, i) in key_order]
        
        # Read columns in order and build ciphertext
        ciphertext = []
        for col in column_order:
            for row in range(num_rows):
                ciphertext.append(grid[row][col])
        
        return ''.join(ciphertext)
    
    def columnar_decrypt(self, ciphertext, key):
        """Decrypts ciphertext that was encrypted with columnar transposition using the given key."""
        ciphertext = ciphertext.replace(" ", "").upper()
        key = key.upper()
        
        key_len = len(key)
        text_len = len(ciphertext)
        num_rows = math.ceil(text_len / key_len)
        
        # Get the order of columns based on the key
        key_order = sorted([(char, i) for i, char in enumerate(key)])
        column_order = [i for (char, i) in key_order]
        
        # Determine the original column order
        original_order = [0] * key_len
        for new_pos, (char, old_pos) in enumerate(key_order):
            original_order[old_pos] = new_pos
        
        # Calculate how many full columns we have
        full_cols = text_len % key_len
        if full_cols == 0:
            full_cols = key_len
        
        # Create empty grid
        grid = [[None for _ in range(key_len)] for _ in range(num_rows)]
        
        # Fill the grid column by column
        current_pos = 0
        for new_col in range(key_len):
            old_col = original_order[new_col]
            
            # Determine how many characters to take for this column
            col_length = num_rows if (old_col < full_cols) else (num_rows - 1)
            
            # Fill the column
            for row in range(col_length):
                if current_pos < text_len:
                    grid[row][old_col] = ciphertext[current_pos]
                    current_pos += 1
        
        # Read the grid row by row to get plaintext
        plaintext = []
        for row in range(num_rows):
            for col in range(key_len):
                if grid[row][col] is not None:
                    plaintext.append(grid[row][col])
        
        return ''.join(plaintext)
    
    def display_result(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        self.result_text.config(state=tk.DISABLED)
    
    def copy_result(self):
        result = self.result_text.get("1.0", tk.END).strip()
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            messagebox.showinfo("Success", "Result copied to clipboard!")
        else:
            messagebox.showerror("Error", "No result to copy!")
    
    def clear(self):
        self.text_entry.delete("1.0", tk.END)
        self.key_entry.delete(0, tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColumnarCipherApp(root)
    root.mainloop()