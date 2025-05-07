from pynput import keyboard

pressed_keys = set()
controller = keyboard.Controller()

def on_press(key):
    try:
        if key.char in ['a', 'd']:
            if key.char == 'a' and 'd' in pressed_keys:
                controller.release('d')
                pressed_keys.discard('d')
            elif key.char == 'd' and 'a' in pressed_keys:
                controller.release('a')
                pressed_keys.discard('a')
            pressed_keys.add(key.char)
    except AttributeError:
        pass

def on_release(key):
    try:
        if key.char in ['a', 'd']:
            pressed_keys.discard(key.char)
    except AttributeError:
        pass

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("Snap Tap is active (A/D). Press ESC to exit.")
    listener.join()
