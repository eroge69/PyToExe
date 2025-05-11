import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

root = tk.Tk()
root.title("مطبعة الصور")
root.geometry("800x600")
root.configure(bg="white")

preview_img = None
current_image_path = None

img_label = tk.Label(root, bg="white")
img_label.pack(pady=20)

def load_image(path):
    global preview_img, current_image_path
    try:
        img = Image.open(path)
        img.thumbnail((400, 400))
        preview_img = ImageTk.PhotoImage(img)
        img_label.config(image=preview_img)
        current_image_path = path
    except Exception as e:
        messagebox.showerror("خطأ", f"فشل تحميل الصورة: {e}")

def open_image():
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
    if path:
        load_image(path)

def print_image():
    if not current_image_path:
        messagebox.showwarning("تنبيه", "من فضلك اختر صورة أولاً.")
        return
    size = size_var.get()
    custom_width = width_entry.get()
    custom_height = height_entry.get()

    if size == "مخصص":
        if not custom_width or not custom_height:
            messagebox.showwarning("تنبيه", "أدخل المقاسات المخصصة.")
            return
        try:
            w = int(custom_width)
            h = int(custom_height)
        except:
            messagebox.showwarning("خطأ", "المقاسات يجب أن تكون أرقام.")
            return
    else:
        sizes = {"A4": (210, 297), "A5": (148, 210), "A6": (105, 148)}
        w, h = sizes.get(size, (210, 297))

    messagebox.showinfo("طباعة", f"سيتم طباعة الصورة بحجم {w}mm × {h}mm")

control_frame = tk.Frame(root, bg="white")
control_frame.pack(pady=10)

tk.Button(control_frame, text="اختر صورة", command=open_image).grid(row=0, column=0, padx=10)

size_var = tk.StringVar(value="A4")
tk.OptionMenu(control_frame, size_var, "A4", "A5", "A6", "مخصص").grid(row=0, column=1)

width_entry = tk.Entry(control_frame, width=5)
height_entry = tk.Entry(control_frame, width=5)
tk.Label(control_frame, text="عرض (مم):", bg="white").grid(row=1, column=0)
width_entry.grid(row=1, column=1)
tk.Label(control_frame, text="ارتفاع (مم):", bg="white").grid(row=1, column=2)
height_entry.grid(row=1, column=3)

tk.Button(root, text="🖨️ طباعة", bg="green", fg="white", font=("Arial", 14), command=print_image).pack(pady=20)

root.mainloop()
