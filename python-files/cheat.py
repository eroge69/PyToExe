import dearpygui.dearpygui as dpg
import json
import os
import subprocess
import threading
import keyboard
import sys
import time
import pyautogui

# Get base directory of the script
BASE_DIR = os.path.dirname(__file__)
REQ_DIR = os.path.join(BASE_DIR, "req")

# Correct paths
SETTINGS_PATH = os.path.join(REQ_DIR, "configuration.json")
VERF_PATH = os.path.join(BASE_DIR, "verf.txt")
MEDAL_EXE_PATH = os.path.join(REQ_DIR, "Medal.exe")

# Default settings structure
DEFAULT_SETTINGS = {
    "Configuration": {
        "Binds": {
            "Keybind": "RButton",
            "Pause": "Esc",
            "Reload": "R"
        },
        "Color": {
            "Saturation": 10
        },
        "Bezier": {
            "LinearCurveX": 0.350,
            "LinearCurveY": 0.200
        },
        "Easing": {
            "SmoothnessX": 100,
            "SmoothnessY": 120,
            "SmoothingReplicatorX": 5,
            "SmoothingReplicatorY": 5,
            "SmoothingDividerX": 250,
            "SmoothingDividerY": 250,
            "Prediction": {
                "Enabled": False,
                "Mode": "Ideal",
                "PredictionX": 5,
                "PredictionY": 8
            }
        },
        "Misc": {
            "AimbotUpdateTick": 600,
            "AimbotUpdateMS": 1000,
            "CameraToGunFOV": 85,
            "FlickTime": 2
        },
        "FOV": {
            "FOVOffsetX": 5,
            "FOVOffsetY": 5
        }
    }
}

# Exit if verf.txt not present
if not os.path.exists(VERF_PATH):
    sys.exit()
os.remove(VERF_PATH)

def merge_settings(default, custom):
    result = default.copy()
    for key, value in custom.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_settings(result[key], value)
            else:
                result[key] = value
        else:
            result[key] = value
    return result

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            loaded = json.load(f)
            return merge_settings(DEFAULT_SETTINGS, loaded)
    return DEFAULT_SETTINGS.copy()

def save_settings():
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=4)

def run_ahk_script():
    subprocess.run([MEDAL_EXE_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def unload_script():
    try:
        subprocess.run(["taskkill", "/f", "/im", "Medal.exe"], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pass
    dpg.stop_dearpygui()
    sys.exit()

settings = load_settings()

restart_timer = None
restart_lock = threading.Lock()

def schedule_restart():
    global restart_timer

    def restart():
        time.sleep(0.2)
        with restart_lock:
            try:
                subprocess.run(["taskkill", "/f", "/im", "Medal.exe"], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                pass
            time.sleep(0.5)
            run_ahk_script()

    with restart_lock:
        if restart_timer and restart_timer.is_alive():
            restart_timer.cancel()
        restart_timer = threading.Timer(0.2, restart)
        restart_timer.start()

def update_setting(sender, app_data, user_data):
    section, key = user_data
    if section == "Prediction":
        settings["Configuration"]["Easing"]["Prediction"][key] = app_data
    else:
        settings["Configuration"][section][key] = app_data
    save_settings()
    schedule_restart()

panic_key = "F12"
panic_enabled = False

def panic_key_listener():
    while True:
        if panic_enabled and keyboard.is_pressed(panic_key):
            unload_script()
            break
        time.sleep(0.01)

panic_thread = threading.Thread(target=panic_key_listener, daemon=True)
panic_thread.start()

def set_panic_key(sender, app_data):
    global panic_key
    panic_key = app_data

# --- UI Setup ---

dpg.create_context()

with dpg.theme() as Default_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (25, 25, 25), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (20, 20, 20), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (220, 220, 220), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (185, 185, 185), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 60, 60), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 80, 80), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (100, 100, 100), category=dpg.mvThemeCat_Core)

with dpg.theme() as shinigami_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (80, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (100, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (60, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (150, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (150, 20, 20), category=dpg.mvThemeCat_Core)

def create_ui():
    dpg.create_viewport(title='Spotify App', width=625, height=475)

    with dpg.window(label="ecstasy.wtf | Beta Rebrand", width=625, height=475, no_move=True):
        with dpg.collapsing_header(label="Aim Assist", default_open=True):
            dpg.add_input_text(label="Keybind", default_value=settings["Configuration"]["Binds"]["Keybind"],
                               callback=update_setting, user_data=("Binds", "Keybind"))
            dpg.add_slider_int(label="Saturation", min_value=0, max_value=100,
                               default_value=settings["Configuration"]["Color"]["Saturation"],
                               callback=update_setting, user_data=("Color", "Saturation"))
            dpg.add_slider_int(label="SmoothnessX", min_value=0, max_value=500,
                               default_value=settings["Configuration"]["Easing"]["SmoothnessX"],
                               callback=update_setting, user_data=("Easing", "SmoothnessX"))
            dpg.add_slider_int(label="SmoothnessY", min_value=0, max_value=500,
                               default_value=settings["Configuration"]["Easing"]["SmoothnessY"],
                               callback=update_setting, user_data=("Easing", "SmoothnessY"))

            prediction = settings["Configuration"]["Easing"]["Prediction"]
            dpg.add_checkbox(label="Prediction Enabled", default_value=prediction["Enabled"],
                             callback=update_setting, user_data=("Prediction", "Enabled"))
            dpg.add_combo(label="Prediction Mode", items=["Ideal", "Advanced"],
                          default_value=prediction["Mode"],
                          callback=update_setting, user_data=("Prediction", "Mode"))
            dpg.add_slider_int(label="PredictionX", min_value=0, max_value=50,
                               default_value=prediction["PredictionX"],
                               callback=update_setting, user_data=("Prediction", "PredictionX"))
            dpg.add_slider_int(label="PredictionY", min_value=0, max_value=50,
                               default_value=prediction["PredictionY"],
                               callback=update_setting, user_data=("Prediction", "PredictionY"))

            dpg.add_slider_int(label="FOVOffsetX", min_value=-100, max_value=100,
                               default_value=settings["Configuration"]["FOV"]["FOVOffsetX"],
                               callback=update_setting, user_data=("FOV", "FOVOffsetX"))
            dpg.add_slider_int(label="FOVOffsetY", min_value=-100, max_value=100,
                               default_value=settings["Configuration"]["FOV"]["FOVOffsetY"],
                               callback=update_setting, user_data=("FOV", "FOVOffsetY"))

        with dpg.collapsing_header(label="Exploits", default_open=False):
            dpg.add_text("This section is currently under development. xoxo")
            dpg.add_spacer(height=10)

        with dpg.collapsing_header(label="Misc", default_open=False):
            def toggle_panic(sender, app_data):
                global panic_enabled
                panic_enabled = app_data

            dpg.add_checkbox(label="Enable Panic Key", callback=toggle_panic)
            dpg.add_input_text(label="Panic Keybind", default_value="F12", callback=set_panic_key)

            def toggle_theme(sender, app_data):
                if app_data == "Default":
                    dpg.bind_theme(Default_theme)
                elif app_data == "Shinigami":
                    dpg.bind_theme(shinigami_theme)
                elif app_data == "ImGui":
                    dpg.bind_theme(0)

            dpg.add_spacer(height=10)
            dpg.add_combo(label="Select Theme", items=["Default", "Shinigami", "ImGui"], default_value="Default", callback=toggle_theme)

            dpg.add_spacer(height=10)
            dpg.add_button(label="Unload", callback=unload_script)
            dpg.add_button(label="Hide UI", callback=lambda: sys.exit())

    dpg.bind_theme(Default_theme)
    dpg.setup_dearpygui()
    dpg.set_viewport_decorated(False)
    dpg.set_viewport_clear_color((0, 0, 0, 0))
    dpg.show_viewport()
    dpg.start_dearpygui()

create_ui()
