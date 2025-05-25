import tkinter as tk

class Calculator:
    def __init__(self, win):
        self.win = win
        win.title("TinaCalc")
        win.geometry("300x400")
        self.nam_text = tk.StringVar()
        self.expression = ""
        self.javab = False

        self.entry = tk.Entry(win, textvariable=self.nam_text, justify="right", state="readonly")
        self.entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.sakhte_dokmeha()

        for i in range(6):
            self.set_satr(i, 1)
        for j in range(4):
            self.set_sotoon(j, 1)

    def set_satr(self, satr, faza):
        self.win.rowconfigure(satr, weight=faza)

    def set_sotoon(self, sotoon, faza):
        self.win.columnconfigure(sotoon, weight=faza)

    def hesab_kon(self):
        exp = self.expression
        if not exp:
            return ""

        adad = []
        amal = []

        temp = ""
        for ch in exp:
            if ch in '+-*/':
                if temp == "":
                    return "Error"
                adad.append(temp)
                temp = ""
                amal.append(ch)
            else:
                if ch.isdigit():
                    temp += ch
                else:
                    return "Error"

        if temp == "":
            return "Error"
        adad.append(temp)

        try:
            res = int(adad[0])
        except:
            return "Error"

        for i in range(len(amal)):
            try:
                b = int(adad[i+1])
            except:
                return "Error"

            if amal[i] == '+':
                res = res + b
            elif amal[i] == '-':
                res = res - b
            elif amal[i] == '*':
                res = res * b
            elif amal[i] == '/':
                if b == 0:
                    return "0"
                res = res // b
            else:
                return "Error"

        return str(res)

    def dokme_zade_shod(self, meghdar):
        if meghdar == 'C':
            self.expression = ""
            self.javab = False
        elif meghdar == '=':
            self.expression = self.hesab_kon()
            self.javab = True
        else:
            if self.javab:
                if meghdar.isdigit():
                    self.expression = meghdar
                    self.javab = False
                else:
                    self.expression += meghdar
                    self.javab = False
            else:
                self.expression += meghdar

        self.nam_text.set(self.expression)
        self.entry.config(state='readonly')

    def sakhte_dokmeha(self):
        dokmeha = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', 'C', '=', '+']
        ]

        for i in range(4):
            for j in range(4):
                btn = tk.Button(self.win, text=dokmeha[i][j], command=lambda x=dokmeha[i][j]: self.dokme_zade_shod(x))
                btn.grid(row=i+1, column=j, sticky='nsew', padx=2, pady=2)


root = tk.Tk()
app = Calculator(root)
root.mainloop()
