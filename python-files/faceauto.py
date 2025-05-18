import cv2
import mediapipe as mp
import time
import subprocess
import threading
from plyer import notification
import pystray
from PIL import Image, ImageDraw
import os
import sys
import shutil

# MediaPipe face detection setup
mp_face = mp.solutions.face_detection
face_detection = mp_face.FaceDetection(min_detection_confidence=0.6)

# Webcam setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

face_last_seen = time.time()
locked = False
notified = False
LOCK_DELAY = 5  # seconds

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=2
    )

def monitor():
    global face_last_seen, locked, notified

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb)

        if results.detections:
            face_last_seen = time.time()
            locked = False
            notified = False
        else:
            if not locked and time.time() - face_last_seen > LOCK_DELAY:
                if not notified:
                    show_notification("Locking", "No face detected. Locking in 5 seconds...")
                    notified = True
                    # Wait 5 seconds, but check for face during this period
                    for _ in range(10):  # 10 x 0.5s = 5s
                        time.sleep(0.5)
                        ret, frame = cap.read()
                        if not ret:
                            continue
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        results = face_detection.process(rgb)
                        if results.detections:
                            # Face detected again, cancel lock
                            notified = False
                            break
                    else:
                        # Only lock if face was not detected during the wait
                        subprocess.call("rundll32.exe user32.dll,LockWorkStation")
                        locked = True

        time.sleep(0.5)

def quit_app(icon, item):
    icon.stop()
    cap.release()

def turn_off_autostart(icon, item):
    remove_from_startup()
    show_notification("FaceLock", "Auto-start disabled.")

def tray_icon():
    img = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(img)
    draw.ellipse((16, 16, 48, 48), fill='blue')

    menu = pystray.Menu(
        pystray.MenuItem("Turn Off Auto-Start", turn_off_autostart),
        pystray.MenuItem("Quit", quit_app)
    )
    icon = pystray.Icon("FaceLock", img, "FaceLock Running", menu)

    threading.Thread(target=monitor, daemon=True).start()
    icon.run()

def get_startup_folder():
    return os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")

def get_script_shortcut_path():
    startup_folder = get_startup_folder()
    return os.path.join(startup_folder, "FaceLock.lnk")

def add_to_startup():
    import winshell
    from win32com.client import Dispatch
    shortcut_path = get_script_shortcut_path()
    target = sys.executable
    script = os.path.abspath(__file__)
    # Use pythonw.exe for no console window
    if target.endswith("python.exe"):
        target = target.replace("python.exe", "pythonw.exe")
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target
    shortcut.Arguments = f'"{script}"'
    shortcut.WorkingDirectory = os.path.dirname(script)
    shortcut.IconLocation = script
    shortcut.save()

def remove_from_startup():
    shortcut_path = get_script_shortcut_path()
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)

if __name__ == "__main__":
    add_to_startup()
    tray_icon()
