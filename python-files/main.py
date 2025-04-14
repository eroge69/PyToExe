from telethon import TelegramClient, events
import os
import asyncio
import colorama
from datetime import datetime
from colorama import Fore, Back, Style
colorama.init()

valid = 0
nevalid = 0

current_datetime = datetime.now()

h = current_datetime.hour
m = current_datetime.minute
s = current_datetime.second

async def check_session(session_file):
    global valid
    global nevalid
    global me
    session_name = os.path.splitext(session_file)[0]
    client = TelegramClient(session_name, api_id, api_hash)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            nevalid += 1
            print(Fore.YELLOW, f"[-] [{os.path.basename(session_name)}] Аккаунт невалидный")
        else:
            print(Fore.GREEN, f"[+] [{os.path.basename(session_name)}] Аккаунт валидный")
            valid += 1
            me = await client.get_me() 
            print(Fore.GREEN,f'[+] номер телефона: {me.phone}')
            chat = await client.get_entity(777000)
            message = (await client.get_messages(chat, limit=1))[0]
            sender = await client.get_entity(message.sender_id)
            sender_name = sender.username or sender.first_name or str(sender.id)
            timestamp = message.date.strftime("%Y-%m-%d %H:%M:%S")
            text = message.message or ""
            if 'give' in text[26:31]:
                print(Fore.GREEN,f"[+] Полученный код для входа: {text[12:17]}")
            else:
                print(Fore.GREEN,f"[+] Полученный код для входа: {text[26:31]}")

    except Exception as e:
        print(Fore.RED, f"[!] [{os.path.basename(session_name)}] Ошибка: {e}")
    finally:
        await client.disconnect()

async def main():
    sessions_folder = 'sessions'
    session_files = os.listdir(sessions_folder)
    tasks = []

    for session_file in session_files:
        if session_file.endswith('.session'):
            task = asyncio.create_task(check_session(os.path.join(sessions_folder, session_file)))
            tasks.append(task)
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    api_id = 22145591
    api_hash = 'a158695b95d3c634ee71b0c54f93bb5c'
    asyncio.run(main())