# -*- coding: cp1251 -*-
import os
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
import numpy as np
from tensorflow.keras.models import load_model

clear = lambda: os.system('cls')

class Neiro:
    def __init__(self):
        #self.model = load_model('mnist.h5')
        self.model = load_model('mnist_and_custom.h5')

    def recognize(self, image):
        image = np.asarray(image).astype("float32") / 255
        image = image.reshape(1, 28, 28, 1)
        #print(image)

        output = self.model.predict([image])[0]

        #print(output.argmax())
        return output

def crop_black_background_and_center(image, size):
    image_np = np.array(image)

    # Find non-black pixels (pixel value > 0)
    non_black = np.argwhere(image_np > 0)

    # If all pixels are black, return the original image
    if non_black.size == 0:
        return image

    # Bounding box of non-black pixels
    top_left = non_black.min(axis=0)
    bottom_right = non_black.max(axis=0) + 1 # add 1 because slicing is exclusive at the end

    width = bottom_right[1] - top_left[1]
    height = bottom_right[0] - top_left[0]
    aspect_ratio = width / height

    # Resize the image to fit within size x size while maintaining aspect ratio
    if aspect_ratio > 1:  # Width is greater than height
        width = size
        height = int(size / aspect_ratio)
    else:  # Height is greater than width or square
        height = size
        width = int(size * aspect_ratio)

    # Make sure the content is centered by placing it on a white 28x28 background
    image = Image.new('L', (28, 28), color=0)

    # Crop image to bounding box
    # Convert back to Image for further processing
    # Resize the image to the new size
    # Paste the resized image onto the center of the background
    offset_x = (28 - width) // 2
    offset_y = (28 - height) // 2
    image.paste(Image.fromarray(image_np[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]]).resize((width, height), Image.LANCZOS), (offset_x, offset_y))
    #Image.NEAREST

    return image

class DigitApp:
    def __init__(self, root, width=28, height=28, scale=20):
        self.root = root
        self.root.title("���� ��� ��������� �����")
        self.root.resizable(False, False)

        self.neiro = Neiro()

        self.base_width = width
        self.base_height = height
        self.scale = scale
        self.bg_color = "black"
        #self.brush_color = "#ffffff"
        #self.brush_size = 1

        # Create image and drawing context
        self.image = Image.new("L", (self.base_width, self.base_height), self.bg_color)
        self.input_image = self.image
        self.draw = ImageDraw.Draw(self.image)

        # Canvas for drawing
        self.canvas = tk.Canvas(root, width=width*scale, height=height*scale, bg=self.bg_color)
        self.canvas.pack()

        # UI buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="��������", command=self.reset).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="���������", command=self.save_image).pack(side=tk.LEFT)

        # Bind events
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<B3-Motion>", self.paint)
        self.root.bind("<space>", self.reset)

        self.secondary_window = tk.Toplevel()
        self.secondary_window.title("����������� ���������� �� ���� ���������")
        self.secondary_window.resizable(False, False)
        self.secondary_canvas = tk.Canvas(self.secondary_window, width=width*scale, height=height*scale, bg=self.bg_color)
        self.secondary_canvas.pack()

        self.reset()

    def reset(self, event=None):
        self.draw.rectangle((0, 0, int(self.base_width * self.scale), int(self.base_height * self.scale)), fill=self.bg_color, outline=self.bg_color)
        self.input_image = self.image
        self.update_canvas()
        self.update_secondary_canvas()
        clear()
        print("��������� �����")

    def paint(self, event):
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)
        #radius = self.brush_size
        #self.draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=self.brush_color, outline=self.brush_color)
        i = 0                                                                                                                                                         	
        while i < self.base_width:
            j = 0
            while j < self.base_height:
                dist = (i - x) * (i - x) + (j - y) * (j - y);
                if dist < 1:
                    dist = 0.5
                dist *= dist
                p = self.image.getpixel((i, j))
                if event.state == 256:
                    p += int(76.5 / float(dist))
                else:
                    p -= int(76.5 / float(dist))
                self.draw.point((i, j), fill=p)
                j += 1
            i += 1
        self.input_image = crop_black_background_and_center(self.image, 26)
        self.update_canvas()
        self.update_secondary_canvas()
        self.show_status(self.neiro.recognize(self.input_image))

    def update_canvas(self):
        resized = self.image.resize(
            (int(self.base_width * self.scale), int(self.base_height * self.scale)),
            Image.NEAREST
        )
        self.tk_image = ImageTk.PhotoImage(resized)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def update_secondary_canvas(self):
        if self.secondary_window.winfo_exists():
            resized = self.input_image.resize(
                (int(self.base_width * self.scale), int(self.base_height * self.scale)),
                Image.NEAREST
            )
            self.tk_input_image = ImageTk.PhotoImage(resized)
            self.secondary_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_input_image)

    def save_image(self):
        self.image.save("custom.png")
        self.input_image.save("custom_resized.png")
        print("����������� ��������� � ���� custom.png")

    def show_status(self, output):
        clear()
        i = 0
        while i < 10:
            s = f"{i}: {float(output[i]):.8f}"
            if i == output.argmax():
                s += " <==="
            print(s)
            i += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitApp(root)
    root.after(1, lambda: root.focus_force())
    root.mainloop()
