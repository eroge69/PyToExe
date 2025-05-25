
import tkinter as tk

class GRECalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("GRE Calculator")
        self.root.geometry("300x400")
        self.memory = 0
        self.create_widgets()

    def create_widgets(self):
        self.entry = tk.Entry(self.root, font=("Arial", 18), borderwidth=2, relief="solid", justify='right')
        self.entry.grid(row=0, column=0, columnspan=4, sticky="we", ipady=10)

        buttons = [
            ("MC", self.memory_clear), ("MR", self.memory_recall), ("M+", self.memory_add), ("M-", self.memory_subtract),
            ("7", lambda: self.append("7")), ("8", lambda: self.append("8")), ("9", lambda: self.append("9")), ("/", lambda: self.append("/")),
            ("4", lambda: self.append("4")), ("5", lambda: self.append("5")), ("6", lambda: self.append("6")), ("*", lambda: self.append("*")),
            ("1", lambda: self.append("1")), ("2", lambda: self.append("2")), ("3", lambda: self.append("3")), ("-", lambda: self.append("-")),
            ("0", lambda: self.append("0")), (".", lambda: self.append(".")), ("=", self.calculate), ("+", lambda: self.append("+")),
            ("C", self.clear), ("Transfer", self.transfer)
        ]

        row, col = 1, 0
        for (text, command) in buttons:
            button = tk.Button(self.root, text=text, width=6, height=2, command=command)
            button.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def append(self, char):
        self.entry.insert(tk.END, char)

    def clear(self):
        self.entry.delete(0, tk.END)

    def calculate(self):
        try:
            result = eval(self.entry.get())
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, result)
        except:
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, "Error")

    def memory_clear(self):
        self.memory = 0

    def memory_recall(self):
        self.entry.insert(tk.END, str(self.memory))

    def memory_add(self):
        try:
            self.memory += float(self.entry.get())
        except:
            pass

    def memory_subtract(self):
        try:
            self.memory -= float(self.entry.get())
        except:
            pass

    def transfer(self):
        print("Transfer Display:", self.entry.get())  # Placeholder for GRE-like behavior

if __name__ == "__main__":
    root = tk.Tk()
    app = GRECalculator(root)
    root.mainloop()
