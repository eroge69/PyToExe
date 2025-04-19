import os, base64, sys

def god_curse():
    print("\033[91mПечать Ауриэля нарушена! Данные уничтожаются...\033[0m")
    [os.remove(f) for f in os.listdir() if f.endswith(('.enc', '.key'))]
    sys.exit(666)

def decrypt(key):
    if key != "AURIEL":
        god_curse()
    with open("secret.enc", "rb") as f:
        data = base64.b64decode(f.read())
    print("Послание:", bytes([d ^ 0x77 for d in data]).decode())

if __name__ == "__main__":
    decrypt(input("Введите священное имя: ").strip().upper())