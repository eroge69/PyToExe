import pyautogui
from pynput import keyboard
import time

# 全局控制变量
clicking = True  # 初始状态为运行中
interval = 0.1   # 点击间隔（秒）

def on_press(key):
    """ 键盘按键回调函数 """
    global clicking
    if key == keyboard.Key.space:
        clicking = not clicking
        status = "运行中" if clicking else "已暂停"
        print(f"\n状态切换：{status}")

# 设置键盘监听器
listener = keyboard.Listener(on_press=on_press)
listener.start()

print("连点器已启动！（按下空格键暂停/继续，Ctrl+C退出）")
print("初始状态：运行中")

try:
    while True:
        if clicking:
            pyautogui.click()    # 执行鼠标点击
            time.sleep(interval) # 等待间隔时间
        else:
            time.sleep(0.05)     # 非活动状态时降低CPU占用
except KeyboardInterrupt:
    print("\n程序已终止")
finally:
    listener.stop()  # 确保释放键盘监听资源