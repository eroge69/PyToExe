
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

# 支持的视频文件扩展名
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.flv']

def get_video_files(folder):
    return sorted([f for f in os.listdir(folder)
                   if os.path.isfile(f) and os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS])

def get_new_names_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        names = [line.strip() for line in file if line.strip()]
    return names

def rename_files(video_files, new_names):
    log = []
    for i, original in enumerate(video_files):
        base, ext = os.path.splitext(original)
        new_name = new_names[i] + ext
        suffix = 1
        while os.path.exists(new_name):
            new_name = f"{new_names[i]}_{suffix}{ext}"
            suffix += 1
        os.rename(original, new_name)
        log.append(f"{original} → {new_name}")
    return log

def main():
    current_folder = os.getcwd()
    video_files = get_video_files(current_folder)

    if not video_files:
        messagebox.showerror("错误", "当前目录下未找到支持的视频文件（mp4, avi, mkv, mov, flv）")
        return

    root = tk.Tk()
    root.withdraw()
    txt_path = filedialog.askopenfilename(title="请选择包含新文件名的TXT文件",
                                          filetypes=[("Text files", "*.txt")])
    if not txt_path:
        messagebox.showinfo("取消", "未选择txt文件，程序已取消。")
        return

    try:
        new_names = get_new_names_from_txt(txt_path)
    except Exception as e:
        messagebox.showerror("错误", f"读取TXT文件时出错：{e}")
        return

    if len(new_names) != len(video_files):
        messagebox.showerror("错误", f"文件数量不匹配：视频文件 {len(video_files)} 个，名称 {len(new_names)} 行。")
        return

    try:
        log = rename_files(video_files, new_names)
        messagebox.showinfo("重命名完成", "
".join(log))
    except Exception as e:
        messagebox.showerror("重命名失败", str(e))

if __name__ == "__main__":
    main()
