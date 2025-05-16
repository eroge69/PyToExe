import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import json
import os
import random

# Paths
DATA_FILE = 'data/words.json'
VISUALS_DIR = 'visuals'

# Ensure folders exist
os.makedirs('data', exist_ok=True)
os.makedirs(VISUALS_DIR, exist_ok=True)

# Word manager
class WordManager:
    def __init__(self):
        self.words = []
        self.load_words()

    def load_words(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                self.words = json.load(f)

    def save_words(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.words, f, indent=4)

    def add_word(self, word):
        word = word.strip().lower()
        if word and not any(w["word"] == word for w in self.words):
            self.words.append({
                "word": word,
                "color": random.choice(["#FF9999", "#99CCFF", "#CCFFCC", "#FFFF99"]),
                "shape": random.choice(["circle", "square"]),
                "icon": random.choice(["✨", "🌟", "📘", "💡", "🧠"]),
                "status": "unmarked"
            })
            self.save_words()

    def get_random_word(self):
        return random.choice(self.words) if self.words else None

# Image creator
def generate_image(word_data):
    W, H = 400, 300
    img = Image.new('RGB', (W, H), color=word_data["color"])
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_large = ImageFont.truetype("arial.ttf", 40)
        font_icon = ImageFont.truetype("seguiemj.ttf", 60)
    except:
        font_large = ImageFont.load_default()
        font_icon = ImageFont.load_default()

    # Draw icon
    icon = word_data.get("icon", "")
    draw.text((W // 2, 40), icon, font=font_icon, anchor="mm", fill="black")

    # Draw word
    word = word_data["word"].upper()
    draw.text((W // 2, H // 2), word, font=font_large, anchor="mm", fill="black")

    # Draw shape
    shape = word_data.get("shape", "circle")
    if shape == "circle":
        draw.ellipse([150, 200, 250, 300], outline="black", width=3)
    elif shape == "square":
        draw.rectangle([150, 200, 250, 300], outline="black", width=3)

    # Save image
    filename = os.path.join(VISUALS_DIR, f"{word_data['word']}.png")
    img.save(filename)
    return filename

# GUI
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Word Visualizer")
        self.manager = WordManager()
        self.current_word = None

        self.build_gui()
        self.show_random()

    def build_gui(self):
        self.root.geometry("800x500")
        self.root.configure(bg="#f9f9f9")

        # Top frame
        top = tk.Frame(self.root, bg="#f9f9f9")
        top.pack(pady=10)

        self.word_entry = tk.Entry(top, font=("Arial", 14), width=30)
        self.word_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(top, text="Add Word", command=self.add_word, bg="#4CAF50", fg="white").pack(side=tk.LEFT)

        # Middle
        self.image_label = tk.Label(self.root, bg="#f9f9f9")
        self.image_label.pack(pady=20)

        # Bottom controls
        bottom = tk.Frame(self.root, bg="#f9f9f9")
        bottom.pack()

        tk.Button(bottom, text="🔄 Shuffle", command=self.show_random).pack(side=tk.LEFT, padx=10)
        tk.Button(bottom, text="💾 Save Image", command=self.save_current_image).pack(side=tk.LEFT, padx=10)

    def add_word(self):
        word = self.word_entry.get()
        if word:
            self.manager.add_word(word)
            self.word_entry.delete(0, tk.END)
            self.show_word(word)
        else:
            messagebox.showwarning("Input Needed", "Please enter a word.")

    def show_word(self, word_text):
        for w in self.manager.words:
            if w["word"] == word_text.lower():
                self.current_word = w
                img_path = generate_image(w)
                img = Image.open(img_path)
                img = img.resize((400, 300))
                self.tk_img = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.tk_img)
                break

    def show_random(self):
        word_data = self.manager.get_random_word()
        if word_data:
            self.show_word(word_data["word"])

    def save_current_image(self):
        if self.current_word:
            path = os.path.join(VISUALS_DIR, f"{self.current_word['word']}.png")
            messagebox.showinfo("Saved", f"Image saved as:\n{path}")

# Start app
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
