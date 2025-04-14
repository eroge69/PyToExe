from operator import index
from tkinter import *

root = Tk()

def min(event):
    ent_0.insert(END," - ")
def plus(event):
    ent_0.insert(END," + ")
def ymn(event):
    ent_0.insert(END," * ")
def dell(event):
    ent_0.insert(END, " / ")
def _1_(event):
    ent_0.insert(END, "1")
def _2_(event):
    ent_0.insert(END, "2")
def _3_(event):
    ent_0.insert(END, "3")
def _4_(event):
    ent_0.insert(END, "4")
def _5_(event):
    ent_0.insert(END, "5")
def _6_(event):
    ent_0.insert(END, "6")
def _7_(event):
    ent_0.insert(END, "7")
def _8_(event):
    ent_0.insert(END, "8")
def _9_(event):
    ent_0.insert(END, "9")
def _0_(event):
    ent_0.insert(END, "0")
def new_win(event):
    new_window = Toplevel(root)
    new_window.title("руководство пользования")
    new_window.geometry("250x150")
    new_window.resizable(width=False, height=False)
    Label(new_window, text="будет текст",font="Arial 10").place(x=100,y=55)
def cleare(event):
    ent_0.delete(0, END)

root.geometry('800x500')
root.title('калькулятор')
root.resizable(width=False, height=False)

lab_0 = Label(root, text= "калькулятор", font= "Arial 30" )
lab_1 = Label(root, text= "ввод:", font= "Arial 10" )
lab_2 = Label(root, text= "ответ:", font= "Arial 10" )

ent_1 = Entry(root, width= 30)

ent_0 = Entry(root, width= 30)

but_plus = Button(root)
but_plus = Button(text="+", width=10,   height=5 ,  font= "Arial 9")
but_plus.bind("<Button-1>",plus)

but_min = Button(root)
but_min = Button(text="-",font= "Arial 9")
but_min["width"] = 10
but_min["height"] = 5
but_min.bind("<Button-1>",min)

but_ymn = Button(root)
but_ymn = Button(text="*",font= "Arial 9")
but_ymn["width"] = 10
but_ymn["height"] = 5
but_ymn.bind("<Button-1>",ymn)

but_del = Button(root)
but_del['text'] = ("/")
but_del["width"] = 10
but_del["height"] = 5
but_del.bind("<Button-1>",dell)

but1 = Button(root)
but1['text'] = ("1")
but1["width"] = 10
but1["height"] = 5
but1.bind("<Button-1>",_1_)

but2 = Button(root)
but2['text'] = ("2")
but2["width"] = 10
but2["height"] = 5
but2.bind("<Button-1>",_2_)

but3 = Button(root)
but3['text'] = ("3")
but3["width"] = 10
but3["height"] = 5
but3.bind("<Button-1>",_3_)

but4 = Button(root)
but4['text'] = ("4")
but4["width"] = 10
but4["height"] = 5
but4.bind("<Button-1>",_4_)

but5 = Button(root)
but5['text'] = ("5")
but5["width"] = 10
but5["height"] = 5
but5.bind("<Button-1>",_5_)

but6 = Button(root)
but6['text'] = ("6")
but6["width"] = 10
but6["height"] = 5
but6.bind("<Button-1>",_6_)

but7 = Button(root)
but7['text'] = ("7")
but7["width"] = 10
but7["height"] = 5
but7.bind("<Button-1>",_7_)

but8 = Button(root)
but8['text'] = ("8")
but8["width"] = 10
but8["height"] = 5
but8.bind("<Button-1>",_8_)

but9 = Button(root)
but9['text'] = ("9")
but9["width"] = 10
but9["height"] = 5
but9.bind("<Button-1>",_9_)

but0 = Button(root)
but0['text'] = ("0")
but0["width"] = 10
but0["height"] = 5
but0.bind("<Button-1>",_0_)

but_clear = Button(root)
but_clear['text'] = ("очистить")
but_clear["width"] = 10
but_clear["height"] = 5
but_clear.bind("<Button-1>",cleare)

but_inf = Button(root)
but_inf['text'] = ("руководство пользования")
but_inf["width"] = 22
but_inf["height"] = 5
but_inf.bind("<Button-1>", new_win)

def calculate(event):
    ent_1.delete(0,END)
    str_given = ent_0.get()
    list_remaked = str_given.split()
    cnt_of_plus = list_remaked.count("+")
    cnt_of_minus = list_remaked.count("-")
    cnt_of_del = list_remaked.count("/")
    cnt_of_ymn = list_remaked.count("*")
    cnt_of_iterations = (cnt_of_plus + cnt_of_minus + cnt_of_del + cnt_of_ymn)

    for r in range(cnt_of_iterations):
        for i in list_remaked:

            if i == "*":
                ind_ymn = list_remaked.index(i)

                first_num_list = []
                index_of_first_num = ind_ymn - 1
                first_num_list.extend(list_remaked[index_of_first_num])
                str_first_num = "".join(first_num_list)
                int_first_num = int(str_first_num)

                second_num_list = []
                index_of_second_num = ind_ymn + 1
                second_num_list.extend(list_remaked[index_of_second_num])
                str_second_num = "".join(second_num_list)
                int_second_num = int(str_second_num)

                ans_of_ymn = (int_second_num * int_first_num)

                del list_remaked[0]
                del list_remaked[0]
                del list_remaked[0]
                ans_of_ymn_str = str(ans_of_ymn)
                list_remaked.insert(0, ans_of_ymn_str)

            if i == "/":
                ind_del = list_remaked.index(i)

                first_num_list_1 = []
                index_of_first_num_1 = ind_del - 1
                first_num_list_1.extend(list_remaked[index_of_first_num_1])
                str_first_num_1 = "".join(first_num_list_1)
                int_first_num_1 = int(str_first_num_1)

                second_num_list_1 = []
                index_of_second_num_1 = ind_del + 1
                second_num_list_1.extend(list_remaked[index_of_second_num_1])
                str_second_num_1 = "".join(second_num_list_1)
                int_second_num_1 = int(str_second_num_1)

                ans_of_del_1 = ( int_first_num_1  / int_second_num_1)

                del list_remaked[0]
                del list_remaked[0]
                del list_remaked[0]
                ans_of_del_str = str(ans_of_del_1)
                list_remaked.insert(0, ans_of_del_str)

            if i == "+":
                ind_plus = list_remaked.index(i)

                first_num_list_2 = []
                index_of_first_num_2 = ind_plus - 1
                first_num_list_2.extend(list_remaked[index_of_first_num_2])
                str_first_num_2 = "".join(first_num_list_2)
                int_first_num_2 = int(str_first_num_2)

                second_num_list_2 = []
                index_of_second_num_2 = ind_plus + 1
                second_num_list_2.extend(list_remaked[index_of_second_num_2])
                str_second_num_2 = "".join(second_num_list_2)
                int_second_num_2 = int(str_second_num_2)

                ans_of_plus_2 = (int_first_num_2 + int_second_num_2)

                del list_remaked[0]
                del list_remaked[0]
                del list_remaked[0]
                ans_of_plus_str = str(ans_of_plus_2)
                list_remaked.insert(0, ans_of_plus_str)

            if i == "-":
                ind_min = list_remaked.index(i)

                first_num_list_3 = []
                index_of_first_num_3 = ind_min - 1
                first_num_list_3.extend(list_remaked[index_of_first_num_3])
                str_first_num_3 = "".join(first_num_list_3)
                int_first_num_3 = int(str_first_num_3)

                second_num_list_3 = []
                index_of_second_num_3 = ind_min + 1
                second_num_list_3.extend(list_remaked[index_of_second_num_3])
                str_second_num_3 = "".join(second_num_list_3)
                int_second_num_3 = int(str_second_num_3)

                ans_of_minus_2 = (int_first_num_3 - int_second_num_3)

                del list_remaked[0]
                del list_remaked[0]
                del list_remaked[0]
                ans_of_minus_str = str(ans_of_minus_2)
                list_remaked.insert(0, ans_of_minus_str)
    ent_1.insert(END, list_remaked)

but_end = Button(root)
but_end['text'] = ("=")
but_end["width"] = 10
but_end["height"] = 5
but_end.bind("<Button-1>",calculate)

but_plus.place(x=700, y=400)
but_min.place(x=600, y=400)
but_ymn.place(x=500, y=400)
but_del.place(x=400, y=400)
but0.place(x=400, y=200)
but1.place(x=500, y=300)
but2.place(x=600,y=300)
but3.place(x=700,y=300)
but4.place(x=500,y=200)
but5.place(x=600,y=200)
but6.place(x=700,y=200)
but7.place(x=500,y=100)
but8.place(x=600,y=100)
but9.place(x=700,y=100)
but_end.place(x=400,y=300)
lab_0.pack()
ent_0.place(x=100,y=150)
lab_1.place(x=100,y=120)
lab_2.place(x=100,y=180)
ent_1.place(x=100,y=210)
but_inf.place(x=60,y=400)
but_clear.place(x=400, y=100)

root.mainloop()