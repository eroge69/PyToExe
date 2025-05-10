from tkinter import Tk, Label, Button, filedialog, colorchooser, Entry, IntVar, Checkbutton, StringVar
from PIL import Image, ImageDraw, ImageFont

font_path = None

def choose_font():
    global font_path
    path = filedialog.askopenfilename(title="Vyber TTF font", filetypes=[("Font files", "*.ttf")])
    if path:
        font_path = path
        font_label_var.set(path.split("/")[-1])

def generate_bitmap():
    if not font_path:
        print("Nejprve vyber font (.ttf)")
        return

    text = entry_text.get().upper() if var_uppercase.get() else entry_text.get()
    font_size = int(entry_font_size.get())
    char_spacing = int(entry_spacing.get())
    space_width = int(entry_space_width.get())
    color = color_hex.get()

    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"Chyba při načítání fontu: {e}")
        return

    width = sum([font.getsize(c)[0] + char_spacing for c in text]) + (text.count(" ") * space_width)
    height = font.getsize("A")[1]

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    x = 0
    for c in text:
        if c == " ":
            x += space_width
        else:
            draw.text((x, 0), c, font=font, fill=color)
            x += font.getsize(c)[0] + char_spacing

    save_path = filedialog.asksaveasfilename(defaultextension=".png")
    if save_path:
        image.save(save_path)

def choose_color():
    color_code = colorchooser.askcolor(title="Vyber barvu")[1]
    if color_code:
        color_hex.set(color_code + "FF")

root = Tk()
root.title("Kontakt Bitmap Font Generator")

Label(root, text="Text:").grid(row=0, column=0, sticky="e")
entry_text = Entry(root, width=30)
entry_text.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

Label(root, text="Font size (px):").grid(row=1, column=0, sticky="e")
entry_font_size = Entry(root, width=10)
entry_font_size.insert(0, "24")
entry_font_size.grid(row=1, column=1, padx=5, pady=5)

Label(root, text="Char spacing (px):").grid(row=2, column=0, sticky="e")
entry_spacing = Entry(root, width=10)
entry_spacing.insert(0, "1")
entry_spacing.grid(row=2, column=1, padx=5, pady=5)

Label(root, text="Space width (px):").grid(row=3, column=0, sticky="e")
entry_space_width = Entry(root, width=10)
entry_space_width.insert(0, "4")
entry_space_width.grid(row=3, column=1, padx=5, pady=5)

color_hex = StringVar(value="#FFFFFFFF")
Label(root, text="Color (#RGBA):").grid(row=4, column=0, sticky="e")
Entry(root, textvariable=color_hex, width=10).grid(row=4, column=1, padx=5, pady=5)
Button(root, text="Vyber barvu", command=choose_color).grid(row=4, column=2, padx=5)

var_uppercase = IntVar(value=1)
Checkbutton(root, text="All Uppercase", variable=var_uppercase).grid(row=5, column=0, columnspan=2, pady=5)

font_label_var = StringVar(value="(žádný font)")
Label(root, text="Vybraný font:").grid(row=6, column=0, sticky="e")
Label(root, textvariable=font_label_var).grid(row=6, column=1, sticky="w")
Button(root, text="Vyber TTF", command=choose_font).grid(row=6, column=2, padx=5, pady=5)

Button(root, text="Vygeneruj bitmapu", command=generate_bitmap).grid(row=7, column=0, columnspan=3, pady=10)

root.mainloop()
