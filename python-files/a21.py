from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import datetime


win1=Tk()
win1.geometry('500x500')
win1.title('Personnel entry and exit control')
win1.resizable()

def manager():
    manager_user=e1.get()
    manager_password=e2.get()
    situ=combo_box.get()
    if manager_user=="admin" and manager_password=="12345":
        l6["text"]="hello manager what you want to do?".upper()
        if situ=="add":
            with open("karmandan.txt","a") as file:
                karmand_name=e3.get()
                karmand_pass=e4.get()
                #l6["text"]=(f'name={karmand_name} pass={karmand_pass}'+"\n")
                file.write(f'{karmand_name}@{karmand_pass}'+"\n")
                l6["text"]=f'{e3.get()} added to main list'
        elif situ=="remove":
            pass
        elif situ=="none":
           l6["text"]="no person added or removed" 
    else:
        l6["text"]="you are not system manager".upper()

def login():
    with open ("karmandan.txt","r") as file:
        cont=file.read()
        if f'{e3.get()}@{e4.get()}' in cont:
            messagebox.showinfo("message","user and password is correct")
            l6["text"]=f'Time of {e3.get()} saved to the file successfully'
            file2=open(f'{e5.get()}.txt',"a")
            file2.write(f'name={e3.get()} time={datetime.datetime.now()}'+"\n")
            file2.close()
            e3.delete(0,END)
            e4.delete(0,END)
        elif e3.get() in cont:
            l6["text"]="your name exist be sure your password is correct"
            messagebox.showinfo("message","user or password not correct")
            e3.delete(0,END)
            e4.delete(0,END)
        elif  e3.get() not in cont:
            l6["text"]="your name not in list"
            messagebox.showinfo("message","this name not in list")
            e3.delete(0,END)
            e4.delete(0,END)
        else:
            pass    

k1=LabelFrame(win1,text="manager side",width=220,height=200)
k1.place(x=1,y=5)
k2=LabelFrame(win1,text="personel side",width=270,height=200)
k2.place(x=228,y=5)

l1=Label(win1,text='manager user:',width=15,height=1,bg="orange")
l1.place(x=8,y=25)

l2=Label(win1,text='manager password',width=15,height=1,bg="orange")
l2.place(x=8,y=65)

e1=Entry(win1,width=14,bg="sky blue",relief="sunken",borderwidth=5)
e1.place(x=123,y=25)

e2=Entry(win1,width=14,show='*',bg="sky blue",relief="sunken",borderwidth=5)
e2.place(x=123,y=65)
l10=Label(win1,text='choose one',width=15,height=1,bg="orange",justify="left")
l10.place(x=3,y=156)
combo_box=ttk.Combobox(win1,width=15)
combo_box["values"]=list(['add','remove','none'])
combo_box.place(x=100,y=156)

l3=Label(win1,text='person name:',width=12,height=1,bg="orange")
l3.place(x=230,y=25)

l4=Label(win1,text='password',width=12,height=1,bg="orange")
l4.place(x=230,y=65)

e3=Entry(win1,width=25,bg="pink",relief="sunken",borderwidth=5)
e3.place(x=330,y=25)

e4=Entry(win1,width=25,show='*',bg="pink",relief="sunken",borderwidth=5)
e4.place(x=330,y=65)

l5=Label(win1,text='enter your file date: ',width=15,bg='orange')
l5.place(x=230,y=105)

e5=Entry(win1,width=20,relief="sunken",borderwidth=5)
e5.place(x=345,y=105)

l6=Label(win1,width=60,text='massage',bg="yellow",font="verdana 10 bold italic")
l6.place(x=5,y=220)

k3=edit_area=ScrolledText(win1,
        width=30,
        height=10,
        bg="sky blue",
        fg="dark blue",
        font="calibri 15 bold italic",
        )#inja mishod be jaye scrolledText text newsht vali dige scroll bar nadasht
k3.place(x=10,y=250)

b1=Button(win1,padx=20,text="manager",width=7,bg="green",relief="raised",borderwidth=5,command=manager)
b1.place(x=8,y=105)
b1=Button(win1,padx=20,text="save your time",width=12,bg="pink",relief="raised",borderwidth=5,command=login)
b1.place(x=250,y=140)
win1.mainloop()
#py -m pip install pyinstaller