import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_file():
    file_path = filedialog.askopenfilename(filetypes=[("GEM Files", "*.gem")])
    if not file_path:
        return

    new_path = file_path.replace('.gem', '.mp4')

    try:
        shutil.copy(file_path, new_path)
        messagebox.showinfo("تم التحويل", f"تم إنشاء الملف: {new_path}")
    except Exception as e:
        messagebox.showerror("خطأ", str(e))

root = tk.Tk()
root.title("محول GEM إلى MP4")
root.geometry("300x150")

label = tk.Label(root, text="اضغط على الزر لاختيار ملف .gem وتحويله")
label.pack(pady=10)

btn = tk.Button(root, text="اختيار الملف وتحويله", command=convert_file)
btn.pack(pady=10)

root.mainloop()
