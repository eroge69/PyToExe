import os
import win32gui
import win32con
import keyboard
import threading

WINDOW_TITLE_KEYWORD = "Chrome"
OPACITY_STEP = 5
MIN_OPACITY = 0
MAX_OPACITY = 255

current_opacity = MAX_OPACITY
hwnd = None

def find_chrome_window():
    def callback(hwnd, result):
        if win32gui.IsWindowVisible(hwnd) and WINDOW_TITLE_KEYWORD in win32gui.GetWindowText(hwnd):
            result.append(hwnd)
    result = []
    win32gui.EnumWindows(callback, result)
    return result[0] if result else None

def set_window_opacity(opacity):
    global hwnd
    if hwnd is None:
        hwnd = find_chrome_window()
    if hwnd is None:
        print("No Chrome window found.")
        return
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    if not (ex_style & win32con.WS_EX_LAYERED):
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, opacity, win32con.LWA_ALPHA)

def increase_opacity():
    global current_opacity
    current_opacity = min(current_opacity + OPACITY_STEP, MAX_OPACITY)
    set_window_opacity(current_opacity)

def decrease_opacity():
    global current_opacity
    current_opacity = max(current_opacity - OPACITY_STEP, MIN_OPACITY)
    set_window_opacity(current_opacity)

def zero_opacity():
    global current_opacity
    current_opacity = 0
    set_window_opacity(current_opacity)

def bring_to_front():
    global hwnd
    if hwnd is None:
        hwnd = find_chrome_window()
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restore first
        win32gui.SetForegroundWindow(hwnd)
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)  # Then maximize

def send_to_back():
    global hwnd
    if hwnd is None:
        hwnd = find_chrome_window()
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
def force_exit():
    os._exit(0)

def main():
    global hwnd
    hwnd = find_chrome_window()
    if hwnd is None:
        print("No Chrome window found.")
    else:
        print("Chrome window found. Ready!")

    keyboard.add_hotkey('ctrl+alt+up', increase_opacity)
    keyboard.add_hotkey('ctrl+alt+down', decrease_opacity)
    keyboard.add_hotkey('ctrl+alt+right', bring_to_front)
    keyboard.add_hotkey('ctrl+alt+left', send_to_back)
    keyboard.add_hotkey('ctrl+alt+0', zero_opacity)
    keyboard.add_hotkey('ctrl+alt+esc', force_exit)

    print("Shortcuts:")
    print("- CTRL + ALT + UP: Increase opacity")
    print("- CTRL + ALT + DOWN: Decrease opacity")
    print("- CTRL + ALT + RIGHT: Bring to front (keep maximized)")
    print("- CTRL + ALT + LEFT: Send to back")
    print("- CTRL + ALT + 0: Set opacity to 0 (invisible)")
    print("- CTRL + ALT + ESC: Exit")

    keyboard.wait('ctrl+alt+esc')

if __name__ == "__main__":
    threading.Thread(target=main).start()
