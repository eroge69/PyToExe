import tkinter
import pyqrcode
from pyqrcode import *
from tkinter import *
from tkinter import messagebox
from tkinter import Tk, Label, Button, Entry
class app:
    def __init__(self, master):
        self.master = master
        master.title("QR Code Generator")
        Label(master, text="Content to generate QR Code").grid(row=0,sticky=W)
        Label(master, text="FileName").grid(row=1,sticky=W)
        self.E1=Entry(master)
        self.E2=Entry(master)
        self.E1.grid(row=0,column=1,padx=10)
        self.E2.grid(row=1,column=1,padx=10)
        self.B1=Button(master, text="Save as SVG" ,command = self.message1)
        self.B2=Button(master, text="Save as EPS" ,command = self.message2)
        self.B1.grid(row=2,column=0)
        self.B2.grid(row=2,column=1)
        Label(master,text="QR Code Generator by aravind using python").grid(row=3,column=0,columnspan=2)
    def message1(self):
        url = pyqrcode.create(self.E1.get())
        file_name = self.E2.get()
        url.svg(file_name+'.svg', scale=5)
    def message2(self):
        url = pyqrcode.create(self.E1.get())
        file_name = self.E2.get()
        url.eps(file_name+'.eps', scale=5)
root = Tk()
app = app(root)
root.resizable(False, False)
root.mainloop()
