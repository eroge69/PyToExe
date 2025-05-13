import sys, os, cv2, numpy as np, customtkinter as ctk, mss, threading, json, time, logging, win32gui, win32con, win32ui, pygetwindow as gw
from datetime import datetime
from ultralytics import YOLO
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, Key
import torch

# Gestion des chemins relatifs
def resource_path(relative_path):
    """Obtient le chemin absolu pour script et exécutable."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# Configuration logging
logging.basicConfig(filename=f"aimbot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialisation
mouse = Controller()
model_path = resource_path("yolov8n.pt")  # Placez yolov8n.pt dans le dossier du script
try:
    model = YOLO(model_path)
    device = 'cpu'  # Forcer l'utilisation du CPU
    model.to(device)
    logging.info(f"Modèle YOLO chargé sur {device.upper()}")
except Exception as e:
    logging.error(f"Échec du chargement du modèle YOLO : {e}")
    exit(1)

# État global
running = False
settings_lock = threading.Lock()
settings = {
    "fov": 300, "sensitivity": 0.8, "fps": 30, "speed": 0.1, "smoothing": 0.3, "confidence": 0.5,
    "autofire": False, "esp_enabled": True, "recoil_comp": False, "wallhack_enabled": False,
    "game_title": "Combat Master", "esp_color": (255, 0, 0), "wallhack_color": (0, 255, 255)
}
PROFILES_DIR = resource_path("profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)
last_dx, last_dy = 0, 0

# Gestion des profils
def save_profile(profile_name="default"):
    with settings_lock:
        try:
            with open(os.path.join(PROFILES_DIR, f"{profile_name}.json"), "w") as f:
                json.dump(settings, f, indent=4)
            logging.info(f"Profil '{profile_name}' enregistré")
        except Exception as e:
            logging.error(f"Erreur enregistrement profil : {e}")

def load_profile(profile_name="default"):
    profile_path = os.path.join(PROFILES_DIR, f"{profile_name}.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r") as f:
                with settings_lock:
                    settings.update(json.load(f))
            logging.info(f"Profil '{profile_name}' chargé")
        except Exception as e:
            logging.error(f"Erreur chargement profil : {e}")

def get_profile_list():
    return [f.replace(".json", "") for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]

# Fenêtre de jeu et superposition
def get_game_window_rect():
    with settings_lock:
        title = settings["game_title"]
    try:
        win = gw.getWindowsWithTitle(title)[0]
        if win.isMinimized:
            win.restore()
        return win.left, win.top, win.width, win.height
    except IndexError:
        logging.warning(f"Fenêtre '{title}' non trouvée")
        return 0, 0, 1920, 1080

def create_overlay_window():
    hwnd = win32gui.FindWindow(None, "Aimbot ESP Overlay")
    if not hwnd:
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = lambda hwnd, msg, wparam, lparam: win32con.HTTRANSPARENT if msg == win32con.WM_NCHITTEST else win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
        wc.lpszClassName = "AimbotESPOverlay"
        win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT,
            "AimbotESPOverlay", "Aimbot ESP Overlay", win32con.WS_POPUP,
            0, 0, 1920, 1080, 0, 0, 0, None
        )
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    return hwnd

def draw_overlay(frame, hwnd):
    try:
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        h, w = img.shape[:2]
        hdc = win32gui.GetDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hdc)
        saveDC = mfcDC.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfcDC, w, h)
        saveDC.SelectObject(bitmap)
        saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
        win32gui.UpdateLayeredWindow(hwnd, hdc, None, (w, h), saveDC.GetSafeHdc(), (0, 0), 0, None, win32con.ULW_OPAQUE)
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hdc)
        win32gui.DeleteObject(bitmap.GetHandle())
    except Exception as e:
        logging.error(f"Erreur draw_overlay : {e}")

# Détection et visée
def smooth_aim(dx, dy, smoothing):
    global last_dx, last_dy
    last_dx = last_dx * smoothing + dx * (1 - smoothing)
    last_dy = last_dy * smoothing + dy * (1 - smoothing)
    return last_dx * np.random.uniform(0.95, 1.05), last_dy * np.random.uniform(0.95, 1.05)

def is_target_hidden(frame, x1, y1, x2, y2):
    try:
        roi = frame[int(y1):int(y2), int(x1):int(x2)]
        if roi.size == 0:
            return False
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return len(contours) < 5
    except Exception as e:
        logging.error(f"Erreur is_target_hidden : {e}")
        return False

def detect_targets(hwnd):
    global running, last_dx, last_dy
    sct = mss.mss()
    start_time = time.time()
    while running:
        try:
            with settings_lock:
                fov = settings["fov"]
                sensitivity = settings["sensitivity"]
                fps = settings["fps"]
                speed = settings["speed"]
                smoothing = settings["smoothing"]
                confidence = settings["confidence"]
                autofire = settings["autofire"]
                esp_enabled = settings["esp_enabled"]
                recoil_comp = settings["recoil_comp"]
                wallhack_enabled = settings["wallhack_enabled"]
                esp_color = settings["esp_color"]
                wallhack_color = settings["wallhack_color"]

            left, top, width, height = get_game_window_rect()
            monitor = {"left": left, "top": top, "width": width, "height": height}
            screen = sct.grab(monitor)
            frame = cv2.cvtColor(np.array(screen), cv2.COLOR_RGBA2BGR)
            frame_center = (width // 2, height // 2)

            results = model(frame) if model else []
            best_target = None
            min_distance = float("inf")

            for r in results:
                for box in r.boxes.data.tolist():
                    x1, y1, x2, y2, score, cls = box
                    conf_threshold = confidence if not wallhack_enabled else confidence * 0.8
                    if int(cls) == 0 and score > conf_threshold:
                        cx, cy = int((x1 + x2) / 2), int(y1 + (y2 - y1) / 5)
                        dist = np.linalg.norm(np.array([cx, cy]) - np.array(frame_center))
                        if dist < min_distance and dist < fov:
                            min_distance = dist
                            best_target = (cx, cy)
                        if esp_enabled:
                            is_hidden = wallhack_enabled and is_target_hidden(frame, x1, y1, x2, y2)
                            color = wallhack_color if is_hidden else esp_color
                            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                            cv2.line(frame, frame_center, (cx, cy), (0, 255, 0), 1)

            if best_target:
                dx = (best_target[0] - frame_center[0]) * sensitivity
                dy = (best_target[1] - frame_center[1]) * sensitivity
                if recoil_comp:
                    dy += 5
                dx, dy = smooth_aim(dx, dy, smoothing)
                mouse.move(int(dx * speed), int(dy * speed))
                if autofire:
                    mouse.press(Button.left)
                    time.sleep(np.random.uniform(0.04, 0.06))
                    mouse.release(Button.left)

            if esp_enabled:
                draw_overlay(frame, hwnd)

            time.sleep(max(0, 1 / fps - (time.time() - start_time)))
            start_time = time.time()
        except Exception as e:
            logging.error(f"Erreur détection : {e}")
            time.sleep(0.1)
    sct.close()
    if hwnd:
        win32gui.DestroyWindow(hwnd)

# Interface utilisateur
def update_slider(val, key):
    with settings_lock:
        settings[key] = float(val)
    status_label.configure(text=f"FOV={settings['fov']:.0f}, Sens={settings['sensitivity']:.2f}, FPS={settings['fps']:.0f}")

def toggle():
    global running
    if not running:
        running = True
        hwnd = create_overlay_window()
        threading.Thread(target=detect_targets, args=(hwnd,), daemon=True).start()
        status_label.configure(text="Aimbot : Actif")
        logging.info("Aimbot démarré")
    else:
        running = False
        status_label.configure(text="Aimbot : Arrêté")
        logging.info("Aimbot arrêté")

def toggle_autofire():
    with settings_lock:
        settings["autofire"] = not settings["autofire"]
    logging.info(f"Tir auto : {settings['autofire']}")

def toggle_esp():
    with settings_lock:
        settings["esp_enabled"] = not settings["esp_enabled"]
    logging.info(f"ESP : {settings['esp_enabled']}")

def toggle_recoil():
    with settings_lock:
        settings["recoil_comp"] = not settings["recoil_comp"]
    logging.info(f"Recoil comp : {settings['recoil_comp']}")

def toggle_wallhack():
    with settings_lock:
        settings["wallhack_enabled"] = not settings["wallhack_enabled"]
    logging.info(f"Wallhack : {settings['wallhack_enabled']}")

def on_key_press(key):
    if key == Key.caps_lock:
        toggle()
        return False
    return True

def update_profile_selection(*args):
    profile_name = profile_var.get()
    load_profile(profile_name)
    fov_slider.set(settings["fov"])
    sensitivity_slider.set(settings["sensitivity"])
    fps_slider.set(settings["fps"])
    speed_slider.set(settings["speed"])
    smoothing_slider.set(settings["smoothing"])
    confidence_slider.set(settings["confidence"])
    status_label.configure(text=f"FOV={settings['fov']:.0f}, Sens={settings['sensitivity']:.2f}, FPS={settings['fps']:.0f}")

def on_closing():
    global running
    running = False
    hwnd = win32gui.FindWindow(None, "Aimbot ESP Overlay")
    if hwnd:
        win32gui.DestroyWindow(hwnd)
    app.destroy()

# Configuration UI
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("Aimbot IA + ESP")
app.geometry("450x750")
app.protocol("WM_DELETE_WINDOW", on_closing)

status_label = ctk.CTkLabel(app, text="Aimbot : Arrêté")
status_label.pack(pady=10)

for label, key, from_, to_, default in [
    ("FOV (100-800)", "fov", 100, 800, settings["fov"]),
    ("Sensibilité (0.1-2.0)", "sensitivity", 0.1, 2.0, settings["sensitivity"]),
    ("FPS (5-60)", "fps", 5, 60, settings["fps"]),
    ("Vitesse (0.01-0.5)", "speed", 0.01, 0.5, settings["speed"]),
    ("Lissage (0.0-0.9)", "smoothing", 0.0, 0.9, settings["smoothing"]),
    ("Confiance (0.1-0.9)", "confidence", 0.1, 0.9, settings["confidence"])
]:
    ctk.CTkLabel(app, text=label).pack()
    slider = ctk.CTkSlider(app, from_=from_, to_=to_, command=lambda val, k=key: update_slider(val, k))
    slider.set(default)
    slider.pack(pady=5)

for text, command in [
    ("Tir automatique", toggle_autofire), ("ESP activé", toggle_esp),
    ("Compensation recul", toggle_recoil), ("Wallhack activé", toggle_wallhack)
]:
    ctk.CTkCheckBox(app, text=text, command=command).pack(pady=5)

ctk.CTkLabel(app, text="Profil").pack(pady=5)
profile_var = ctk.StringVar(value="default")
profile_dropdown = ctk.CTkOptionMenu(app, variable=profile_var, values=get_profile_list(), command=update_profile_selection)
profile_dropdown.pack(pady=5)

ctk.CTkButton(app, text="▶ Start/Stop (Caps Lock)", command=toggle).pack(pady=10)
ctk.CTkButton(app, text="💾 Save Profil", command=lambda: save_profile(profile_var.get())).pack(pady=5)
ctk.CTkButton(app, text="📂 Load Profil", command=lambda: load_profile(profile_var.get())).pack(pady=5)

listener = Listener(on_press=on_key_press)
listener.start()
load_profile()
update_profile_selection()
app.mainloop()