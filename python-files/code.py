#i don't use any external libraries i just use built in libraries
import hashlib
import os
import sys
import time

LOG_FILE = "feistel_cipher.log"
BLOCK_SIZE = 16
KEY_FILE = "feistel_key.txt"

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.ctime()}: {message}\n")

def derive_round_keys(master_key: bytes, num_rounds: int = 3):
    return [hashlib.sha256(master_key + bytes([i])).digest() for i in range(num_rounds)]

def feistel_function(data: bytes, key: bytes) -> bytes:
    return bytes(d ^ k for d, k in zip(data, key[:len(data)]))

def feistel_encrypt_block(block: bytes, round_keys: list) -> bytes:
    half = len(block) // 2
    left, right = block[:half], block[half:]
    for key in round_keys:
        f = feistel_function(right, key)
        left, right = right, bytes(l ^ f1 for l, f1 in zip(left, f))
    return left + right

def feistel_decrypt_block(block: bytes, round_keys: list) -> bytes:
    half = len(block) // 2
    left, right = block[:half], block[half:]
    for key in reversed(round_keys):
        f = feistel_function(left, key)
        right, left = left, bytes(r ^ f1 for r, f1 in zip(right, f))
    return left + right

def pad(data: bytes) -> bytes:
    return data + b'\x00' * ((BLOCK_SIZE - len(data) % BLOCK_SIZE) % BLOCK_SIZE)

def encrypt(data: bytes, key: bytes) -> bytes:
    data = pad(data)
    round_keys = derive_round_keys(key)
    result = b''
    for i in range(0, len(data), BLOCK_SIZE):
        result += feistel_encrypt_block(data[i:i+BLOCK_SIZE], round_keys)
    return result

def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    round_keys = derive_round_keys(key)
    result = b''
    for i in range(0, len(ciphertext), BLOCK_SIZE):
        result += feistel_decrypt_block(ciphertext[i:i+BLOCK_SIZE], round_keys)
    return result.rstrip(b'\x00')

def save_key_to_file(key: bytes, filename: str = KEY_FILE):
    with open(filename, "w") as f:
        f.write(key.hex())
    print(f"[+] Key saved to {filename}")
    log(f"Key saved to {filename}")

def load_key_from_file(filename: str = KEY_FILE) -> bytes:
    with open(filename, "r") as f:
        return bytes.fromhex(f.read().strip())

def read_file(filepath: str) -> bytes:
    with open(filepath, "rb") as f:
        return f.read()

def write_file(filepath: str, data: bytes):
    with open(filepath, "wb") as f:
        f.write(data)

def get_user_key() -> bytes:
    """
    Accept any user input as key. Encode to UTF-8. Generate secure key if blank.
    """
    key_input = input("Enter a key (any characters allowed). Leave blank to generate one: ").strip()
    if key_input:
        try:
            key = key_input.encode("utf-8")
            if len(key) < 8:
                print("[!] Warning: Key is short. For better security, use 8+ characters.")
            print(f"[+] Your key (hex): {key.hex()}")
            return key
        except Exception as e:
            print(f"[!] Encoding error: {e}")
            return os.urandom(16)
    else:
        key = os.urandom(16)
        print(f"[+] Generated secure key (hex): {key.hex()}")
        save_key_to_file(key)
        return key

def get_decryption_key() -> bytes:
    key_input = input("Enter decryption key (hex or plain text, or leave blank to load from file): ").strip()
    if not key_input:
        return load_key_from_file()

    try:
        if all(c in "0123456789abcdefABCDEF" for c in key_input) and len(key_input) % 2 == 0:
            return bytes.fromhex(key_input)
        else:
            return key_input.encode("utf-8")
    except Exception as e:
        print(f"[!] Invalid key input: {e}")
        return None

def encrypt_text_mode():
    plaintext = input("Enter the plaintext: ").encode()
    key = get_user_key()
    encrypted = encrypt(plaintext, key)
    print(f"Encrypted (hex): {encrypted.hex()}")
    log("Encrypted text")

def decrypt_text_mode():
    hex_input = input("Enter ciphertext (hex): ").strip()
    try:
        ciphertext = bytes.fromhex(hex_input)
        key = get_decryption_key()
        decrypted = decrypt(ciphertext, key)
        print(f"Decrypted message: {decrypted.decode(errors='replace')}")
        log("Decrypted text")
    except Exception as e:
        print(f"[!] Decryption error: {e}")
        log(f"Decryption failed: {e}")

def encrypt_file_mode():
    path = input("Enter the file path to encrypt: ").strip()
    if not os.path.exists(path):
        print("[!] File not found.")
        return

    key = get_user_key()
    data = read_file(path)
    encrypted = encrypt(data, key)

    out_path = path + ".enc"
    write_file(out_path, encrypted)
    print(f"[+] Encrypted file saved to {out_path}")
    log(f"Encrypted file {path} -> {out_path}")

def decrypt_file_mode():
    path = input("Enter the encrypted file path: ").strip()
    if not os.path.exists(path):
        print("[!] File not found.")
        return

    key = get_decryption_key()

    try:
        data = read_file(path)
        decrypted = decrypt(data, key)

        out_path = path.replace(".enc", ".dec")
        write_file(out_path, decrypted)
        print(f"[+] Decrypted file saved to {out_path}")
        log(f"Decrypted file {path} -> {out_path}")
    except Exception as e:
        print(f"[!] Error: {e}")
        log(f"Decryption failed: {e}")

def main_menu():
    while True:
        print("\n====== Feistel Cipher Tool ======")
        print("1. Encrypt Text")
        print("2. Decrypt Text")
        print("3. Encrypt File")
        print("4. Decrypt File")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            encrypt_text_mode()
        elif choice == '2':
            decrypt_text_mode()
        elif choice == '3':
            encrypt_file_mode()
        elif choice == '4':
            decrypt_file_mode()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("[!] Invalid option. Try again.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n[!] Interrupted. Exiting.")
        sys.exit(0)
