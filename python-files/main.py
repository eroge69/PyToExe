import tkinter as tk
import ctypes
import threading
import tempfile
import urllib.request
import os
import json

# === Constants ===
RECT_WIDTH_1 = 200
RECT_WIDTH_2 = 320
RECT_HEIGHT = 80
RECT_RADIUS = 20
RECT_COLOR = "#2196F3"
POS_FILE = os.path.join(tempfile.gettempdir(), "widget_positions.json")

# === Get usable screen area (excluding taskbar)
def get_work_area():
    class RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long),
                    ("top", ctypes.c_long),
                    ("right", ctypes.c_long),
                    ("bottom", ctypes.c_long)]
    rect = RECT()
    SPI_GETWORKAREA = 0x0030
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect.left, rect.top, rect.right, rect.bottom

# === Optional Font Download (future use)
def download_montserrat():
    font_url = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Regular.ttf"
    font_path = os.path.join(tempfile.gettempdir(), "Montserrat-Regular.ttf")
    if not os.path.exists(font_path):
        urllib.request.urlretrieve(font_url, font_path)
        ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)

# === Rounded Rectangle Drawing Function ===
def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

# === Save/load widget positions ===
def load_positions():
    if os.path.exists(POS_FILE):
        try:
            with open(POS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_positions(pos_dict):
    with open(POS_FILE, 'w') as f:
        json.dump(pos_dict, f)

def clear_positions_and_exit():
    if os.path.exists(POS_FILE):
        os.remove(POS_FILE)
    os._exit(0)

# === Widget Class ===
class DesktopRectangle:
    def __init__(self, name, width, x, y, color):
        self.name = name
        self.width = width
        self.height = RECT_HEIGHT
        self.color = color
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="white")
        self.root.wm_attributes("-transparentcolor", "white")
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="white", highlightthickness=0)
        self.canvas.pack()
        round_rectangle(self.canvas, 0, 0, self.width, self.height, radius=RECT_RADIUS, fill=color)

        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        self.root.bind("<Control-Alt-Shift-X>", lambda e: clear_positions_and_exit())

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = event.x_root - self._x
        y = event.y_root - self._y
        self.root.geometry(f"+{x}+{y}")
        positions[self.name] = {"x": x, "y": y}
        save_positions(positions)

    def run(self):
        self.root.mainloop()

# === Main Run ===
if __name__ == "__main__":
    threading.Thread(target=download_montserrat).start()
    positions = load_positions()
    left, top, right, bottom = get_work_area()

    # Defaults if no saved positions
    default1 = {"x": left + 20, "y": bottom - RECT_HEIGHT - 20}
    default2 = {"x": right - RECT_WIDTH_2 - 20, "y": bottom - RECT_HEIGHT - 20}

    pos1 = positions.get("widget1", default1)
    pos2 = positions.get("widget2", default2)

    widget1 = DesktopRectangle("widget1", RECT_WIDTH_1, pos1["x"], pos1["y"], RECT_COLOR)
    widget2 = DesktopRectangle("widget2", RECT_WIDTH_2, pos2["x"], pos2["y"], "#0064e4")

    threading.Thread(target=widget1.run).start()
    widget2.run()
