import keyboard
import time

# Файл с паролями (каждый пароль на новой строке)
PASSWORD_FILE = "passwords.txt"

def read_passwords():
    try:
        with open(PASSWORD_FILE, 'r') as file:
            passwords = [line.strip() for line in file if line.strip()]
        return passwords
    except FileNotFoundError:
        print(f"Файл {PASSWORD_FILE} не найден. Создайте файл с паролями.")
        return []

passwords = read_passwords()
current_index = 0

def enter_password(password):
    # Небольшая задержка перед вводом, чтобы дать время переключиться на нужное окно
    time.sleep(0.5)
    
    for char in password:
        keyboard.press(char)
        time.sleep(0.05)  # Короткая задержка между нажатиями
        keyboard.release(char)
        time.sleep(0.05)

def on_l_press(event):
    global current_index
    
    if event.name == 'l' and event.event_type == keyboard.KEY_DOWN:
        if not passwords:
            print("Нет паролей для ввода.")
            return
            
        if current_index < len(passwords):
            password = passwords[current_index]
            if len(password) == 4 and password.isdigit():
                enter_password(password)
                print(f"Введён пароль: {password}")
                current_index += 1
            else:
                print(f"Пароль '{password}' не соответствует формату (4 цифры)")
                current_index += 1
        else:
            print("Все пароли использованы. Сброс индекса.")
            current_index = 0

# Регистрируем обработчик нажатия клавиши
keyboard.hook(on_l_press)

print("Программа запущена. Нажмите 'L' для ввода пароля. Нажмите I для выхода.")
print("Пароли будут браться из файла passwords.txt")

# Ожидаем нажатия Esc для выхода
keyboard.wait('I')