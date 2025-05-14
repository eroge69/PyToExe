
import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
from skimage.metrics import structural_similarity as ssim
import numpy as np
import pandas as pd

def render_text(font_path, text="The quick brown", image_size=(600, 100)):
    font = ImageFont.truetype(font_path, size=60)
    img = Image.new("L", image_size, color=255)
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((image_size[0] - w) / 2, (image_size[1] - h) / 2), text, fill=0, font=font)
    return np.array(img)

def compare_fonts(image_path, font_dir):
    sample_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    sample_img = cv2.resize(sample_img, (600, 100))
    results = []
    for fname in os.listdir(font_dir):
        if not fname.lower().endswith((".ttf", ".otf")):
            continue
        try:
            font_path = os.path.join(font_dir, fname)
            rendered = render_text(font_path)
            score = ssim(sample_img, rendered)
            results.append((fname, round(score * 100, 2)))
        except:
            continue
    return sorted(results, key=lambda x: -x[1])

def browse_image():
    path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if path:
        image_path.set(path)
        load_preview(path)

def browse_fonts():
    path = filedialog.askdirectory()
    if path:
        font_dir.set(path)

def load_preview(path):
    img = Image.open(path).resize((300, 100))
    imgtk = ImageTk.PhotoImage(img)
    preview_label.config(image=imgtk)
    preview_label.image = imgtk

def run_comparison():
    if not os.path.isfile(image_path.get()) or not os.path.isdir(font_dir.get()):
        messagebox.showerror("Lỗi", "Vui lòng chọn ảnh và thư mục font hợp lệ.")
        return
    results = compare_fonts(image_path.get(), font_dir.get())
    output.delete(1.0, tk.END)
    for name, score in results[:10]:
        output.insert(tk.END, f"{name}: {score}%\n")
    df = pd.DataFrame(results, columns=["Font", "Similarity"])
    df.to_excel("ket_qua_tim_font.xlsx", index=False)
    messagebox.showinfo("Xong", "Đã lưu kết quả vào 'ket_qua_tim_font.xlsx'")

app = tk.Tk()
app.title("Phần mềm tìm font giống hình ảnh")
app.geometry("700x500")

image_path = tk.StringVar()
font_dir = tk.StringVar()

tk.Label(app, text="Chọn ảnh chứa chữ:").pack()
tk.Entry(app, textvariable=image_path, width=80).pack()
tk.Button(app, text="Chọn ảnh", command=browse_image).pack()

tk.Label(app, text="Chọn thư mục chứa font:").pack()
tk.Entry(app, textvariable=font_dir, width=80).pack()
tk.Button(app, text="Chọn thư mục", command=browse_fonts).pack()

preview_label = tk.Label(app)
preview_label.pack(pady=10)

tk.Button(app, text="Tìm font giống nhất", command=run_comparison, bg="green", fg="white").pack(pady=10)

output = tk.Text(app, height=10)
output.pack()

app.mainloop()
