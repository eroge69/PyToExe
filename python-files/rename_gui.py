
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')

def select_folder():
    return filedialog.askdirectory(title="选择需要重命名的文件夹")

def select_name_file():
    return filedialog.askopenfilename(title="选择包含新名称的TXT文件", filetypes=[("Text files", "*.txt")])

def main():
    root = tk.Tk()
    root.withdraw()

    folder_path = select_folder()
    if not folder_path:
        messagebox.showerror("错误", "未选择文件夹")
        return

    name_file_path = select_name_file()
    if not name_file_path:
        messagebox.showerror("错误", "未选择新文件名文件")
        return

    original_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    sorted_files = sorted(original_files, key=extract_number)

    with open(name_file_path, "r", encoding="utf-8") as f:
        new_names = [line.strip() for line in f if line.strip()]

    if len(sorted_files) != len(new_names):
        messagebox.showerror("数量不匹配", f"文件夹中有 {len(sorted_files)} 个文件，名称列表有 {len(new_names)} 项")
        return

    for old_name, new_base in zip(sorted_files, new_names):
        old_path = os.path.join(folder_path, old_name)
        ext = os.path.splitext(old_name)[1]
        new_name = new_base + ext
        new_path = os.path.join(folder_path, new_name)

        if os.path.exists(new_path):
            print(f"⚠️ 已存在：{new_name}，跳过")
            continue

        os.rename(old_path, new_path)
        print(f"✅ {old_name} → {new_name}")

    messagebox.showinfo("完成", "重命名已完成")

if __name__ == "__main__":
    main()
