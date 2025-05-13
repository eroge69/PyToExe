import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_excel():
    input_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if not input_path:
        return

    output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if not output_path:
        return

    try:
        df = pd.read_excel(input_path, usecols=range(9))
        new_df = pd.DataFrame()

        new_df["发件州"] = df["发件州"]
        new_df["发件城市"] = df["发件城市"]
        new_df["发件人邮编"] = ""
        new_df["发件人地址"] = ""
        new_df["收件人姓名"] = df["收件人姓名"]
        new_df["收件州"] = df["收件州"]
        new_df["收件城市"] = df["收件城市"]
        new_df["收件人邮编"] = df["收件人邮编"]
        new_df["收件地址一"] = df["收件地址一"]

        new_df.to_excel(output_path, index=False)
        messagebox.showinfo("成功", f"转换完成！文件已保存至：\n{output_path}")
    except Exception as e:
        messagebox.showerror("错误", str(e))

root = tk.Tk()
root.title("Excel列重排工具")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

label = tk.Label(frame, text="点击按钮选择Excel文件，并输出转换后文件")
label.pack(pady=(0, 10))

btn = tk.Button(frame, text="开始转换", command=convert_excel, width=20)
btn.pack()

root.mainloop()
