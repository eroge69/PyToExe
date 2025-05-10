import shutil
import os
import tkinter as tk
from tkinter import messagebox

# 设置路径
src_dir = r"C:\Users\94693\OneDrive\Pictures\Screenshots"
dst_dir = r"C:\Users\94693\OneDrive\Documents\leidian9\Pictures\WeiXin"
ldplayer_path = r"C:\leidian\LDPlayer9\dnplayer.exe"

# 处理函数
def confirm_action():
    value = entry.get().strip()
    if value.lower() == "shanchu":
        try:
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            files = os.listdir(src_dir)
            if not files:
                messagebox.showinfo("提示", "Screenshots 文件夹为空。")
            else:
                for file in files:
                    shutil.move(os.path.join(src_dir, file), dst_dir)
                messagebox.showinfo("成功", "已将所有文件剪切到目标文件夹！")
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {e}")
    elif value.lower() == "dakai":
        try:
            os.startfile(ldplayer_path)
            messagebox.showinfo("成功", "已启动雷电模拟器！")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {e}")
    else:
        messagebox.showinfo("设置成功", f"属性翻倍已设置为 {value} 倍！")

# 创建界面
root = tk.Tk()
root.title("魔兽争霸作弊器 v9.9")
root.geometry("350x250")
root.resizable(False, False)

tk.Label(root, text="魔兽争霸作弊器 v9.9", font=("Arial", 14, "bold")).pack(pady=10)

chk1 = tk.Checkbutton(root, text="全图开关")
chk1.select()
chk1.pack(anchor="w", padx=40)
chk2 = tk.Checkbutton(root, text="自动 T 人")
chk2.pack(anchor="w", padx=40)
chk3 = tk.Checkbutton(root, text="开启无敌")
chk3.select()
chk3.pack(anchor="w", padx=40)

tk.Label(root, text="属性翻倍倍数:").pack(pady=10)
entry = tk.Entry(root, width=20)
entry.pack()

tk.Button(root, text="确定", width=10, command=confirm_action).pack(pady=15)

root.mainloop()