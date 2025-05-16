from tkinter import*
Window=Tk()
Window.geometry('600x300')
Window.title('Калькулятор комунальних послуг')

Label(Window, text='Введіть список значень показників лічилька через пропуск: ').place(x=70, y=25)

Label(Window, text='Попередні показники: газ     світло     вода').place(x=30, y=50)
text1=Text(Window, width=50, height=2, bg='white', font='Arial 11')
text1.place(x=25, y=70)

Label(Window, text='Поточні показники: газ     світло     вода').place(x=30, y=110)
text2=Text(Window, width=50, height=2, bg='white', font='Arial 11')
text2.place(x=25, y=130)

but=Button(Window, text="Розрахувати")
but.place(x=250, y=250)
gaz=Label(Window, text="Спожито газу: ")
gaz.place(x=20, y=180)
elektro=Label(Window, text="Спожито електроенергії: ")
elektro.place(x=20, y=200)
voda=Label(Window, text="Спожито води: ")
voda.place(x=20, y=220)

def komunalni (event):
          a=[int(i) for i in text1.get('1.0', END).split()]
          b=[int(i) for i in text2.get('1.0', END).split()]
          g=b[0]-a[0]
          g1=g*7.96
          gaz["text"]= "Спожито газу: "+str(g)+" м/куб"+" на суму - "+str(g1)+" грн"
          e=b[1]-a[1]
          e1=e*4.32
          elektro["text"]= "Спожито електроенергії: "+str(e)+" кВт/год"+" на суму - "+str(e1)+" грн"
          v=b[0]-a[0]
          v1=v*7.96
          voda["text"]= "Спожито води: "+str(v)+" м/куб"+" на суму - "+str(v1)+" грн"
         
but.bind("<Button-1>", komunalni)

Window.mainloop()
