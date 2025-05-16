import tkinter as tk
t=tk.Tk()
t.title('Calculator')
t.geometry('400x600')
t.iconbitmap('calculator-2017-10-10.ico')
num='0'
num2=''
alamat=0
label=tk.Label(t,text=num,font=('irancell',40))
label.pack()
num=''
label2=tk.Label(t,text='',font=('irancell',20))
label2.place(x=300,y=0)
def btnd0():
    global num
    num+='0'
    label.config(text=num)
btn=tk.Button(t,text='   0   ',font=('irancell',15),command=btnd0)
btn.place(x=110, y=410)
def btndnght():
    global num
    num+='.'
    label.config(text=num)
btn=tk.Button(t,text='   .   ',font=('irancell',15),command=btndnght)
btn.place(x=190, y=410)
def btnd1():
    global num
    num+='1'
    label.config(text=num)
btn=tk.Button(t,text='   1   ',font=('irancell',15),command=btnd1)
btn.place(x=30, y=170)
def btnd2():
    global num
    num+='2'
    label.config(text=num)
btn=tk.Button(t,text='   2   ',font=('irancell',15),command=btnd2)
btn.place(x=110, y=170)
def btnd3():
    global num
    num+='3'
    label.config(text=num)
btn=tk.Button(t,text='   3   ',font=('irancell',15),command=btnd3)
btn.place(x=190, y=170)
def btnd4():
    global num
    num+='4'
    label.config(text=num)
btn=tk.Button(t,text='   4   ',font=('irancell',15),command=btnd4)
btn.place(x=30, y=250)
def btnd5():
    global num
    num+='5'
    label.config(text=num)
btn=tk.Button(t,text='   5   ',font=('irancell',15),command=btnd5)
btn.place(x=110, y=250)
def btnd6():
    global num
    num+='6'
    label.config(text=num)
btn=tk.Button(t,text='   6   ',font=('irancell',15),command=btnd6)
btn.place(x=190, y=250)
def btnd7():
    global num
    num+='7'
    label.config(text=num)
btn=tk.Button(t,text='   7   ',font=('irancell',15),command=btnd7)
btn.place(x=30, y=330)
def btnd8():
    global num
    num+='8'
    label.config(text=num)
btn=tk.Button(t,text='   8   ',font=('irancell',15),command=btnd8)
btn.place(x=110, y=330)
def btnd9():
    global num
    num+='9'
    label.config(text=num)
btn=tk.Button(t,text='   9   ',font=('irancell',15),command=btnd9)
btn.place(x=190, y=330)
def btnddel():
    global num
    num=float(num)
    num//=10
    num=int(num)
    label.config(text=num)
    num=str(num)
btn=tk.Button(t,text=' Del ',font=('irancell',15),command=btnddel)
btn.place(x=30, y=90)
def btndac():
    global num
    num='0'
    label.config(text=num)
    num=''
btn=tk.Button(t,text=' AC ',font=('irancell',15),command=btndac)
btn.place(x=110, y=90)
def btndtqs():
    global num
    global num2
    global alamat
    num2=num
    num=''
    label.config(text=num)
    num=''
    label2.config(text='÷')
    alamat=1
btn=tk.Button(t,text='   ÷   ',font=('irancell',15),command=btndtqs)
btn.place(x=190, y=90)
def btndzrb():
    global num
    global num2
    global alamat
    num2=num
    num=''
    label.config(text=num)
    num=''
    label2.config(text='x')
    alamat=2
btn=tk.Button(t,text='   x   ',font=('irancell',15),command=btndzrb)
btn.place(x=270, y=90)
def btndjam():
    global num
    global num2
    global alamat
    num2=num
    num=''
    label.config(text=num)
    num=''
    label2.config(text='+')
    alamat=3
btn=tk.Button(t,text='   +   ',font=('irancell',15),command=btndjam)
btn.place(x=270, y=250)
def btndmnf():
    global num
    global num2
    global alamat
    num2=num
    num=''
    label.config(text=num)
    num=''
    label2.config(text='-')
    alamat=4
btn=tk.Button(t,text='   -   ',font=('irancell',15),command=btndmnf)
btn.place(x=270, y=170)
def btndmnfms():
    global num
    global num2
    global alamat
    alamat=5
    num=float(num)
    num=num*-1
    if num%1==0:
        num=int(num)
    num=str(num)
    label.config(text=num)
btn=tk.Button(t,text='-/+',font=('irancell',15),command=btndmnfms)
btn.place(x=270, y=410)
def btndmosavi():
    global num
    global num2
    global alamat
    if alamat==1:
        num=float(num)
        num2=float(num2)
        num=num2/num
        num=str(num)
        label.config(text=num)
        label2.config(text='')
    if alamat==2:
        num=float(num)
        num2=float(num2)
        num=num2*num
        num=str(num)
        label.config(text=num)
        label2.config(text='')
    if alamat==3:
        num=float(num)
        num2=float(num2)
        num=num2+num
        num=str(num)
        label.config(text=num)
        label2.config(text='')
    if alamat==4:
        num=float(num)
        num2=float(num2)
        num=num2-num
        num=str(num)
        label.config(text=num)
        label2.config(text='')
    if float(num)%1==0:
        num=float(num)
        num=int(num)
        num=str(num)
        label.config(text=num)
btn=tk.Button(t,text='   =   ',font=('irancell',15),command=btndmosavi)
btn.place(x=270, y=330)
t.mainloop()
