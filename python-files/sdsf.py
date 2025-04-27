import os

os.system(r"start C:\Users\evgen\AppData\Local\Programs\Microsoft_VS_Code\Code.exe")

import keyboard

login = 'esenchugov'
password = '5785'

login_list = list(login)
password_list = list(password)

def pas():
    for i in login_list:
        keyboard.send(i)

def log():
    for i in password_list:
        keyboard.send(str(i))

from time import sleep
sleep(6)
pas()
keyboard.send('enter')
sleep(0.5)
log()
keyboard.send('enter')
