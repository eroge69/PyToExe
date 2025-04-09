from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import ChatWriteForbiddenError, UsernameNotOccupiedError, PeerIdInvalidError, ChannelPrivateError
import asyncio
import os
import configparser

# Конфигурация
CONFIG_FILE = 'config.ini'
SESSION_FILE = 'spam_session'
GROUP_LIST_FILE = 'groups.txt'
DELAY_SECONDS = 5  # Задержка по умолчанию

# Функция для загрузки конфигурации
def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        return (
            config.get('Telegram', 'API_ID', fallback=''),
            config.get('Telegram', 'API_HASH', fallback=''),
            config.get('Telegram', 'PHONE_NUMBER', fallback='')
        )
    return '', '', ''

# Функция для сохранения конфигурации
def save_config(api_id, api_hash, phone_number):
    config = configparser.ConfigParser()
    config['Telegram'] = {
        'API_ID': api_id,
        'API_HASH': api_hash,
        'PHONE_NUMBER': phone_number
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Получение данных от пользователя
def get_credentials():
    api_id = input("Введите ваш API ID: ").strip()
    api_hash = input("Введите ваш API HASH: ").strip()
    phone_number = input("Введите ваш номер телефона: ").strip()
    save_config(api_id, api_hash, phone_number)
    return api_id, api_hash, phone_number

# Загрузка или запрос данных
API_ID, API_HASH, PHONE_NUMBER = load_config()
if not all([API_ID, API_HASH, PHONE_NUMBER]):
    print("Конфигурация не найдена. Введите данные для начала работы.")
    API_ID, API_HASH, PHONE_NUMBER = get_credentials()

# Создаем клиент Telethon
client = TelegramClient(SESSION_FILE, int(API_ID), API_HASH)

# Чтение списка групп из файла
def read_groups():
    if os.path.exists(GROUP_LIST_FILE):
        with open(GROUP_LIST_FILE, 'r') as file:
            return [line.strip() for line in file.readlines()]
    return []

# Запись списка групп в файл
def write_groups(groups):
    with open(GROUP_LIST_FILE, 'w') as file:
        for group in groups:
            file.write(group + '\n')

# Добавить группу
def add_group(group):
    groups = read_groups()
    if group not in groups:
        groups.append(group)
        write_groups(groups)
        print(f"✅ Группа {group} добавлена")
    else:
        print(f"❌ Группа {group} уже существует")

# Удалить группу
def remove_group(group):
    groups = read_groups()
    if group in groups:
        groups.remove(group)
        write_groups(groups)
        print(f"✅ Группа {group} удалена")
    else:
        print(f"❌ Группа {group} не найдена")

# Очистить список групп
def clear_groups():
    if os.path.exists(GROUP_LIST_FILE):
        os.remove(GROUP_LIST_FILE)
        print("✅ Список групп очищен")
    else:
        print("❌ Список групп уже пуст")

async def join_group(group):
    """
    Функция для присоединения к группе/каналу.
    """
    try:
        await client(JoinChannelRequest(group))
        print(f"✅ Успешно присоединился к {group}")
    except UsernameNotOccupiedError:
        print(f"❌ Группа {group} не существует")
    except PeerIdInvalidError:
        print(f"❌ Неверный ID или имя группы {group}")
    except ChannelPrivateError:
        print(f"❌ Группа {group} приватная, и вы не являетесь участником")
    except Exception as e:
        print(f"❌ Ошибка при присоединении к {group}: {str(e)}")

async def send_spam(text, count):
    """
    Функция для рассылки сообщений.
    """
    groups = read_groups()
    if not groups:
        print("❌ Нет групп для рассылки!")
        return

    print(f"🚀 Запуск рассылки: {count} раз(а) с интервалом {DELAY_SECONDS} сек.")

    for i in range(count):
        for group in groups:
            try:
                await join_group(group)
                await client.send_message(entity=group, message=text)
                print(f"✅ [{i+1}/{count}] Отправлено в {group}")
            except ChatWriteForbiddenError:
                print(f"❌ Нет прав на отправку в {group}")
            except ChannelPrivateError:
                print(f"❌ Группа {group} приватная, и вы не являетесь участником")
            except Exception as e:
                print(f"❌ Ошибка в {group}: {str(e)}")
        await asyncio.sleep(DELAY_SECONDS)

    print("📢 Рассылка завершена!")

async def auto_reply(message, reply_text):
    """
    Функция для автоответчика.
    """
    @client.on(events.NewMessage)
    async def handler(event):
        if event.message.message == message:
            await event.reply(reply_text)
            print(f"✅ Автоответ на сообщение: {message}")

async def main():
    await client.start(PHONE_NUMBER)
    print("✅ Авторизация успешна!")

    while True:
        print("==================================================")
        print("            Funpay : Vadya1112")
        print("            THX for your buying")
        print("==================================================")
        print("\nМеню:")
        print("1. Добавить группу")
        print("2. Удалить группу")
        print("3. Очистить список групп")
        print("4. Начать рассылку")
        print("5. Настроить задержку")
        print("6. Настроить автоответчик")
        print("7. Выйти")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            group = input("Введите имя группы/канала: ").strip()
            add_group(group)
        elif choice == "2":
            group = input("Введите имя группы/канала: ").strip()
            remove_group(group)
        elif choice == "3":
            clear_groups()
        elif choice == "4":
            text = input("Введите текст сообщения: ").strip()
            count = int(input("Введите количество сообщений: ").strip())
            await send_spam(text, count)
        elif choice == "5":
            global DELAY_SECONDS
            DELAY_SECONDS = int(input("Введите новую задержку (в секундах): ").strip())
            print(f"✅ Задержка изменена на {DELAY_SECONDS} сек.")
        elif choice == "6":
            message = input("Введите сообщение для отслеживания: ").strip()
            reply_text = input("Введите текст ответа: ").strip()
            await auto_reply(message, reply_text)
            print("✅ Автоответчик настроен")
        elif choice == "7":
            break
        else:
            print("❌ Неверный выбор")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
