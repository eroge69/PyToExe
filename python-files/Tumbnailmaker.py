import os
import cv2
import numpy as np
from tkinter import filedialog, Tk, Button, Label, Entry
from PIL import Image, ImageDraw, ImageFont

# Create output directories if they don't exist
os.makedirs("frames", exist_ok=True)
os.makedirs("upscaled", exist_ok=True)
os.makedirs("final", exist_ok=True)

# Extract frames from video
def extract_frames(video_path, interval=30):
    cap = cv2.VideoCapture(video_path)
    count = 0
    saved = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % interval == 0:
            frame_path = f"frames/frame_{saved}.jpg"
            cv2.imwrite(frame_path, frame)
            saved += 1
        count += 1
    cap.release()
    print(f"Extracted {saved} frames.")

# Detect the frame with most people using basic edge count (simplified logic)
def select_best_frame():
    best_frame = None
    best_score = 0
    for filename in os.listdir("frames"):
        path = os.path.join("frames", filename)
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        edges = cv2.Canny(img, 100, 200)
        score = np.sum(edges)
        if score > best_score:
            best_score = score
            best_frame = path
    return best_frame

# Enlarge image using OpenCV
def enlarge_image(image_path, target_size=(1280, 720)):
    img = cv2.imread(image_path)
    upscaled = cv2.resize(img, target_size, interpolation=cv2.INTER_CUBIC)
    upscaled_path = image_path.replace("frames", "upscaled")
    cv2.imwrite(upscaled_path, upscaled)
    return upscaled_path

# Add text overlay using Pillow
def add_text(image_path, text, font_size=48):
    img = Image.open(image_path).convert("RGBA")
    txt = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    draw.text((30, 30), text, fill="white", font=font)
    combined = Image.alpha_composite(img, txt).convert("RGB")
    final_path = image_path.replace("upscaled", "final")
    combined.save(final_path)
    return final_path

# GUI Application

def browse_video():
    path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.avi")])
    if path:
        video_path.set(path)
        status_label.config(text="Video selected")

def process_video():
    path = video_path.get()
    interval = int(interval_entry.get())
    extract_frames(path, interval=interval)
    status_label.config(text="Frames extracted")

def upscale_and_add_text():
    best_frame = select_best_frame()
    if best_frame:
        upscaled = enlarge_image(best_frame)
        final = add_text(upscaled, overlay_text.get())
        status_label.config(text="Thumbnail created from best frame")
    else:
        status_label.config(text="No frame found")

# GUI setup
if __name__ == "__main__":
    app = Tk()
    app.title("Thumbnail Creator")
    app.geometry("400x300")

    video_path = Entry(app, width=40)
    video_path.pack(pady=10)

    browse_button = Button(app, text="Browse Video", command=browse_video)
    browse_button.pack()

    Label(app, text="Frame Interval:").pack()
    interval_entry = Entry(app)
    interval_entry.insert(0, "30")
    interval_entry.pack(pady=5)

    Label(app, text="Overlay Text:").pack()
    overlay_text = Entry(app)
    overlay_text.insert(0, "Your Thumbnail Text")
    overlay_text.pack(pady=5)

    process_button = Button(app, text="Extract Frames", command=process_video)
    process_button.pack(pady=5)

    final_button = Button(app, text="Create Best Thumbnail", command=upscale_and_add_text)
    final_button.pack(pady=5)

    status_label = Label(app, text="")
    status_label.pack(pady=10)

    app.mainloop()
