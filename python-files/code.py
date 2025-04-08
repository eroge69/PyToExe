import time
import requests
import pyautogui
from urllib.parse import quote

# Логирование
print("ПРИВАТ CREEPER SCRIPT КОНТУРЫ option 10.1")

# Конфигурация Telegram-бота
telegram_bot_token = "7716324496:AAEPKj_FJhroE0im8sk-lu4y2y_ziBIQN98"
chat_id = "5142569647"

# Определение точек
CREEPER = (718, 275)
CREEPE = (740, 297)
CREEP = (1092, 284)
CREE = (608, 654)
CRE = (603, 641)
CR = 1
C = 5723976
creeperso2 = (442, 228)
tiktok = (1136, 63)

subscribe = 70
please = 10

osm = 1  # Если заходит в осмотр или не жмет подтвердить, прибавляйте по 5

# Вспомогательная функция для отправки сообщений в Telegram
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={chat_id}&text={quote(message)}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Ошибка при отправке сообщения в Telegram: {response.text}")
    except Exception as e:
        print(f"Исключение при отправке сообщения в Telegram: {e}")

# Функция для получения цвета пикселя
def get_pixel_color(x, y):
    return pyautogui.pixel(x, y)

# Главный цикл программы
start_time = time.time()
while True:
    # Проверка цвета и клик по creeperso2
    if get_pixel_color(*creeperso2) == C:
        pyautogui.click(creeperso2)
        time.sleep(0.05)

    # Проверка цвета и клик по tiktok
    t1 = get_pixel_color(*tiktok)
    if 5000000 < t1 < 7000001:
        pyautogui.click(tiktok)
        pyautogui.click(creeperso2)
        time.sleep(0.025)
        pyautogui.click(creeperso2)

    # Проверка ошибки покупки скина
    if get_pixel_color(*CRE) == CR:
        pyautogui.click(CRE)
        send_telegram_message("Ошибка покупки скина")

    # Поиск контуров и покупка скина
    for i in range(please):
        offset = i * subscribe
        BRAWL = (CREEPER[0], CREEPER[1] + offset)
        STARS = (CREEPE[0], CREEPE[1] + offset)

        # TODO: Реализация проверки контуров (зависит от используемой библиотеки)
        check = 5  # Пример значения
        if check > 3 and get_pixel_color(CREEP[0], CREEP[1] + offset) < 11111111:
            pyautogui.click(CREEP[0], CREEP[1] + offset)
            time.sleep(osm / 1000)
            pyautogui.click(CREE)
            pyautogui.click(CREE)
            pyautogui.click(CREE)
            send_telegram_message(f"Крипер купил скин по {i + 1} лоту в {time.strftime('%H:%M:%S')}")
            pyautogui.click(creeperso2)
            break

    # Периодический клик каждые 15 секунд
    current_time = time.time()
    if current_time - start_time > 15:
        start_time = current_time
        pyautogui.click(creeperso2)
        time.sleep(0.025)
        pyautogui.click(creeperso2)