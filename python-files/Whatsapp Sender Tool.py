# Save the full working Python script to a .py file
whatsapp_sender_py = """
import pandas as pd
import time
import pyautogui
import pyperclip
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

def send_whatsapp_messages(file_path, message_template, media_files, max_messages, delay_seconds):
    try:
        df = pd.read_excel(file_path)
        df.fillna('', inplace=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read Excel file: {e}")
        return

    log = []
    sent_count = 0

    for index, row in df.iterrows():
        if sent_count >= max_messages:
            break

        name = str(row['Name']).strip().title()
        number1 = str(row['Mobile Number']).strip().replace(" ", "")
        number2 = str(row['Alternate Mobile Number']).strip().replace(" ", "")

        for number in [number1, number2]:
            if not number or number == 'nan':
                number = '0000000000'
            if number != '0000000000' and number.isdigit():
                phone_number = '+91' + number
                personalized_message = message_template.replace("{name}", name)

                # Open chat
                link = f"https://wa.me/{phone_number}"
                os.system(f'start {link}')
                time.sleep(8)

                # Paste message
                pyperclip.copy(personalized_message)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(1)
                pyautogui.press("enter")
                time.sleep(1)

                # Attach media
                for media_file in media_files:
                    pyautogui.hotkey("ctrl", "alt", "a")  # file attach shortcut
                    time.sleep(2)
                    pyperclip.copy(media_file)
                    pyautogui.hotkey("ctrl", "v")
                    time.sleep(1)
                    pyautogui.press("enter")
                    time.sleep(2)

                pyautogui.press("enter")
                log.append([name, phone_number, "Sent", time.strftime("%Y-%m-%d %H:%M:%S")])
                sent_count += 1
                time.sleep(delay_seconds)

    log_df = pd.DataFrame(log, columns=["Name", "Number", "Status", "Timestamp"])
    log_df.to_csv("whatsapp_session_log.csv", index=False)
    messagebox.showinfo("Done", f"Sent {sent_count} messages. Log saved as whatsapp_session_log.csv")

def run_tool():
    root = tk.Tk()
    root.withdraw()

    excel_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel Files", "*.xlsx")])
    if not excel_path:
        return

    message = simpledialog.askstring("Message", "Enter your message (use {name} for personalization):")
    if not message:
        return

    media_paths = filedialog.askopenfilenames(title="Select Media Files")
    if not media_paths:
        return

    try:
        max_msgs = simpledialog.askinteger("Limit", "Number of messages to send:", initialvalue=50)
        delay_secs = simpledialog.askinteger("Delay", "Delay between messages (sec):", initialvalue=15)
    except:
        messagebox.showerror("Error", "Invalid input for limit or delay.")
        return

    send_whatsapp_messages(excel_path, message, media_paths, max_msgs, delay_secs)

if __name__ == "__main__":
    run_tool()
"""

# Save Python file
python_file_path = "/mnt/data/Whatsapp_Sender_Tool.py"
with open(python_file_path, "w") as f:
    f.write(whatsapp_sender_py)

# Save the .bat file
bat_file_content = """
@echo off
echo Creating EXE from Whatsapp_Sender_Tool.py ...
pyinstaller --onefile --noconsole Whatsapp_Sender_Tool.py
pause
"""

bat_file_path = "/mnt/data/build_whatsapp_tool.bat"
with open(bat_file_path, "w") as f:
    f.write(bat_file_content)

python_file_path, bat_file_path
