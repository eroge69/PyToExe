from tkinter import *
from tkinter import filedialog

t = Tk()
t.title("Notepad#")
t.geometry("25000x15000")
t.iconbitmap("C://Users//P1//Documents//Notepad#//Notepad_23093.ico")

types = [("Текстовый файл", "*.txt"), ("Python файлы", "*.py"), ("Файлы C Header", "*.h"), ("Файлы C++", "*.cpp"),          ("Файлы JavaScript", "*.js"), ("Файлы Source Компилятора", "*.qc"), ("Source Материалы","*.vmt"),("Все Файлы", "*.*")]


def quit():
    t.quit()
    




def settings():
    u = Toplevel()
    u.iconbitmap("C://Users//user//Downloads//Notepad#//Notepad_23093.ico")
    top.add_cascade(u,label="Тема:", menu=top)
    
    
    
    

def open_file():
    tfile = filedialog.askopenfilename(defaultextension="*.txt",filetypes=types)
    if tfile:  
        with open(tfile, "r", encoding="utf-8") as f:
            y.delete("1.0", END)  
            y.insert("1.0", f.read())    
            
            
            
def new_text():
    y.delete("1.0", END)  
    

def save_text():

    oo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=types, title="Выберите формат:")
    if oo: 
        with open(oo, 'w', encoding='utf-8') as o:
            o.write(y.get("1.0", END))  

y = Text(height=100, width=300, wrap="word")
y.pack()

t.option_add("*tearOff", FALSE)

top = Menu()

main = Menu()

file = Menu(main)

edit = Menu()

edit.add_command(label = "Настройки",command=settings)

file.add_command(label="Новый", command = new_text)
file.add_command(label="Сохранить", command=save_text)
file.add_command(label="Открыть",command=open_file)
file.add_command(label="Выйти", command=quit)  

main.add_cascade(label="Файл", menu=file)
main.add_cascade(label="Правка",menu=edit)
main.add_cascade(label="Вид")


t.config(menu=main)
t.mainloop()



























