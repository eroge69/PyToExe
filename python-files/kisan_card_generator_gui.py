
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

def generate_card():
    name = name_entry.get()
    mobile = mobile_entry.get()
    village = village_entry.get()
    photo_path = photo_label.image_path if hasattr(photo_label, 'image_path') else None

    card = Image.new('RGB', (600, 350), color='white')
    draw = ImageDraw.Draw(card)
    header_color = (0, 122, 204)
    draw.rectangle([0, 0, 600, 60], fill=header_color)

    font_large = ImageFont.truetype("arial.ttf", 24)
    font_small = ImageFont.truetype("arial.ttf", 20)
    font_bold = ImageFont.truetype("arialbd.ttf", 22)

    draw.text((20, 15), "किसान कार्ड", fill='white', font=font_large)
    draw.text((200, 90), f"नाम      : {name}", fill='black', font=font_small)
    draw.text((200, 130), f"मोबाइल : {mobile}", fill='black', font=font_bold)
    draw.text((200, 170), f"गांव      : {village}", fill='black', font=font_small)

    if photo_path and os.path.exists(photo_path):
        photo = Image.open(photo_path).resize((140, 140))
        card.paste(photo, (40, 90))

    card.save("kisan_card_output.png")
    tk.messagebox.showinfo("सफलता", "किसान कार्ड सेव हो गया (kisan_card_output.png)")

def upload_photo():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    if file_path:
        photo_label.image_path = file_path
        img = Image.open(file_path)
        img.thumbnail((100, 100))
        img = ImageTk.PhotoImage(img)
        photo_label.config(image=img)
        photo_label.image = img

app = tk.Tk()
app.title("किसान कार्ड जनरेटर")
app.geometry("400x400")

tk.Label(app, text="नाम:").pack()
name_entry = tk.Entry(app, width=30)
name_entry.pack()

tk.Label(app, text="मोबाइल:").pack()
mobile_entry = tk.Entry(app, width=30)
mobile_entry.pack()

tk.Label(app, text="गांव:").pack()
village_entry = tk.Entry(app, width=30)
village_entry.pack()

tk.Button(app, text="फोटो अपलोड करें", command=upload_photo).pack(pady=5)
photo_label = tk.Label(app)
photo_label.pack()

tk.Button(app, text="कार्ड जनरेट करें", command=generate_card).pack(pady=10)

app.mainloop()
