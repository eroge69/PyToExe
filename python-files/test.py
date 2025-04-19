import requests

def check_website_availability(url):
    try:
        # Выполняем GET-запрос
        response = requests.get(url)
        
        # Проверяем статус-код ответа
        if response.status_code == 200:
            print(f"Сайт {url} доступен.")
        else:
            print(f"Не удалось зайти на сайт {url}. Статус-код: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Не удалось зайти на сайт {url}. Ошибка: {e}")

if __name__ == "__main__":
    url = "https://discord.com"  # URL для проверки доступности
    check_website_availability(url)
    
    # Ожидание нажатия клавиши перед завершением
    input("Нажмите Enter, чтобы завершить программу...")
