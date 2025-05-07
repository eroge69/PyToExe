import random as r
from tkinter import *
markk=2
mark=0
f='Arial 15 normal roman'

def show_message():
    try:
        global mark
        ans=entry.get()
        ans1=entry1.get()
        ans2=entry2.get()
        ans3=entry3.get()
        ans4=entry4.get()
        ans5=entry5.get()
        ans6=entry6.get()
        ans7=entry7.get()
        surname=entry8.get()
        if ans1.isdigit and ans2.isdigit and ans3.isdigit and ans5.isdigit and ans.isdigit and ans4.isdigit and ans6.isdigit and ans7.isdigit and surname !='':
            if int(ans)==answ: mark+=1
            if int(ans1)==answ1: mark+=1
            if int(ans2)==answ2: mark+=1
            if int(ans3)==answ3: mark+=1
            if int(ans4)==answ4: mark+=1
            if int(ans5)==answ5: mark+=1
            if int(ans6)==answ6: mark+=1
            if int(ans7)==answ7: mark+=1
            label=Label(root,text=f'    {answ}    ',fg='#0F0', font=f)
            label.grid(row=0,column=3)
            label=Label(root,text=f'    {answ1}    ',fg='#0F0', font=f)
            label.grid(row=1,column=3)
            label=Label(root,text=f'    {answ2}    ',fg='#0F0', font=f)
            label.grid(row=2,column=3)
            label=Label(root,text=f'    {answ3}    ',fg='#0F0', font=f)
            label.grid(row=3,column=3)
            label=Label(root,text=f'    {answ4}    ',fg='#0F0', font=f)
            label.grid(row=4,column=3)
            label=Label(root,text=f'    {answ5}    ',fg='#0F0', font=f)
            label.grid(row=5,column=3)
            label=Label(root,text=f'    {answ6}    ',fg='#0F0', font=f)
            label.grid(row=6,column=3)
            label=Label(root,text=f'    {answ7}    ',fg='#0F0', font=f)
            label.grid(row=7,column=3)
            if mark==8: markk=5
            elif mark==7: markk=4
            elif mark==6 or mark==5: markk=3
            else: markk=2
            with open(r'\\srv5\общая папка учеников\logs.txt','a', encoding='UTF-8') as fil:
                fil.write(f'{surname} - {markk}')
                fil.write('\n')
            messagebox.showinfo('Результат',  f'Ваша оценка {markk}!')
            root.withdraw()
        else:
            messagebox.showinfo('Ошибка','Некорректный формат данных')
    except Exception as e: print(e)
root=Tk()
root.title('Единицы измерения информации')
root.geometry('800x400')
root.resizable(1,1)
root.minsize(400,200)
root.maxsize(1920,1080)
root.update_idletasks()
randbit=r.randint(8,128)
randbit-=randbit%8
answ=randbit//8

label=Label(root, text=f'{randbit} бит   ', font=f)
label.grid(row=0,column=0)

randbit1=r.randint(3,22)
answ1=randbit1*8

label1=Label(root, text=f'{randbit1} байт   ',font=f)
label1.grid(row=1,column=0)

randbit2=r.randint(2,6)
answ2=randbit2*1024

label2=Label(root, text=f'{randbit2} Мбайт   ', font=f)
label2.grid(row=2,column=0)

randbit3=r.randint(1024,9216)
randbit3-=randbit3%1024
answ3=randbit3//1024

label3=Label(root, text=f'{randbit3} Кбайт   ', font=f)
label3.grid(row=3,column=0)

randbit4=r.randint(1024,9216)
randbit4-=randbit4%1024
answ4=randbit4//1024

label4=Label(root, text=f'{randbit4} байт   ', font=f)
label4.grid(row=4,column=0)

randbit5=r.randint(1,9)
answ5=randbit5*1024

label5=Label(root, text=f'{randbit5} Гбайт   ', font=f)
label5.grid(row=5,column=0)

randbit6=r.randint(1024,9216)
randbit6-=randbit6%1024
answ6=randbit6//1024

label6=Label(root, text=f'{randbit6} Мбайт   ', font=f)
label6.grid(row=6,column=0)

randbit7=r.randint(8192,24576)
randbit7-=randbit7%8192
answ7=randbit7//8192

label7=Label(root, text=f'{randbit7} бит   ', font=f)
label7.grid(row=7,column=0)

label8=Label(root, text='Введите фамилию и класс',font=f)
label8.grid(row=8, column=0)

entry=Entry(root,font=f)
entry.grid(row=0,column=1)

entry1=Entry(root,font=f)
entry1.grid(row=1,column=1)

entry2=Entry(root,font=f)
entry2.grid(row=2,column=1)

entry3=Entry(root,font=f)
entry3.grid(row=3,column=1)

entry4=Entry(root,font=f)
entry4.grid(row=4,column=1)

entry5=Entry(root,font=f)
entry5.grid(row=5, column=1)

entry6=Entry(root,font=f)
entry6.grid(row=6, column=1)

entry7=Entry(root,font=f)
entry7.grid(row=7, column=1)

entry8=Entry(root, font=f)
entry8.grid(row=8, column=1)

label=Label(root,text='байт',font=f)
label.grid(row=0,column=2)
label=Label(root,text='бит',font=f)
label.grid(row=1,column=2)
label=Label(root,text='Кбайт',font=f)
label.grid(row=2,column=2)
label=Label(root,text='Мбайт',font=f)
label.grid(row=3,column=2)
label=Label(root,text='Кбайт',font=f)
label.grid(row=4,column=2)
label=Label(root,text='Мбайт',font=f)
label.grid(row=5,column=2)
label=Label(root,text='Гбайт',font=f)
label.grid(row=6,column=2)
label=Label(root,text='Кбайт',font=f)
label.grid(row=7,column=2)

btn=Button(text='Закончить!', command=show_message,font=f)
btn.grid(row=10)

root.mainloop()