import tkinter as tk
from threading import Thread
import time
import keyboard
import pyautogui

class Clicker:
    def __init__(self):
        self.running = False
        self.cps = 10
        self.click_key = 'f6'
        self.mine_key = 'f7'
        self.macro1_key = 'f8'
        self.macro2_key = 'f9'
        self.macro1_text = '/spawn'
        self.macro2_text = '/home'

    def start_clicking(self):
        while self.running:
            pyautogui.click()
            time.sleep(1 / self.cps)

    def start_mining(self):
        while self.running:
            pyautogui.mouseDown()
            time.sleep(1 / self.cps)
            pyautogui.mouseUp()
            time.sleep(0.01)

    def listen_keys(self):
        while True:
            if keyboard.is_pressed(self.click_key):
                self.running = True
                self.start_clicking()
                self.running = False
            if keyboard.is_pressed(self.mine_key):
                self.running = True
                self.start_mining()
                self.running = False
            if keyboard.is_pressed(self.macro1_key):
                keyboard.write(self.macro1_text)
                keyboard.press('enter')
            if keyboard.is_pressed(self.macro2_key):
                keyboard.write(self.macro2_text)
                keyboard.press('enter')
            time.sleep(0.01)

clicker = Clicker()

def start_bot():
    clicker.cps = cps_slider.get()
    clicker.click_key = click_entry.get()
    clicker.mine_key = mine_entry.get()
    clicker.macro1_key = macro1_key_entry.get()
    clicker.macro2_key = macro2_key_entry.get()
    clicker.macro1_text = macro1_entry.get()
    clicker.macro2_text = macro2_entry.get()
    Thread(target=clicker.listen_keys, daemon=True).start()

# GUI
root = tk.Tk()
root.title('GigaChad Clicker by ChatGPT')
root.geometry('400x400')

cps_slider = tk.Scale(root, from_=1, to=20, orient=tk.HORIZONTAL, label='CPS')
cps_slider.pack()
cps_slider.set(10)

tk.Label(root, text='Key for Clicking:').pack()
click_entry = tk.Entry(root)
click_entry.insert(0, 'f6')
click_entry.pack()

tk.Label(root, text='Key for Mining:').pack()
mine_entry = tk.Entry(root)
mine_entry.insert(0, 'f7')
mine_entry.pack()

tk.Label(root, text='Key for Macro 1:').pack()
macro1_key_entry = tk.Entry(root)
macro1_key_entry.insert(0, 'f8')
macro1_key_entry.pack()

tk.Label(root, text='Macro 1 Text:').pack()
macro1_entry = tk.Entry(root)
macro1_entry.insert(0, '/spawn')
macro1_entry.pack()

tk.Label(root, text='Key for Macro 2:').pack()
macro2_key_entry = tk.Entry(root)
macro2_key_entry.insert(0, 'f9')
macro2_key_entry.pack()

tk.Label(root, text='Macro 2 Text:').pack()
macro2_entry = tk.Entry(root)
macro2_entry.insert(0, '/home')
macro2_entry.pack()

start_button = tk.Button(root, text='Start', command=start_bot)
start_button.pack(pady=20)

root.mainloop()
