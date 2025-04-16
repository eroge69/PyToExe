import tkinter as tk
from tkinter import scrolledtext
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import time, pickle, threading

FILENAME = 'actions.pkl'
actions = []
recording = False
start_time = None

mouse_listener = None
keyboard_listener = None

# ========== Функции для записи ==========
def timestamp():
    return time.time() - start_time

def log(text):
    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)

def on_move(x, y):
    if recording:
        actions.append(('move', timestamp(), x, y))

def on_click(x, y, button, pressed):
    if recording:
        actions.append(('click', timestamp(), x, y, button.name, pressed))

def on_scroll(x, y, dx, dy):
    if recording:
        actions.append(('scroll', timestamp(), x, y, dx, dy))

def on_press(key):
    global recording
    if recording:
        actions.append(('key_press', timestamp(), str(key)))
        if key == Key.esc:
            stop_recording()

def on_release(key):
    if recording:
        actions.append(('key_release', timestamp(), str(key)))

def start_recording():
    global recording, actions, start_time, mouse_listener, keyboard_listener
    actions = []
    start_time = time.time()
    recording = True
    log("🟢 Запись началась... Нажмите ESC для остановки")

    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

    mouse_listener.start()
    keyboard_listener.start()

def stop_recording():
    global recording
    if not recording:
        return
    recording = False
    mouse_listener.stop()
    keyboard_listener.stop()

    with open(FILENAME, 'wb') as f:
        pickle.dump(actions, f)
    log("⏹️ Запись остановлена и сохранена.")

# ========== Воспроизведение ==========
def playback():
    def run():
        log("▶️ Воспроизведение началось...")
        with open(FILENAME, 'rb') as f:
            actions = pickle.load(f)

        mouse = MouseController()
        keyboard = KeyboardController()

        for i, action in enumerate(actions):
            action_type, t, *data = action
            if i > 0:
                prev_t = actions[i - 1][1]
                time.sleep(t - prev_t)

            if action_type == 'move':
                x, y = data
                mouse.position = (x, y)
            elif action_type == 'click':
                x, y, button, pressed = data
                btn = Button.left if button == 'left' else Button.right
                mouse.position = (x, y)
                if pressed:
                    mouse.press(btn)
                else:
                    mouse.release(btn)
            elif action_type == 'scroll':
                x, y, dx, dy = data
                mouse.position = (x, y)
                mouse.scroll(dx, dy)
            elif action_type == 'key_press':
                key = data[0]
                try:
                    keyboard.press(eval(key))
                except:
                    keyboard.press(key.strip("'"))
            elif action_type == 'key_release':
                key = data[0]
                try:
                    keyboard.release(eval(key))
                except:
                    keyboard.release(key.strip("'"))

        log("✅ Воспроизведение завершено.")

    threading.Thread(target=run).start()

# ========== Интерфейс ==========
window = tk.Tk()
window.title("🖱️ Mouse & Keyboard Recorder")

frame = tk.Frame(window, padx=10, pady=10)
frame.pack()

btn_start = tk.Button(frame, text="Начать запись", command=lambda: threading.Thread(target=start_recording).start(), width=20)
btn_start.grid(row=0, column=0, pady=5)

btn_stop = tk.Button(frame, text="Остановить запись", command=stop_recording, width=20)
btn_stop.grid(row=1, column=0, pady=5)

btn_play = tk.Button(frame, text="Воспроизвести", command=playback, width=20)
btn_play.grid(row=2, column=0, pady=5)

log_box = scrolledtext.ScrolledText(frame, width=50, height=15)
log_box.grid(row=0, column=1, rowspan=3, padx=10)

window.mainloop()
