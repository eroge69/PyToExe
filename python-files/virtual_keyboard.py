import tkinter as tk
import pyautogui
import time
import threading

class GlobalVK:
    def __init__(self, root):
        self.root = root
        self.root.title("Bàn phím ảo - Gửi phím ra ngoài")
        self.root.geometry("300x400")
        self.root.attributes('-topmost', True)

        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('0', 3, 1), ('←', 3, 0), ('Enter', 3, 2),
        ]

        for (text, row, col) in buttons:
            if text == '←':
                action = self.backspace
            elif text == 'Enter':
                action = self.enter
            else:
                action = lambda t=text: self.send_key(t)

            btn = tk.Button(root, text=text, font=("Arial", 18), width=5, height=2, command=action)
            btn.grid(row=row, column=col, padx=5, pady=5)

    def send_key(self, key):
        threading.Thread(target=self._delayed_send, args=(key,)).start()

    def backspace(self):
        threading.Thread(target=self._delayed_send, args=('backspace',)).start()

    def enter(self):
        threading.Thread(target=self._delayed_send, args=('enter',)).start()

    def _delayed_send(self, key):
        self.root.withdraw()  # Ẩn cửa sổ
        time.sleep(0.2)       # Chờ để trả focus về app khác
        if key in ['backspace', 'enter']:
            pyautogui.press(key)
        else:
            pyautogui.write(key)
        time.sleep(0.1)
        self.root.deiconify()  # Hiện lại cửa sổ

# Chạy chương trình
if __name__ == "__main__":
    root = tk.Tk()
    app = GlobalVK(root)
    root.mainloop()
