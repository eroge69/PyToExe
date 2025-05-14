
import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Verrouiller"
        self.hi_there["command"] = self.verrouiller
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="Quitter", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def verrouiller(self):
        # Code pour verrouiller l'ordinateur
        pass

root = tk.Tk()
app = Application(master=root)
app.mainloop()