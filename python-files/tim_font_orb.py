
import os
import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from tkinter import Tk, filedialog, Label, Entry, Button, StringVar, messagebox, Text

def extract_characters(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    chars = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 5 and h > 10:
            char_img = image[y:y+h, x:x+w]
            chars.append((x, char_img))
    chars = sorted(chars, key=lambda x: x[0])
    return [char[1] for char in chars]

def render_character(font_path, char, size=(100, 100)):
    try:
        font = ImageFont.truetype(font_path, 80)
        img = Image.new('L', size, color=255)
        draw = ImageDraw.Draw(img)
        w, h = draw.textsize(char, font=font)
        draw.text(((size[0]-w)//2, (size[1]-h)//2), char, fill=0, font=font)
        return np.array(img)
    except:
        return np.ones(size, dtype=np.uint8) * 255

def match_images(img1, img2):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    if des1 is None or des2 is None:
        return 0
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    return len(matches)

def find_best_fonts(image_path, font_dir):
    chars = extract_characters(image_path)
    font_scores = []
    for font_file in os.listdir(font_dir):
        if not font_file.lower().endswith((".ttf", ".otf")):
            continue
        font_path = os.path.join(font_dir, font_file)
        total_score = 0
        for i, char_img in enumerate(chars):
            rendered = render_character(font_path, chr(65 + i))
            char_img_resized = cv2.resize(char_img, (100, 100))
            score = match_images(char_img_resized, rendered)
            total_score += score
        font_scores.append((font_file, total_score))
    font_scores.sort(key=lambda x: -x[1])
    return font_scores[:10]

def browse_image():
    path = filedialog.askopenfilename()
    if path:
        image_path.set(path)

def browse_folder():
    path = filedialog.askdirectory()
    if path:
        font_folder.set(path)

def run():
    if not os.path.isfile(image_path.get()) or not os.path.isdir(font_folder.get()):
        messagebox.showerror("Lỗi", "Vui lòng chọn đúng ảnh và thư mục font.")
        return
    results = find_best_fonts(image_path.get(), font_folder.get())
    output.delete("1.0", "end")
    for font, score in results:
        output.insert("end", f"{font}: {score}\n")

root = Tk()
root.title("Tìm font bằng ORB thông minh")

image_path = StringVar()
font_folder = StringVar()

Label(root, text="Ảnh chứa chữ:").pack()
Entry(root, textvariable=image_path, width=80).pack()
Button(root, text="Chọn ảnh", command=browse_image).pack()

Label(root, text="Thư mục font:").pack()
Entry(root, textvariable=font_folder, width=80).pack()
Button(root, text="Chọn thư mục", command=browse_folder).pack()

Button(root, text="Tìm font giống nhất", command=run, bg="green", fg="white").pack(pady=10)

output = Text(root, height=15)
output.pack()

root.mainloop()
