
import os
import string
from tkinter import Tk, Label, Button, filedialog, colorchooser, simpledialog
from PIL import Image, ImageDraw, ImageFont

CHARACTERS = string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation + " "

def generate_font_image(font_path, font_size, font_color, bg_color):
    cols = 16
    rows = (len(CHARACTERS) + cols - 1) // cols
    margin = 4
    font = ImageFont.truetype(font_path, font_size)

    max_w = max_h = 0
    for char in CHARACTERS:
        bbox = font.getbbox(char)
        max_w = max(max_w, bbox[2] - bbox[0])
        max_h = max(max_h, bbox[3] - bbox[1])

    cell_w = max_w + margin * 2
    cell_h = max_h + margin * 2

    img_w = cols * cell_w
    img_h = rows * cell_h

    img = Image.new("RGBA", (img_w, img_h), bg_color)
    draw = ImageDraw.Draw(img)

    txt_lines = []

    for idx, char in enumerate(CHARACTERS):
        row = idx // cols
        col = idx % cols
        x = col * cell_w + margin
        y = row * cell_h + margin
        draw.text((x, y), char, font=font, fill=font_color)
        txt_lines.append(f"{char} {col * cell_w} {row * cell_h} {cell_w} {cell_h}")

    return img, txt_lines

def start_gui():
    root = Tk()
    root.title("Kontakt Font Tool - Offline")

    Label(root, text="Vyber TTF font:").pack()

    def select_font():
        font_path = filedialog.askopenfilename(filetypes=[("TrueType Fonts", "*.ttf")])
        if not font_path:
            return
        font_size = simpledialog.askinteger("Velikost písma", "Zadej velikost fontu (např. 32):", initialvalue=32)
        font_color = colorchooser.askcolor(title="Barva písma")[0]
        bg_color = colorchooser.askcolor(title="Barva pozadí")[0]

        if not (font_size and font_color and bg_color):
            return

        font_rgb = tuple(map(int, font_color))
        bg_rgb = tuple(map(int, bg_color))

        image, txt_data = generate_font_image(font_path, font_size, font_rgb, bg_rgb)

        save_dir = filedialog.askdirectory(title="Vyber složku pro uložení výstupu")
        if not save_dir:
            return

        image.save(os.path.join(save_dir, "fontsheet.png"))
        with open(os.path.join(save_dir, "fontsheet.txt"), "w", encoding="utf-8") as f:
            for line in txt_data:
                f.write(line + "\n")

        Label(root, text="✅ Hotovo! Soubor uložen jako 'fontsheet.png' a 'fontsheet.txt'.").pack()

    Button(root, text="Spustit generátor", command=select_font).pack()
    root.mainloop()

start_gui()
