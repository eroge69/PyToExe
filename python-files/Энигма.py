import string
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
class Rotor:
    def __init__(self, wiring, notch):
        self.left = string.ascii_uppercase
        self.right = wiring
        self.notch = notch
    def forward(self, signal):
        letter = self.right[signal]
        return self.left.index(letter)
    def backward(self, signal):
        letter = self.left[signal]
        return self.right.index(letter)
    def rotate(self, n=1, forward=True):
        for _ in range(n):
            if forward:
                self.left = self.left[1:] + self.left[0]
                self.right = self.right[1:] + self.right[0]
            else:
                self.left = self.left[-1] + self.left[:-1]
                self.right = self.right[-1] + self.right[:-1]
    def rotate_to_letter(self, letter):
        n = string.ascii_uppercase.index(letter)
        current_pos = string.ascii_uppercase.index(self.left[0])
        rotations = (n - current_pos) % 26
        self.rotate(rotations)
class Reflector:
    def __init__(self, wiring):
        self.left = string.ascii_uppercase
        self.right = wiring
    def reflect(self, signal):
        letter = self.right[signal]
        return self.left.index(letter)
class EnigmaMachine:
    def __init__(self, rotors, reflector, rotor_positions):
        self.rotors = rotors
        self.reflector = reflector
        for i, pos in enumerate(rotor_positions):
            self.rotors[i].rotate_to_letter(pos)
    def encrypt_letter(self, letter):
        if letter not in string.ascii_uppercase:
            return letter
        self.rotors[0].rotate()
        for i in range(1, len(self.rotors)):
            if self.rotors[i-1].left[0] == self.rotors[i-1].notch:
                self.rotors[i].rotate()
        signal = string.ascii_uppercase.index(letter)
        for rotor in reversed(self.rotors):
            signal = rotor.forward(signal)
        signal = self.reflector.reflect(signal)
        for rotor in self.rotors:
            signal = rotor.backward(signal)
        return string.ascii_uppercase[signal]
    def encrypt(self, text):
        encrypted_text = []
        for letter in text.upper():
            encrypted_text.append(self.encrypt_letter(letter))
        return ''.join(encrypted_text)
ROTOR_I = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
ROTOR_II = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
ROTOR_III = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
ROTOR_NOTCH_I = "Q"
ROTOR_NOTCH_II = "E"
ROTOR_NOTCH_III = "V"
REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
class EnigmaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Энигма-шифратор")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.rotor1 = Rotor(ROTOR_I, ROTOR_NOTCH_I)
        self.rotor2 = Rotor(ROTOR_II, ROTOR_NOTCH_II)
        self.rotor3 = Rotor(ROTOR_III, ROTOR_NOTCH_III)
        self.reflector = Reflector(REFLECTOR_B)
        self.enigma = None
        self.create_widgets()
    def create_widgets(self):
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('TButton', font=('Arial', 10))
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки роторов", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(settings_frame, text="Ротор 1:").grid(row=0, column=0, padx=5)
        self.rotor1_pos = ttk.Combobox(settings_frame, 
                                     values=list(string.ascii_uppercase),
                                     width=3,
                                     font=('Arial', 12))
        self.rotor1_pos.grid(row=0, column=1)
        self.rotor1_pos.set("A")
        ttk.Label(settings_frame, text="Ротор 2:").grid(row=0, column=2, padx=5)
        self.rotor2_pos = ttk.Combobox(settings_frame, 
                                     values=list(string.ascii_uppercase),
                                     width=3,
                                     font=('Arial', 12))
        self.rotor2_pos.grid(row=0, column=3)
        self.rotor2_pos.set("A")
        ttk.Label(settings_frame, text="Ротор 3:").grid(row=0, column=4, padx=5)
        self.rotor3_pos = ttk.Combobox(settings_frame, 
                                     values=list(string.ascii_uppercase),
                                     width=3,
                                     font=('Arial', 12))
        self.rotor3_pos.grid(row=0, column=5)
        self.rotor3_pos.set("A")
        ttk.Button(settings_frame, 
                  text="Применить настройки", 
                  command=self.apply_settings).grid(row=0, column=6, padx=10)
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        input_frame = ttk.LabelFrame(text_frame, text="Исходный текст", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.input_text = scrolledtext.ScrolledText(input_frame, 
                                                  wrap=tk.WORD, 
                                                  font=('Arial', 12),
                                                  height=10)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        button_frame = ttk.Frame(text_frame)
        button_frame.pack(fill=tk.Y, expand=False, side=tk.LEFT, padx=5)
        ttk.Button(button_frame, 
                  text="Зашифровать →", 
                  command=self.encrypt_text,
                  width=15).pack(pady=5)
        ttk.Button(button_frame, 
                  text="← Расшифровать", 
                  command=self.decrypt_text,
                  width=15).pack(pady=5)
        ttk.Button(button_frame, 
                  text="Очистить", 
                  command=self.clear_text,
                  width=15).pack(pady=5)
        output_frame = ttk.LabelFrame(text_frame, text="Результат", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.output_text = scrolledtext.ScrolledText(output_frame, 
                                                   wrap=tk.WORD, 
                                                   font=('Arial', 12),
                                                   height=10,
                                                   state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)
    def apply_settings(self):
        try:
            pos1 = self.rotor1_pos.get().upper()
            pos2 = self.rotor2_pos.get().upper()
            pos3 = self.rotor3_pos.get().upper()
            if not (pos1 in string.ascii_uppercase and 
                   pos2 in string.ascii_uppercase and 
                   pos3 in string.ascii_uppercase):
                raise ValueError("Позиции роторов должны быть буквами A-Z")
            self.enigma = EnigmaMachine(
                [self.rotor1, self.rotor2, self.rotor3],
                self.reflector,
                [pos1, pos2, pos3]
            )
            messagebox.showinfo("Настройки", "Настройки роторов успешно применены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить настройки:\n{str(e)}")
    def encrypt_text(self):
        if not self.enigma:
            messagebox.showerror("Ошибка", "Сначала установите настройки роторов!")
            return
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для шифрования")
            return
        encrypted = self.enigma.encrypt(text)
        self.show_result(encrypted)
    def decrypt_text(self):
        if not self.enigma:
            messagebox.showerror("Ошибка", "Сначала установите настройки роторов!")
            return
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст для расшифровки")
            return
        self.rotor1.rotate_to_letter(self.rotor1_pos.get().upper())
        self.rotor2.rotate_to_letter(self.rotor2_pos.get().upper())
        self.rotor3.rotate_to_letter(self.rotor3_pos.get().upper())
        decrypted = self.enigma.encrypt(text) 
        self.show_result(decrypted)
    def show_result(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)
        self.output_text.config(state=tk.DISABLED)
    def clear_text(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
if __name__ == "__main__":
    root = tk.Tk()
    app = EnigmaApp(root)
    root.mainloop()