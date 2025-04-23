import vk_api
import telegram
import asyncio
import time
from vk_api.exceptions import ApiError
from datetime import datetime

# Конфигурация
VK_TOKEN = 'vk1.a.wZE4naZ1Qs7i-NNHqEKnQGaxUq7b8dD8ttD7DduqleTyWGXRJwR-A88qXQT6C9WaLazPsq4wsTANp67T6CqjyJ6JWIKJz0238498ErE_Yi2dEQ4w4WQ9ZZZjROaLdMHf-qYiLyxpP9SORQyUNCWSuksmklwJTdVIBAoLK4IMzlu8eU43Rx7B5_AH7emI4h10aT5v1aqErCf2LgzD15gvpA'  # Ваш токен
GROUP_ID = -207203501  # ID группы ВК
TARGET_USER_ID = 715493925  # Ваш ID (Евгения Голубова)
TELEGRAM_TOKEN = '7391360173:AAGeymKY6QXZ5mRksuNQ0DPQuFqEuenrbAk'  # Токен Telegram-бота
TELEGRAM_CHAT_ID = '5092781395'  # Вставьте ID чата Telegram
CHECK_INTERVAL = 30  # Интервал проверки в секундах (5 минут)

# Инициализация API
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
telegram_bot = telegram.Bot(token=TELEGRAM_TOKEN)

def format_attachments(attachments):
    if not attachments:
        return "Нет вложений"
    attachment_info = []
    for attachment in attachments:
        if attachment['type'] == 'photo':
            photo = attachment['photo']
            largest_photo = max(photo['sizes'], key=lambda s: s['width'])
            attachment_info.append(f"Фото: {largest_photo['url']}")
        elif attachment['type'] == 'video':
            video = attachment['video']
            attachment_info.append(f"Видео: {video.get('title', 'Без названия')}")
        elif attachment['type'] == 'link':
            link = attachment['link']
            attachment_info.append(f"Ссылка: {link.get('url', 'Нет URL')}")
        else:
            attachment_info.append(f"Вложение ({attachment['type']}): {attachment.get('id', 'Нет ID')}")
    return "\n".join(attachment_info)

async def send_group_info():
    try:
        # Получаем информацию о группе
        group_info = vk.groups.getById(group_id=abs(GROUP_ID), fields='description,members_count')[0]
        
        # Извлекаем данные
        group_name = group_info.get('name', 'Не указано')
        group_id = group_info.get('id', 'Не указано')
        members_count = group_info.get('members_count', 'Не указано')
        description = group_info.get('description', 'Нет описания')
        group_url = f"https://vk.com/club{group_id}"
        
        # Ищем аватарку группы
        photo_url = None
        if 'photo_200' in group_info:
            photo_url = group_info['photo_200']

        # Формируем сообщение
        message = (
            f"🏠 Информация о группе ВКонтакте:\n"
            f"📛 Название: {group_name}\n"
            f"🆔 ID: {group_id}\n"
            f"👥 Подписчиков: {members_count}\n"
            f"📝 Описание: {description[:200] + '...' if len(description) > 200 else description}\n"
            f"🔗 Ссылка: {group_url}\n"
            f"⏰ Бот запущен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Отправляем сообщение с фото (если есть)
        if photo_url:
            await telegram_bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=photo_url,
                caption=message
            )
        else:
            await telegram_bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message
            )

    except ApiError as e:
        error_msg = f"Ошибка при получении информации о группе: {str(e)}"
        print(error_msg)
        await telegram_bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"⚠️ {error_msg}"
        )
    except telegram.error.TelegramError as e:
        error_msg = f"Ошибка при отправке информации о группе в Telegram: {str(e)}"
        print(error_msg)
        await telegram_bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"⚠️ {error_msg}"
        )

async def check_and_delete_posts():
    while True:
        try:
            # Получаем последние 10 постов
            posts = vk.wall.get(owner_id=GROUP_ID, count=10)
            
            for post in posts['items']:
                # Проверяем signer_id, from_id и created_by
                signer_id = post.get('signer_id')
                from_id = post.get('from_id')
                created_by = post.get('created_by')
                post_id = post['id']
                post_text = post.get('text', '')
                post_date = datetime.fromtimestamp(post['date']).strftime('%Y-%m-%d %H:%M:%S')
                attachments = post.get('attachments', [])
                likes = post['likes']['count']
                reposts = post['reposts']['count']
                views = post.get('views', {}).get('count', 'Неизвестно')

                # Условие удаления: если signer_id, from_id или created_by совпадает с вашим ID
                should_delete = False
                if signer_id == TARGET_USER_ID or from_id == TARGET_USER_ID or created_by == TARGET_USER_ID:
                    should_delete = True
                
                if should_delete:
                    try:
                        # Ищем первое фото для отправки в Telegram
                        photo_url = None
                        for attachment in attachments:
                            if attachment['type'] == 'photo':
                                photo = attachment['photo']
                                largest_photo = max(photo['sizes'], key=lambda s: s['width'])
                                photo_url = largest_photo['url']
                                break

                        # Формируем уведомление
                        message = (
                            f"🔔 Обнаружен и удалён пост в группе ВК!\n"
                            f"📜 ID поста: {post_id}\n"
                            f"👤 Автор: Vlada Zaytseva (ID: {TARGET_USER_ID})\n"
                            f"✍️ Подписал: {signer_id or 'нет подписи'}\n"
                            f"🖌️ Создал: {created_by or 'не указано'}\n"
                            f"📝 Текст: {post_text[:200] + '...' if len(post_text) > 200 else post_text}\n"
                            f"📅 Опубликован: {post_date}\n"
                            f"🗑️ Удалён: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"📎 Вложения:\n{format_attachments(attachments)}\n"
                            f"❤️ Лайков: {likes}\n"
                            f"🔄 Репостов: {reposts}\n"
                            f"👀 Просмотров: {views}"
                        )

                        # Отправляем уведомление и фото (если есть)
                        if photo_url:
                            await telegram_bot.send_photo(
                                chat_id=TELEGRAM_CHAT_ID,
                                photo=photo_url,
                                caption=message
                            )
                        else:
                            await telegram_bot.send_message(
                                chat_id=TELEGRAM_CHAT_ID,
                                text=message
                            )

                        # Удаляем пост после отправки уведомления
                        vk.wall.delete(owner_id=GROUP_ID, post_id=post_id)
                        print(f"Удалён пост {post_id} от пользователя {signer_id or from_id or created_by}")
                        
                    except ApiError as e:
                        error_msg = f"Ошибка при удалении поста {post_id}: {str(e)}"
                        print(error_msg)
                        await telegram_bot.send_message(
                            chat_id=TELEGRAM_CHAT_ID,
                            text=f"⚠️ {error_msg}"
                        )
                    except telegram.error.TelegramError as e:
                        error_msg = f"Ошибка при отправке в Telegram: {str(e)}"
                        print(error_msg)
                        await telegram_bot.send_message(
                            chat_id=TELEGRAM_CHAT_ID,
                            text=f"⚠️ {error_msg}"
                        )
            
        except ApiError as e:
            error_msg = f"Ошибка при проверке постов: {str(e)}"
            print(error_msg)
            await telegram_bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=f"⚠️ {error_msg}"
            )
        
        # Ждём 5 минут
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    print("Бот запущен...")
    # Отправляем информацию о группе при запуске
    await send_group_info()
    # Запускаем цикл проверки постов
    await check_and_delete_posts()

if __name__ == "__main__":
    asyncio.run(main())
