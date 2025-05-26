import os
import subprocess
import pyautogui
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from datetime import datetime
import logging
import shutil
import psutil
import platform
import time
import winsound  # Для Windows, для інших ОС потрібні альтернативи
import glob

# Налаштування логування
logging.basicConfig(
    filename='bot_activity.log',  # Лог зберігатиметься у файл
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ваш Telegram ID для обмеження доступу (замініть на свій ID)
ALLOWED_USER_ID = 123456789  # Отримайте свій ID, надіславши /start боту
# Токен вашого бота від BotFather
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Замініть на токен від @BotFather

# Налаштування pyautogui
pyautogui.FAILSAFE = True  # Переміщення миші в кут екрана зупинить виконання
pyautogui.PAUSE = 0.1  # Пауза між діями

async def start(update, context):
    """Обробник команди /start"""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("Доступ заборонено! Ви не авторизований користувач.")
        logger.warning(f"Несанкціонований доступ: user_id={user_id}")
        return
    await update.message.reply_text(
        "Ласкаво просимо до бота для керування ПК!\n"
        "Доступні команди:\n"
        "/screenshot - Зробити знімок екрана\n"
        "/shutdown - Вимкнути ПК\n"
        "/reboot - Перезавантажити ПК\n"
        "/cmd <команда> - Виконати команду в терміналі\n"
        "/processes - Показати список запущених процесів\n"
        "/lock - Заблокувати екран\n"
        "/upload <шлях> - Надіслати файл\n"
        "/play_sound <повідомлення> - Відтворити звукове повідомлення\n"
        "/system_info - Показати використання CPU, RAM, диска\n"
        "/run_app <шлях або назва> - Запустити програму\n"
        "/mouse <x> <y> - Перемістити мишу\n"
        "/type <текст> - Ввести текст\n"
        "/list_dir <шлях> - Показати вміст директорії"
    )
    logger.info(f"Команда /start виконана користувачем {user_id}")

async def check_access(update, context):
    """Перевірка доступу користувача"""
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Доступ заборонено! Ви не авторизований користувач.")
        logger.warning(f"Несанкціонований доступ: user_id={update.effective_user.id}")
        return False
    return True

async def screenshot(update, context):
    """Зробити знімок екрана та надіслати його"""
    if not await check_access(update, context):
        return
    try:
        screenshot = pyautogui.screenshot()
        screenshot_path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot.save(screenshot_path)
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(screenshot_path, 'rb')
        )
        os.remove(screenshot_path)
        await update.message.reply_text("Скріншот надіслано!")
        logger.info("Скріншот створено та надіслано")
    except Exception as e:
        await update.message.reply_text(f"Помилка при створенні скріншота: {str(e)}")
        logger.error(f"Помилка скріншота: {str(e)}")

async def shutdown(update, context):
    """Вимкнути комп'ютер"""
    if not await check_access(update, context):
        return
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(["shutdown", "/s", "/t", "0"])
        else:  # Linux/MacOS
            subprocess.run(["sudo", "shutdown", "-h", "now"])
        await update.message.reply_text("Комп'ютер вимикається...")
        logger.info("Команда вимкнення виконана")
    except Exception as e:
        await update.message.reply_text(f"Помилка при вимкненні: {str(e)}")
        logger.error(f"Помилка вимкнення: {str(e)}")

async def reboot(update, context):
    """Перезавантажити комп'ютер"""
    if not await check_access(update, context):
        return
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(["shutdown", "/r", "/t", "0"])
        else:  # Linux/MacOS
            subprocess.run(["sudo", "reboot"])
        await update.message.reply_text("Комп'ютер перезавантажується...")
        logger.info("Команда перезавантаження виконана")
    except Exception as e:
        await update.message.reply_text(f"Помилка при перезавантаженні: {str(e)}")
        logger.error(f"Помилка перезавантаження: {str(e)}")

async def cmd(update, context):
    """Виконати команду в терміналі"""
    if not await check_access(update, context):
        return
    try:
        command = ' '.join(context.args)
        if not command:
            await update.message.reply_text("Будь ласка, вкажіть команду. Наприклад: /cmd dir")
            return
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout or result.stderr
        if len(output) > 4096:
            output = output[:4090] + "..."
        await update.message.reply_text(output or "Команда виконана без виведення.")
        logger.info(f"Команда '{command}' виконана")
    except Exception as e:
        await update.message.reply_text(f"Помилка при виконанні команди: {str(e)}")
        logger.error(f"Помилка команди '{command}': {str(e)}")

async def processes(update, context):
    """Показати список запущених процесів"""
    if not await check_access(update, context):
        return
    try:
        process_list = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            process_list.append(f"PID: {proc.info['pid']} | Name: {proc.info['name']} | CPU: {proc.info['cpu_percent']:.1f}%")
        output = "\n".join(process_list[:50])  # Обмежуємо до 50 процесів
        if len(output) > 4096:
            output = output[:4090] + "..."
        await update.message.reply_text(output or "Немає активних процесів.")
        logger.info("Список процесів надіслано")
    except Exception as e:
        await update.message.reply_text(f"Помилка при отриманні списку процесів: {str(e)}")
        logger.error(f"Помилка списку процесів: {str(e)}")

async def lock(update, context):
    """Заблокувати екран"""
    if not await check_access(update, context):
        return
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        else:  # Linux (залежить від середовища)
            subprocess.run(["xdg-screensaver", "lock"])
        await update.message.reply_text("Екран заблоковано!")
        logger.info("Екран заблоковано")
    except Exception as e:
        await update.message.reply_text(f"Помилка при блокуванні екрана: {str(e)}")
        logger.error(f"Помилка блокування екрана: {str(e)}")

async def upload(update, context):
    """Надіслати файл із комп'ютера"""
    if not await check_access(update, context):
        return
    try:
        file_path = ' '.join(context.args)
        if not file_path:
            await update.message.reply_text("Будь ласка, вкажіть шлях до файлу. Наприклад: /upload C:\\file.txt")
            return
        if not os.path.exists(file_path):
            await update.message.reply_text("Файл не знайдено!")
            return
        if os.path.getsize(file_path) > 50 * 1024 * 1024:  # Ліміт Telegram 50 МБ
            await update.message.reply_text("Файл занадто великий (ліміт 50 МБ)!")
            return
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=open(file_path, 'rb')
        )
        await update.message.reply_text("Файл надіслано!")
        logger.info(f"Файл '{file_path}' надіслано")
    except Exception as e:
        await update.message.reply_text(f"Помилка при надсиланні файлу: {str(e)}")
        logger.error(f"Помилка надсилання файлу '{file_path}': {str(e)}")

async def play_sound(update, context):
    """Відтворити звукове повідомлення"""
    if not await check_access(update, context):
        return
    try:
        message = ' '.join(context.args) or "Hello from your PC!"
        if os.name == 'nt':  # Windows
            winsound.MessageBeep()  # Простий звуковий сигнал
            # Для текстового повідомлення потрібна TTS бібліотека, наприклад, pyttsx3
            await update.message.reply_text("Звук відтворено!")
        else:
            # Для Linux/MacOS можна використати 'say' або 'aplay'
            subprocess.run(["say", message] if platform.system() == "Darwin" else ["aplay", "/usr/share/sounds/alsa/Front_Center.wav"])
            await update.message.reply_text("Звук відтворено!")
        logger.info(f"Звук відтворено: {message}")
    except Exception as e:
        await update.message.reply_text(f"Помилка при відтворенні звуку: {str(e)}")
        logger.error(f"Помилка відтворення звуку: {str(e)}")

async def system_info(update, context):
    """Показати використання системних ресурсів"""
    if not await check_access(update, context):
        return
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        output = (
            f"CPU: {cpu_usage}%\n"
            f"RAM: {(ram.used / 1024**3):.2f}/{ram.total / 1024**3:.2f} GB ({ram.percent}%)\n"
            f"Диск: {(disk.used / 1024**3):.2f}/{disk.total / 1024**3:.2f} GB ({disk.percent}%)"
        )
        await update.message.reply_text(output)
        logger.info("Інформація про систему надіслана")
    except Exception as e:
        await update.message.reply_text(f"Помилка при отриманні інформації про систему: {str(e)}")
        logger.error(f"Помилка системної інформації: {str(e)}")

async def run_app(update, context):
    """Запустити програму"""
    if not await check_access(update, context):
        return
    try:
        app = ' '.join(context.args)
        if not app:
            await update.message.reply_text("Будь ласка, вкажіть назву програми або шлях. Наприклад: /run_app notepad")
            return
        if os.name == 'nt':  # Windows
            subprocess.Popen(app, shell=True)
        else:  # Linux/MacOS
            subprocess.run(["open", app] if platform.system() == "Darwin" else ["xdg-open", app])
        await update.message.reply_text(f"Програму '{app}' запущено!")
        logger.info(f"Програма '{app}' запущена")
    except Exception as e:
        await update.message.reply_text(f"Помилка при запуску програми: {str(e)}")
        logger.error(f"Помилка запуску програми '{app}': {str(e)}")

async def mouse(update, context):
    """Перемістити мишу до координат"""
    if not await check_access(update, context):
        return
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Вкажіть координати x, y. Наприклад: /mouse 100 200")
            return
        x, y = map(int, args)
        pyautogui.moveTo(x, y)
        await update.message.reply_text(f"Мишу переміщено до ({x}, {y})")
        logger.info(f"Мишу переміщено до ({x}, {y})")
    except Exception as e:
        await update.message.reply_text(f"Помилка при переміщенні миші: {str(e)}")
        logger.error(f"Помилка переміщення миші: {str(e)}")

async def type_text(update, context):
    """Ввести текст"""
    if not await check_access(update, context):
        return
    try:
        text = ' '.join(context.args)
        if not text:
            await update.message.reply_text("Вкажіть текст для введення. Наприклад: /type Hello World")
            return
        pyautogui.write(text)
        await update.message.reply_text(f"Текст '{text}' введено")
        logger.info(f"Текст '{text}' введено")
    except Exception as e:
        await update.message.reply_text(f"Помилка при введенні тексту: {str(e)}")
        logger.error(f"Помилка введення тексту: {str(e)}")

async def list_dir(update, context):
    """Показати вміст директорії"""
    if not await check_access(update, context):
        return
    try:
        path = ' '.join(context.args) or os.getcwd()
        if not os.path.isdir(path):
            await update.message.reply_text("Недійсна директорія!")
            return
        files = glob.glob(os.path.join(path, '*'))
        output = "\n".join([os.path.basename(f) for f in files][:50])  # Обмежуємо до 50 елементів
        if len(output) > 4096:
            output = output[:4090] + "..."
        await update.message.reply_text(output or "Директорія порожня.")
        logger.info(f"Вміст директорії '{path}' надіслано")
    except Exception as e:
        await update.message.reply_text(f"Помилка при перегляді директорії: {str(e)}")
        logger.error(f"Помилка перегляду директорії '{path}': {str(e)}")

async def error_handler(update, context):
    """Обробка помилок"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("Виникла помилка. Спробуйте ще раз.")

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("screenshot", screenshot))
    application.add_handler(CommandHandler("shutdown", shutdown))
    application.add_handler(CommandHandler("reboot", reboot))
    application.add_handler(CommandHandler("cmd", cmd))
    application.add_handler(CommandHandler("processes", processes))
    application.add_handler(CommandHandler("lock", lock))
    application.add_handler(CommandHandler("upload", upload))
    application.add_handler(CommandHandler("play_sound", play_sound))
    application.add_handler(CommandHandler("system_info", system_info))
    application.add_handler(CommandHandler("run_app", run_app))
    application.add_handler(CommandHandler("mouse", mouse))
    application.add_handler(CommandHandler("type", type_text))
    application.add_handler(CommandHandler("list_dir", list_dir))
    application.add_error_handler(error_handler)

    logger.info("Бот запущено")
    application.run_polling()

if __name__ == '__main__':
    main()
