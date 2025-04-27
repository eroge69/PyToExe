from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils import config

bot = Bot(token=("7510676019:AAGThUFUeGVgPt6G4_iTAwCKLmAQvfNsI9c"), parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
vip = Dispatcher(bot, storage=storage)
