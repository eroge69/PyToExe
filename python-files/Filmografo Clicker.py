import os
import sys
import subprocess
from ctypes import windll, WinDLL
from random import getrandbits, uniform, randint
from threading import Thread
from time import sleep
from pynput.keyboard import KeyCode, Listener as KeyboardListener
from pynput.mouse import Button, Controller, Listener as MouseListener
from colorama import Fore, Style, init

init(autoreset=True)

GWL_STYLE = -16
WS_MAXIMIZEBOX = 0x00010000
WS_SIZEBOX = 0x00040000

kernel32 = windll.kernel32
user32 = windll.user32
WinMM = WinDLL("winmm")
WinMM.timeBeginPeriod(15)
kernel32.SetThreadPriority(kernel32.GetCurrentThread(), 31)

logo: str = """
   █████▒██▓ ██▓     ███▄ ▄███▓ ▒█████    ▄████  ██▀███   ▄▄▄        █████▒▒█████  
 ▓██   ▒▓██▒▓██▒    ▓██▒▀█▀ ██▒▒██▒  ██▒ ██▒ ▀█▒▓██ ▒ ██▒▒████▄    ▓██   ▒▒██▒  ██▒
 ▒████ ░▒██▒▒██░    ▓██    ▓██░▒██░  ██▒▒██░▄▄▄░▓██ ░▄█ ▒▒██  ▀█▄  ▒████ ░▒██░  ██▒
 ░▓█▒  ░░██░▒██░    ▒██    ▒██ ▒██   ██░░▓█  ██▓▒██▀▀█▄  ░██▄▄▄▄██ ░▓█▒  ░▒██   ██░
 ░▒█░   ░██░░██████▒▒██▒   ░██▒░ ████▓▒░░▒▓███▀▒░██▓ ▒██▒ ▓█   ▓██▒░▒█░   ░ ████▓▒░
  ▒ ░   ░▓  ░ ▒░▓  ░░ ▒░   ░  ░░ ▒░▒░▒░  ░▒   ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░ ▒ ░   ░ ▒░▒░▒░ 
  ░      ▒ ░░ ░ ▒  ░░  ░      ░  ░ ▒ ▒░   ░   ░   ░▒ ░ ▒░  ▒   ▒▒ ░ ░       ░ ▒ ▒░ 
  ░ ░    ▒ ░  ░ ░   ░      ░   ░ ░ ░ ▒  ░ ░   ░   ░░   ░   ░   ▒    ░ ░   ░ ░ ░ ▒  
         ░      ░  ░       ░       ░ ░        ░    ░           ░  ░           ░ ░
""".center(43)

def clear_and_logo():
    os.system("cls")
    os.system("mode 84,17")
    print(Fore.RED + logo + Style.RESET_ALL)

def introduction():
    kernel32.SetConsoleTitleW("Filmografo Clicker")
    hwnd = kernel32.GetConsoleWindow()
    style = user32.GetWindowLongW(hwnd, GWL_STYLE)
    user32.SetWindowLongW(hwnd, GWL_STYLE, style & ~WS_MAXIMIZEBOX & ~WS_SIZEBOX)

    while True:
        clear_and_logo()
        try:
            click_choice = input(" [CLICK-BUTTON] Left (s) / Right (d) > ").lower()
            if click_choice == "s":
                button = Button.left
            elif click_choice == "d":
                button = Button.right
            else:
                continue

            user_cps = float(input(" [CPS] > "))
            toggle_key = input(" [TOGGLE-KEY] > ")
            reset_key = input(" [RESET-KEY] > ")
            if len(toggle_key) != 1 or len(reset_key) != 1:
                continue
            toggle_key = KeyCode(char=toggle_key.lower())
            reset_key = KeyCode(char=reset_key.lower())
        except ValueError:
            continue
        else:
            return 0.5 / user_cps * 800, toggle_key, reset_key, int(user_cps), button

cps, toggle_key, reset_key, raw_cps, click_button = introduction()

def get_randomisation(base, depressed: bool):
    randomisation = []

    def get_delay(base_delay, high=False, low=False) -> float:
        if high:
            return base_delay * uniform(1.1, 1.5) / 1000
        elif low:
            return base_delay * uniform(0.8, 1.0) / 1000
        else:
            return (base_delay + getrandbits(4)) / randint(800, 1000)

    fatigue = 0
    cycle_duration = raw_cps * (16 if depressed else 26)

    for iteration in range(cycle_duration):
        if fatigue > 0:
            randomisation.append(get_delay(base, high=True))
            fatigue -= 1
        elif fatigue < 0:
            randomisation.append(get_delay(base, low=True))
            fatigue += 1
        else:
            if iteration % raw_cps == 0:
                fatigue += randint(-5, 5)

            randomisation.append(get_delay(base))

    return iter(randomisation)

class Filmografo(Thread):
    def __init__(self):
        super().__init__()
        self.mouse = Controller()
        self.button = click_button
        self.toggleable = False
        self.running = True
        self.held = False
        self.cycles = 0
        self.pattern = get_randomisation(cps, False)
        self.keymap = {
            toggle_key: self.toggle,
            reset_key: self.reset
        }

    def regenerate(self):
        depressed = self.cycles % 2 == 0
        offset = 0.5 / raw_cps * (1000 if depressed else 800)
        self.pattern = get_randomisation(offset, depressed)
        self.cycles += 1

    def toggle(self):
        self.held = False
        self.toggleable = not self.toggleable
        if self.toggleable:
            print(Fore.GREEN + " [STATUS] Attivo     " + Style.RESET_ALL, end="\r")
        else:
            print(Fore.RED + " [STATUS] Disattivato" + Style.RESET_ALL, end="\r")
            self.regenerate()

    def reset(self):
        try:
            script_path = os.path.abspath(sys.argv[0])
            subprocess.Popen([sys.executable, script_path, *sys.argv[1:]])
            os._exit(0)
        except Exception as e:
            print(Fore.RED + f"[ERRORE RESET] {e}" + Style.RESET_ALL)

    def on_click(self, _, __, button, ___):
        if self.toggleable and button == self.button:
            self.held = not self.held

    def on_press(self, key):
        action = self.keymap.get(key)
        if action:
            action()

    def run(self):
        while self.running:
            while self.held:
                try:
                    delay = next(self.pattern)
                except StopIteration:
                    self.regenerate()
                    delay = next(self.pattern)

                self.mouse.press(self.button)
                sleep(delay)
                self.mouse.release(self.button)
                sleep(delay)
            sleep(0.1)

click_thread = Filmografo()
mouse_handler = MouseListener(on_click=click_thread.on_click)
keyboard_handler = KeyboardListener(on_press=click_thread.on_press)

click_thread.start()
mouse_handler.start()
keyboard_handler.start()