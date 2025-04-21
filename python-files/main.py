import requests
from bs4 import BeautifulSoup
import time

app_ids = [3594280, 3474130,270880,393380]  # твои appid
base_url = "https://help.steampowered.com/ru/wizard/HelpWithGameTechnicalIssue/?appid="

results = {}

for appid in app_ids:
    url = f"{base_url}{appid}"
    print(f"Обрабатываю AppID: {appid}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        divs = soup.find_all('div', class_='help_official_support_row')
        found = False
        for div in divs:
            if 'Эл. почта' in div.text:
                text = div.get_text(strip=True)
                email = text.split(':', 1)[1].strip()
                results[appid] = email
                found = True
                break
        if not found:
            results[appid] = "Не найдено"
    except Exception as e:
        results[appid] = f"Ошибка: {e}"

    time.sleep(1)  # Пауза между запросами

# Вывод результата
for appid, email in results.items():
    print(f"AppID: {appid}, Email: {email}")