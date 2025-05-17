import os
import subprocess
import tempfile
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация бота
BOT_TOKEN = '7739389715:AAF6mPckUWvL2giM0l-ZItp9w62IyNAovQc'
ALLOWED_USER_IDS = {689591132}  # Замените на ID пользователей, которым разрешено взаимодействие
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB максимальный размер файла


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("Доступ запрещен.")
        return

    await update.message.reply_text(
        "Привет! Отправь мне любой файл, и я попробую его запустить на этом компьютере.\n"
        "Поддерживаются все типы файлов:\n"
        "- Исполняемые файлы (.exe, .bat, .sh, .py и др.)\n"
        "- Документы (.docx, .pdf и др.) - будут открыты в соответствующей программе\n"
        "- Медиафайлы - будут воспроизведены\n\n"
        "Будь осторожен - это может быть опасно!"
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик загруженных файлов"""
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("Доступ запрещен.")
        return

    try:
        document = update.message.document

        # Проверка размера файла
        if document.file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024 * 1024)}MB")
            return

        file = await context.bot.get_file(document.file_id)
        file_extension = os.path.splitext(document.file_name)[1].lower()

        # Создаем временную директорию для файла
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, document.file_name)

            # Скачиваем файл
            await file.download_to_drive(file_path)
            await update.message.reply_text(f"Файл {document.file_name} успешно скачан. Пытаюсь запустить...")

            # Определяем команду для запуска в зависимости от типа файла
            if os.name == 'nt':  # Windows
                if file_extension in ('.exe', '.msi', '.bat', '.cmd'):
                    command = file_path
                elif file_extension in ('.py', '.pl', '.rb'):
                    command = f'python "{file_path}"'
                elif file_extension in ('.ps1',):
                    command = f'powershell -ExecutionPolicy Bypass -File "{file_path}"'
                else:
                    # Для остальных файлов пытаемся открыть с помощью ассоциированной программы
                    command = f'start "" "{file_path}"'
            else:  # Unix-like
                if file_extension in ('.sh', '.bash', '.zsh', '.py', '.pl', '.rb'):
                    os.chmod(file_path, 0o755)
                    command = f'./"{document.file_name}"'
                elif file_extension in ('.bin', '.run'):
                    os.chmod(file_path, 0o755)
                    command = f'./"{document.file_name}"'
                else:
                    # Для остальных файлов пытаемся открыть с помощью xdg-open
                    command = f'xdg-open "{file_path}"'

            try:
                # Запускаем файл с таймаутом (60 секунд)
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=temp_dir,
                    text=True
                )

                try:
                    stdout, stderr = process.communicate(timeout=60)
                    return_code = process.returncode
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    return_code = -1
                    await update.message.reply_text("Процесс был остановлен по таймауту (60 секунд)")

                # Формируем ответ
                response = (
                    f"Файл {document.file_name} выполнен.\n"
                    f"Код возврата: {return_code}\n"
                    f"Команда: {command}\n"
                )

                if stdout:
                    response += f"\nStdout:\n{stdout[:3000]}"
                if stderr:
                    response += f"\nStderr:\n{stderr[:3000]}"

                await update.message.reply_text(response)

            except Exception as e:
                await update.message.reply_text(f"Ошибка при выполнении файла: {str(e)}")
                logger.error(f"Error executing file: {e}", exc_info=True)

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")
        logger.error(f"Error in handle_document: {e}", exc_info=True)


def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()