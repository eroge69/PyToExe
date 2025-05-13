import keyboard
import pystray
import threading
from PIL import Image
import win32gui
import win32con
import time
import sys

# Configuration
GAME_WINDOW_CLASS = "Valve001"  # CS2 window class
KEY_GROUPS = {
    "horizontal": ["a", "d"],
    "vertical": ["w", "s"]
}
CHAT_MODE_KEY = "t"  # Key to detect chat mode
POLL_RATE = 0.001  # Polling rate in seconds

class SnapTap:
    def __init__(self):
        self.enabled = True
        self.icon = None
        self.active_group_states = {group: None for group in KEY_GROUPS}
        self.chat_mode = False
        self.game_active = False

    def is_game_active(self):
        foreground_window = win32gui.GetForegroundWindow()
        window_class = win32gui.GetClassName(foreground_window)
        return window_class == GAME_WINDOW_CLASS

    def handle_key_event(self):
        while self.enabled:
            if not self.is_game_active():
                self.game_active = False
                time.sleep(POLL_RATE)
                continue
            self.game_active = True

            # Check for chat mode
            if keyboard.is_pressed(CHAT_MODE_KEY):
                self.chat_mode = True
                time.sleep(0.1)
                continue
            else:
                self.chat_mode = False

            if self.chat_mode:
                time.sleep(POLL_RATE)
                continue

            # Process key groups
            for group, keys in KEY_GROUPS.items():
                pressed_key = None
                for key in keys:
                    if keyboard.is_pressed(key):
                        pressed_key = key
                        break

                if pressed_key and pressed_key != self.active_group_states[group]:
                    # Release previous key in group
                    if self.active_group_states[group]:
                        keyboard.release(self.active_group_states[group])
                    # Update state
                    self.active_group_states[group] = pressed_key

                # If no key is pressed, release active key
                if not pressed_key and self.active_group_states[group]:
                    keyboard.release(self.active_group_states[group])
                    self.active_group_states[group] = None

            time.sleep(POLL_RATE)

    def create_system_tray(self):
        # Create a simple icon (white square for demonstration)
        image = Image.new("RGB", (64, 64), color="white")
        menu = (
            pystray.MenuItem("Enable SnapTap", self.toggle_enabled, checked=lambda item: self.enabled),
            pystray.MenuItem("Exit", self.exit)
        )
        self.icon = pystray.Icon("SnapTap", image, "SnapTap", menu)

    def toggle_enabled(self):
        self.enabled = not self.enabled
        if self.icon:
            self.icon.notify(f"SnapTap {'Enabled' if self.enabled else 'Disabled'}", "SnapTap")

    def exit(self):
        self.enabled = False
        if self.icon:
            self.icon.stop()
        sys.exit()

    def run(self):
        # Start system tray in a separate thread
        tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        tray_thread.start()
        # Start key handling
        self.handle_key_event()

if __name__ == "__main__":
    snap_tap = SnapTap()
    snap_tap.create_system_tray()
    snap_tap.run()