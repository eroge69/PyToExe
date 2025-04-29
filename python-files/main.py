# 五行洗炼识别锁定工具 - 升级版
# 兼容 v0-pytoexe.vercel.app 打包

import pytesseract
import pyautogui
import pyttsx3
import tkinter as tk
from tkinter import messagebox
import re
import time
import os
from PIL import Image

# 设置Tesseract-OCR路径（如果安装了Tesseract并配置环境变量，可以注释掉）
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 默认识别区域（根据你的屏幕自己调整）
OCR_REGION = (600, 250, 300, 100)  # (left, top, width, height)
LOCK_BUTTON_POS = (820, 400)       # 锁定按钮位置 (x, y)

# 初始化语音引擎
engine = pyttsx3.init()

# 截图函数
def capture_screen(region):
    screenshot = pyautogui.screenshot(region=region)
    screenshot.save("screenshot.png")

# OCR识别
def extract_text(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang='chi_sim')
    return text

# 匹配目标属性
def match_target(text, threshold):
    pattern = r"(金属性|火属性|木属性|水属性|土属性).*?([0-9]+\.[0-9]+)%"
    matches = re.findall(pattern, text)
    for attr, val in matches:
        if float(val) >= threshold:
            return attr, val
    return None, None

# 语音播报
def speak(text):
    engine.say(text)
    engine.runAndWait()

# 点击锁定
def click_lock_button(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.click()

# 成功后保存截图
def save_success_screenshot():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    success_path = f"success_{timestamp}.png"
    pyautogui.screenshot(success_path)
    print(f"🎯 成功截图已保存: {success_path}")

# 主检测循环
def start_check(threshold_value):
    messagebox.showinfo("提示", f"开始识别，锁定阈值：{threshold_value}%")
    while True:
        capture_screen(OCR_REGION)
        text = extract_text("screenshot.png")
        attr, val = match_target(text, threshold_value)
        if attr:
            msg = f"✔ 发现 {attr} 数值 {val}%，开始锁定！"
            print(msg)
            speak(msg)
            click_lock_button(*LOCK_BUTTON_POS)
            save_success_screenshot()
            messagebox.showinfo("锁定成功", msg)
            break
        else:
            print("未检测到目标属性，继续刷新...")
        time.sleep(1)

# GUI界面
def run_gui():
    def on_start():
        try:
            threshold = float(entry.get())
            if threshold <= 0 or threshold >= 100:
                raise ValueError
            root.destroy()
            start_check(threshold)
        except:
            messagebox.showerror("错误", "请输入正确的数值（如2.90）")

    root = tk.Tk()
    root.title("五行洗炼识别锁定工具")
    root.geometry("300x150")

    label = tk.Label(root, text="请输入识别阈值（%）:", font=("Arial", 12))
    label.pack(pady=10)

    entry = tk.Entry(root, font=("Arial", 12))
    entry.pack()

    start_button = tk.Button(root, text="开始识别", font=("Arial", 12), command=on_start)
    start_button.pack(pady=20)

    root.mainloop()

if __name__ == '__main__':
    run_gui()
