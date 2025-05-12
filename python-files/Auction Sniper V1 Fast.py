import time, random, os
import pyautogui
from PIL import ImageGrab
import winsound
import configparser

# ───── LOAD CONFIG ─────
cfg = configparser.ConfigParser()
cfg.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

# Detection settings
PIXEL_X        = cfg.getint('Detection', 'pixel_x')
PIXEL_Y        = cfg.getint('Detection', 'pixel_y')
CAR_COLOR      = tuple(map(int, cfg.get('Detection', 'car_color').split(',')))
REGION_SIZE    = cfg.getint('Detection', 'region_size')
THRESHOLD      = cfg.getint('Detection', 'match_threshold')

# Timing settings
T       = lambda name: cfg.getfloat('Timing', name)
JITTER  = cfg.getfloat('Timing', 'jitter')

START_DELAY       = T('start_delay')
POST_SEARCH_DELAY = T('post_search_delay')
WAIT_BEFORE_BUY   = T('wait_before_buy')
BUY_NAV_DELAY     = T('buy_nav_delay')
POST_BUY_DELAY    = T('post_buy_delay')
BACK_DELAY        = T('back_delay')

def rand_sleep(base):
    """Sleep for base ± uniform(0, JITTER)."""
    delay = base + random.uniform(-JITTER, JITTER)
    time.sleep(max(0, delay))

# ───── ACTION FUNCTIONS ─────

def do_search():
    pyautogui.press('esc');   rand_sleep(BACK_DELAY)
    pyautogui.press('enter'); rand_sleep(BACK_DELAY)
    pyautogui.press('enter'); rand_sleep(POST_SEARCH_DELAY)

def check_for_car():
    half = REGION_SIZE // 2
    matches = 0
    # sample REGION_SIZE × REGION_SIZE around the center
    img = ImageGrab.grab(bbox=(
        PIXEL_X - half, PIXEL_Y - half,
        PIXEL_X + half + 1, PIXEL_Y + half + 1
    ))
    for x in range(REGION_SIZE):
        for y in range(REGION_SIZE):
            if img.getpixel((x, y)) == CAR_COLOR:
                matches += 1
                if matches >= THRESHOLD:
                    return True
    return False

def do_buyout():
    winsound.Beep(1000, 500)
    rand_sleep(WAIT_BEFORE_BUY)
    pyautogui.press('y');        rand_sleep(BUY_NAV_DELAY)
    pyautogui.press('down');     rand_sleep(BUY_NAV_DELAY)
    pyautogui.press('enter');    rand_sleep(BUY_NAV_DELAY)
    pyautogui.press('enter');    rand_sleep(POST_BUY_DELAY)

def backout_and_restart():
    pyautogui.press('enter'); rand_sleep(BACK_DELAY)
    pyautogui.press('esc');   rand_sleep(BACK_DELAY)
    pyautogui.press('esc');   rand_sleep(BACK_DELAY)
    pyautogui.press('enter'); rand_sleep(BACK_DELAY)
    pyautogui.press('enter'); rand_sleep(POST_SEARCH_DELAY)

# ───── MAIN LOOP ─────

def main():
    print(f"Waiting {START_DELAY}s to let you switch to FH5…")
    time.sleep(START_DELAY)
    do_search()
    while True:
        if check_for_car():
            print("Car detected! Executing buyout…")
            do_buyout()
            backout_and_restart()
        else:
            do_search()

if __name__ == "__main__":
    main()