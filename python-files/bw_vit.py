import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2
import os

def ps_black_and_white_numpy(im_array, weights, lightness_ratio=0.2):
    r_w, y_w, g_w, c_w, b_w, m_w = [w / 100 for w in weights]
    orig_b = im_array[:, :, 2].astype(np.float32)
    r = im_array[:, :, 0].astype(np.float32)
    g = im_array[:, :, 1].astype(np.float32)
    b = orig_b.copy()

    gray = np.minimum(np.minimum(r, g), b)
    r -= gray
    g -= gray
    b -= gray

    mask_c = (r == 0)
    mask_m = (g == 0) & (~mask_c)
    mask_y = (~mask_c) & (~mask_m)

    out = np.zeros_like(gray)

    cyan = np.minimum(g, b)
    out += mask_c * (gray + cyan * c_w + (g - cyan) * g_w + (b - cyan) * b_w)

    magenta = np.minimum(r, b)
    out += mask_m * (gray + magenta * m_w + (r - magenta) * r_w + (b - magenta) * b_w)

    yellow = np.minimum(r, g)
    out += mask_y * (gray + yellow * y_w + (r - yellow) * r_w + (g - yellow) * g_w)

    lab = cv2.cvtColor(im_array.astype(np.uint8), cv2.COLOR_RGB2Lab)
    L = lab[:, :, 0].astype(np.float32) * (255.0 / 100.0)
    out = (1 - lightness_ratio) * out + lightness_ratio * L

    return np.stack([out, out, out], axis=2).clip(0, 255).astype(np.uint8)

class BWFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BW_Vit - Black & White Filter App")
        self.root.geometry("800x600")
        self.root.configure(bg="white")

        self.weights = [40, -200, 40, 60, 20, 80]  # R, Y, G, C, B, M
        self.orig_image = None
        self.preview_image = None
        self.im_array = None
        self._throttle_job = None

        self.build_gui()

    def build_gui(self):
        # 顶部按钮栏
        top_frame = tk.Frame(self.root, bg="white")
        top_frame.pack(side="top", fill="x", pady=10)

        tk.Button(top_frame, text="📂 Open Image", command=self.load_image).pack(side="left", padx=10)
        self.save_btn = tk.Button(top_frame, text="💾 Save Result", command=self.save_image, state="disabled")
        self.save_btn.pack(side="left")

        # 图像展示
        image_frame = tk.Frame(self.root, bg="white")
        image_frame.pack(pady=5)

        self.panel_orig = tk.Label(image_frame, text="Original", bg="white")
        self.panel_orig.grid(row=0, column=0, padx=20)

        self.panel_filtered = tk.Label(image_frame, text="Filtered", bg="white")
        self.panel_filtered.grid(row=0, column=1, padx=20)

        # 滑动条区域
        self.slider_vars = []
        self.slider_labels = ["R", "Y", "G", "C", "B", "M"]
        slider_frame = tk.Frame(self.root, bg="white")
        slider_frame.pack(pady=10)

        for i, label in enumerate(self.slider_labels):
            var = tk.IntVar(value=self.weights[i])
            self.slider_vars.append(var)
            row = tk.Frame(slider_frame, bg="white")
            row.pack(fill="x", padx=20)
            tk.Label(row, text=f"{label}", width=3, bg="white").pack(side="left")
            tk.Scale(row, from_=-300, to=300, orient="horizontal", variable=var,
                     command=self.update_image_smooth, length=500, bg="white").pack(side="left")

        # Lightness slider
        self.lightness_ratio = tk.DoubleVar(value=20)
        self.light_label = tk.Label(self.root, text="Lightness Contribution: 20%", bg="white")
        self.light_label.pack()
        tk.Scale(self.root, from_=0, to=100, orient="horizontal", variable=self.lightness_ratio,
                 command=self.update_image_smooth, length=500, bg="white").pack()

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")
        ])
        if file_path:
            self.orig_image = Image.open(file_path).convert("RGB")
            self.preview_image = self.orig_image.resize((300, 300))
            self.im_array = np.array(self.preview_image)
            self.save_btn.config(state="normal")
            self.refresh_display()

    def update_image_smooth(self, val):
        self.light_label.config(text=f"Lightness Contribution: {int(self.lightness_ratio.get())}%")
        if self._throttle_job:
            self.root.after_cancel(self._throttle_job)
        self._throttle_job = self.root.after(100, self.refresh_display)

    def refresh_display(self):
        weights = [var.get() for var in self.slider_vars]
        ratio = self.lightness_ratio.get() / 100.0
        result_array = ps_black_and_white_numpy(self.im_array, weights, lightness_ratio=ratio)
        result_img = Image.fromarray(result_array)

        tk_orig = ImageTk.PhotoImage(self.preview_image)
        self.panel_orig.configure(image=tk_orig)
        self.panel_orig.image = tk_orig

        tk_result = ImageTk.PhotoImage(result_img)
        self.panel_filtered.configure(image=tk_result)
        self.panel_filtered.image = tk_result

    def save_image(self):
        if self.orig_image is None:
            return
        weights = [var.get() for var in self.slider_vars]
        ratio = self.lightness_ratio.get() / 100.0
        result_array = ps_black_and_white_numpy(np.array(self.orig_image), weights, lightness_ratio=ratio)
        result_img = Image.fromarray(result_array)
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if file_path:
            result_img.save(file_path)
            messagebox.showinfo("Saved", f"Image saved to:\n{file_path}")

# 启动主程序
if __name__ == "__main__":
    root = tk.Tk()
    app = BWFilterApp(root)
    root.mainloop()
