import ctypes
import time
import random
import os
import webbrowser
import pyautogui
from tkinter import *
from tkinter import messagebox
import winsound
import subprocess
import keyboard  # To lock special keys like Ctrl, Alt, Shift, F1-F12

# Window setup
root = Tk()
root.title("Warning: Security Alert")
root.geometry("500x300")
root.configure(bg='black')

# Add a scary image
try:
    img = PhotoImage(file="horror_image.png")  # Path to your horror image
    label = Label(root, image=img, bg='black')
    label.pack()
except:
    pass  # If no image, skip the error

# Add two paragraphs of horror text
text = """
This is a simulated warning from a hacker group!
Your computer has been infected with ransomware. 
All your files are encrypted, and only we can decrypt them!
"""
text2 = """
You will be contacted for a ransom payment in Bitcoin.
Failure to pay will result in permanent data loss.
We are watching your every move.
"""
label1 = Label(root, text=text, font=("Helvetica", 12), fg="red", bg="black")
label1.pack(pady=10)
label2 = Label(root, text=text2, font=("Helvetica", 12), fg="red", bg="black")
label2.pack(pady=10)

# Function to simulate "Execution" button behavior
def execute_fake_ransomware():
    # Open temp folder several times
    for _ in range(5):
        subprocess.Popen("explorer C:\\Windows\\Temp")

    # Play beep sound several times
    for _ in range(10):
        winsound.Beep(random.randint(200, 1000), 500)

    # Run Disk Cleanup (this is harmless)
    subprocess.Popen("cleanmgr")
    
    # Simulate fake error
    ctypes.windll.user32.MessageBoxW(0, "Your system has been compromised. Pay Bitcoin to 1A1B2C3D4E5F6G7H8I9J", "Fake Ransomware", 0x10)

    # Wait a little before opening "encrypted" fake window
    time.sleep(2)

    # Lock special keys (Ctrl, Alt, Shift, F1-F12)
    for key in range(112, 124):  # F1 to F12
        keyboard.block_key(key)
    keyboard.block_key('ctrl')
    keyboard.block_key('alt')
    keyboard.block_key('shift')

    # Open fake "Encryption" window
    def password_prompt():
        password = "123456"  # Correct password to "decrypt"
        def check_password():
            entered_password = entry.get()
            if entered_password == password:
                # Unlock keyboard (fake)
                pyautogui.alert("Correct Password! Your files are decrypted.")
                unlock_keys()
                root.quit()
            else:
                pyautogui.alert("Incorrect password. Try again.")

        # Window for entering password
        password_window = Toplevel(root)
        password_window.title("File Encryption")
        password_window.geometry("400x200")
        
        label3 = Label(password_window, text="Enter Password to Decrypt Files", font=("Helvetica", 12), fg="red")
        label3.pack(pady=20)

        entry = Entry(password_window, show="*", font=("Helvetica", 12))
        entry.pack(pady=10)

        submit_btn = Button(password_window, text="Decrypt", font=("Helvetica", 12), command=check_password)
        submit_btn.pack(pady=20)

    password_prompt()

# Function to unlock keys after decryption
def unlock_keys():
    for key in range(112, 124):  # Unlock F1 to F12 keys
        keyboard.unblock_key(key)
    keyboard.unblock_key('ctrl')
    keyboard.unblock_key('alt')
    keyboard.unblock_key('shift')

    # Display the "PC has died" message after correct password
    ctypes.windll.user32.MessageBoxW(0, "Your PC has now died. Use it as long as you can...", "ERROR", 0x10)

    # Simulate closing windows after encryption and fake PC death message
    time.sleep(2)
    root.quit()

# Button to start the prank execution
execute_btn = Button(root, text="Execute", command=execute_fake_ransomware, font=("Helvetica", 14), bg="red", fg="white")
execute_btn.pack(pady=20)

root.mainloop()
