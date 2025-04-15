from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile, WebAppInfo
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json
import os
import logging
import asyncio
import subprocess

TOKEN = "7705593359:AAG0c8-Fl6S_NoemvEgZsb3v8TgDHwBppig"
bot = Bot(token=TOKEN)
dp = Dispatcher()

key_auth = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Авторизоваться")]
], resize_keyboard=True)

key_main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Командная строка ВКЛ"), KeyboardButton(text="Командная строка ВЫКЛ")],
    [KeyboardButton(text="Загрузить файл"), KeyboardButton(text="Скачать файл")],
], resize_keyboard=True)

key_cancel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Отмена")]
], resize_keyboard=True)

def auth_scan(id):
    with open("auth.json", "r") as f:
        data = json.load(f)
    if id in data:
        return True
    else:
        return False

input_auth = []
input_cmd = []
input_download = []

@dp.message()
async def echo(message: Message):
    if message.document:
        try:
            path = os.getcwd()
            file = await bot.get_file(message.document.file_id)
            file_data = await bot.download_file(file.file_path)
            with open(os.path.join(path, message.document.file_name), "wb") as f:
                f.write(file_data.read())
            await message.reply("Файл сохранён")
        except Exception as e:
            await message.reply(f'Ошибка: {e}')
    if message.text == "/start":
        if auth_scan(message.from_user.id):
            await message.reply("Выберите операцию", reply_markup=key_main)
        else:
            await message.reply("Вы не авторизованные", reply_markup=key_auth)
    elif message.text == "Авторизоваться":
        await message.reply("Напишите токен доступа")
        input_auth.append(message.from_user.id)
    elif message.text == "Командная строка ВКЛ" and auth_scan(message.from_user.id):
        if not message.from_user.id in input_cmd:
            input_cmd.append(message.from_user.id)
            await message.reply("Теперь вводите команды")
        else:
            await message.reply("Бот уже принимает команды")
    elif message.text == "Командная строка ВЫКЛ" and auth_scan(message.from_user.id):
        if message.from_user.id in input_cmd:
            input_cmd.remove(message.from_user.id)
            await message.reply("Команды больше не принимаются")
        else:
            await message.reply("Бот уже не принимает команды")
    elif message.text == "Скачать файл" and auth_scan(message.from_user.id):
        input_download.append(message.from_user.id)
        await message.reply("Введите директорию файла", reply_markup=key_cancel)
    elif message.text == "Отмена" and auth_scan(message.from_user.id):
        if message.from_user.id in input_download:
            input_download.remove(message.from_user.id)
        await message.reply("Отмена", reply_markup=key_main)
    elif message.text == "Загрузить файл" and auth_scan(message.from_user.id):
        await message.reply("Скиньте файл виде документа")
    else:
        if message.from_user.id in input_download:
            await bot.send_document(message.from_user.id, FSInputFile(message.text))
            input_download.remove(message.from_user.id)
        if message.from_user.id in input_auth:
            if message.text == "nodefeat2025":
                await message.reply("Токен доступа принят")
                with open("auth.json", "r") as f:
                    data = json.load(f)
                data.append(message.from_user.id)
                with open("auth.json", "w") as f:
                    json.dump(data, f)
            else:
                await message.reply("Неверный токен")
                input_auth.remove(message.from_user.id)
        if message.from_user.id in input_cmd:
            try:
                out = subprocess.check_output(message.text, shell=True, stderr=subprocess.STDOUT)
                await message.reply(out)
            except Exception as e:
                await message.reply("Ошибка "+str(e))

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())