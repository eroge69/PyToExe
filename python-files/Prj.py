import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

window = tk.Tk()

window.geometry("1291x900")
window.configure(bg="#5DC8CD")
window.title("Кодировщик текста")

Entry1 = tk.Text(window, width=60, height=30, wrap="word")
Entry2 = tk.Text(window, width=60, height=30, wrap="word", state="disabled")  

Entry2.place(x=700, y=40)
Entry1.place(x=100, y=40)


items = ["Русский Язык", "Азбука Морзе", "Двоичный код", "Кирпичный язык"]

combobox1 = ttk.Combobox(window, values=items, width=30)
combobox2 = ttk.Combobox(window, values=items, width=30)
combobox2.set(items[1])
combobox1.set(items[0])
combobox1.place(y=650, x=330)
combobox2.place(y=650, x=710)


Morze = {
  
    "а": ".-",   "б": "-...",  "в": ".--",   "г": "--.",   "д": "-..",
    "е": ".", "ж": "...-",  "з": "--..",  "и": "..",
    "й": ".---", "к": "-.-",   "л": ".-..",  "м": "--",    "н": "-.",
    "о": "---",  "п": ".--.",  "р": ".-.",   "с": "...",   "т": "-",
    "у": "..-",  "ф": "..-.",  "х": "....",  "ц": "-.-.",  "ч": "---.",
    "ш": "----", "щ": "--.-",  "ъ": "--..-", "ы": "-.--",  "ь": "-..-",
    "э": "..-..", "ю": "..--", "я": ".-.-",

    "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....",
    "6": "-....", "7": "--...", "8": "---..", "9": "----.", "0": "-----",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "!": "-.-.--", "-": "-....-", "\n" : "\n"
}

dvoichn = {
    "а": "11000000", "б": "11000001", "в": "11000010", "г": "11000011", "д": "11000100",
    "е": "11000101", "ж": "11000110", "з": "11000111", "и": "11001000",
    "й": "11001001", "к": "11001010", "л": "11001011", "м": "11001100", "н": "11001101",
    "о": "11001110", "п": "11001111", "р": "11010000", "с": "11010001", "т": "11010010",
    "у": "11010011", "ф": "11010100", "х": "11010101", "ц": "11010110", "ч": "11010111",
    "ш": "11011000", "щ": "11011001", "ъ": "11011010", "ы": "11011011", "ь": "11011100",
    "э": "11011101", "ю": "11011110", "я": "11011111",

    "0": "00110000", "1": "00110001", "2": "00110010", "3": "00110011", "4": "00110100",
    "5": "00110101", "6": "00110110", "7": "00110111", "8": "00111000", "9": "00111001",
    ".": "00101110", ",": "00101100", "?": "00111111", "!": "00100001", "-": "00101101",
    "\n" : "\n"
}

def cod():
    new_text = Entry1.get("1.0", tk.END).strip()
    chs1 = combobox1.get()
    chs2 = combobox2.get()

    if chs1 == chs2:
        messagebox.showerror("Ошибка", "Выберите разные языки для кодирования и декодирования!")
        return

    if chs1 == "Русский Язык":
        new_text = new_text.lower() 
        if chs2 == "Азбука Морзе":
            result = ""
            for char in new_text:
                if char in Morze:
                    result += Morze[char] + " "
                elif char == " ":
                    result += "/ "  
                else:
                    messagebox.showwarning("Предупреждение", f"Символ '{char}' не поддерживается")
                    
            Entry2.config(state="normal")
            Entry2.delete("1.0", tk.END)
            Entry2.insert("1.0", result)
            Entry2.config(state="disabled")
        
        elif chs2 == "Двоичный код":
            result = ""
            for char in new_text.lower():
                if char in dvoichn:
                    result += dvoichn[char] + " "
                elif char == " ":
                    result += "00100000 "  
                else:
                    messagebox.showwarning("Предупреждение", f"Символ '{char}' не поддерживается")
            Entry2.config(state="normal")
            Entry2.delete("1.0", tk.END)
            Entry2.insert("1.0", result)
            Entry2.config(state="disabled")
                
    if chs2 == "Кирпичный язык":
        vowels = "аеёиоуыэюяАЕЁИОУЫЭЮЯ"
        result = ""
        for char in new_text:
            result += char.lower() 
            if char in vowels:
                result += "с" + char.lower()  

    elif chs1 == "Азбука Морзе":
        if chs2 == "Русский Язык":
            reverse_morze = {v: k for k, v in Morze.items()}
            temp_text = new_text.replace('\n', ' ¶ ')
            codes = temp_text.split()
            print(codes)
            result = ""
            for code in codes:
                if code in reverse_morze:
                    result += reverse_morze[code]
                elif code == "/":  
                    result += " "
                elif code == "¶":
                    result += "\n"
                else:
                    messagebox.showwarning("Предупреждение", f"Код '{code}' не поддерживается")
            Entry2.config(state="normal")
            Entry2.delete("1.0", tk.END)
            Entry2.insert("1.0", result)
            Entry2.config(state="disabled")
        else:
            messagebox.showerror("Ошибка", "Азбуку морзе можно декодировать только в русский!")
            return
    elif chs1 == "Двоичный код":
        if chs2 == "Русский Язык":
            reverse_dvoichn = {v: k for k, v in dvoichn.items()}
            temp_text = new_text.replace('\n', ' ¶ ')
            codes = temp_text.split()
            result = ""
            for code in codes:
                if code in reverse_dvoichn:
                    result += reverse_dvoichn[code]
                elif code == "00100000": 
                    result += " "
                elif code == "¶":
                    result += "\n"
                else:
                    messagebox.showwarning("Предупреждение", f"Код '{code}' не поддерживается")
        else:
            messagebox.showerror("Ошибка", "Двоичный код можно декодировать только в русский!")
            return

        
        Entry2.config(state="normal")
        Entry2.delete("1.0", tk.END)
        Entry2.insert("1.0", result)
        Entry2.config(state="disabled")
    
    elif chs1 == "Кирпичный язык":
        if chs2 == "Русский Язык":
            vowels = "аеёиоуыэюяАЕЁИОУЫЭЮЯ"
            result = ""
            i = 0
            while i < len(new_text):
                result += new_text[i]
                
                if (new_text[i] in vowels 
                    and i+2 < len(new_text) 
                    and new_text[i+1].lower() == "с"
                    and new_text[i+2].lower() == new_text[i].lower()):  
                    i += 2
                i += 1
            Entry2.config(state="normal")
            Entry2.delete("1.0", tk.END)
            Entry2.insert("1.0", result)
            Entry2.config(state="disabled")
    
        else:
            messagebox.showerror("Ошибка", "Кирпичный язык можно декодировать только в русский!")
            return
 

    Entry2.config(state="normal")  
    Entry2.delete("1.0", tk.END)  
    Entry2.insert("1.0", result)  
    Entry2.config(state="disabled")
    
def clear_entry1():
    Entry1.delete("1.0", tk.END)

def clear_entry2():
    Entry2.config(state="normal")
    Entry2.delete("1.0", tk.END)
    Entry2.config(state="disabled")

        
encode_button = tk.Button(window, text="Кодировать/Декодировать", command=cod)
encode_button.place(y=700, x=550)


clear1_button = tk.Button(window, text="Очистить поле ввода", command=clear_entry1)
clear1_button.place(y=525, x=260)


clear2_button = tk.Button(window, text="Очистить поле вывода", command=clear_entry2)
clear2_button.place(y=525, x=860)


def copytext1():
    Entry1.clipboard_clear()
    Entry1.clipboard_append(Entry1.get("1.0", tk.END))

def copytext2():
    Entry1.clipboard_clear()
    Entry2.clipboard_append(Entry2.get("1.0", tk.END))

def VstavButton():
    Entry1.delete("1.0", tk.END)
    Entry1.insert("insert", window.clipboard_get())
    
    
def VstavButton2():
    Entry2.delete("1.0", tk.END)
    Entry2.config(state = "normal")
    
    Entry2.insert("insert", window.clipboard_get())
    Entry2.config(state = "disabled")


copy_button = tk.Button(window, text="Скопировать текст", command = copytext1 )
copy_button.place(y=575, x = 260)

copy_button2 = tk.Button(window, text="Скопировать текст", command = copytext2 )
copy_button2.place(y=575, x = 860)

vstav_button = tk.Button(window, text="Вставить текст", command = VstavButton )
vstav_button.place(y=610, x = 260)


vstav_button = tk.Button(window, text="Вставить текст", command = VstavButton2 )
vstav_button.place(y=610, x = 860)

window.mainloop()
