#7559561963:AAHIAMex4w5Lg6Z2z_0iNAybxH8W59JM9yo
import json
import telebot, math
from telebot import types

bot = telebot.TeleBot("7559561963:AAHIAMex4w5Lg6Z2z_0iNAybxH8W59JM9yo")

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

user_progress = {}

activities = {
    1: "Рекомендую вам посетить SPA. Вот подходящий вариант: https://yandex.ru/maps/-/CHbOaH~v",
    2: "Рекомендую вам посетить уютное кафе. Вот подходящий вариант: https://yandex.ru/maps/-/CHbOa8lf",
    3: "Рекомендую вам посетить ужин в ресторане. Вот подходящий вариант: https://yandex.ru/maps/-/CHbOa0ir",
    4: "Рекомендую вам посетить театр или оперу. Вот подходящий вариант: https://yandex.ru/maps/-/CHbOaP5B",
    5: "Рекомендую вам посетить галерею или выставку. Вот подходящий вариант: https://yandex.ru/maps/-/CHbOaT~n",
    6: "Рекомендую вам посетить историческую экскурсию. Вот подходящий вариант: https://yandex.ru/maps/-/CHbOa-6A",
    7: "Рекомендую вам прогуляться по парку или набережной. Вот подходящий вариант: https://yandex.ru/maps/-/CHbOeILP",
    8: "Рекомендую вам посетить дегустацию и кулинарные мастер-классы. Вот подходящий вариант: https://yandex.ru/maps/-/CHbOeQ~R",
    9: "Рекомендую вам посетить фестиваль или концерт. Вот подходящий вариант: https://afisha.yandex.ru/perm/concert/solisty-orkestra-teatra-opery-i-baleta?source=rubric&schedule-date=2025-04-21",
    10: "Рекомендую вам посетить спортивное мероприятие. Вот подходящий вариант: https://afisha.yandex.ru/perm/sport/football-amkar-perm-orenburg-2?source=search-page",
    11: "Рекомендую вам посетить квест-комнату или VR-арену. Вот подходящий вариант: https://yandex.ru/maps/-/CHbOeJ9c",
    12: "Рекомендую вам посетить танцы в клубе/на вечеринке. Вот подходящий вариант: https://yandex.ru/maps/-/CHbOeR2U"
}

def send_question(chat_id, user_id):
    progress = user_progress[user_id]
    q_index = progress["current_q"]

    if q_index >= len(questions):
        result = process_results(progress["answers"])
        if user_id in user_progress.keys() and user_progress[user_id]["last_message_id"]:
            bot.delete_message(chat_id, user_progress[user_id]["last_message_id"])
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("/start")
        bot.send_message(chat_id=chat_id,
                              text=result, reply_markup=markup)
        user_progress.pop(user_id)
        return

    q = questions[q_index]
    text = f"{q['question']}"

    markup = types.InlineKeyboardMarkup()
    for i, ans in enumerate(q['answers']):
        markup.add(types.InlineKeyboardButton(
            text=ans, callback_data=str(i)))
    if q_index > 0:
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))

    if progress.get("last_message_id"):
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=progress["last_message_id"],
                text=text,
                reply_markup=markup
            )
        except:
            msg = bot.send_message(chat_id, text, reply_markup=markup)
            progress["last_message_id"] = msg.message_id
    else:
        msg = bot.send_message(chat_id, text, reply_markup=markup)
        progress["last_message_id"] = msg.message_id

def process_results(answers):
    int_answers = list(map(lambda x: int(x)+1, answers))
    Y1= 1.12 + 0.85*int_answers[0] + 0.49*int_answers[1] - 0.08*int_answers[2] + 1.15*int_answers[3] + 0.66*int_answers[4] - 0.20*int_answers[5] + 0.14*int_answers[0]**2 - 0.02*int_answers[1]**2 + 0.05*int_answers[2]**2 + 0.10*int_answers[3]**2 - 0.07*int_answers[4]**2 + 0.03*int_answers[5]**2 + 0.18*int_answers[0]*int_answers[1] + 0.04*int_answers[0]*int_answers[2] - 0.11*int_answers[0]*int_answers[3] + 0.06*int_answers[0]*int_answers[4] + 0.01*int_answers[0]*int_answers[5] - 0.05*int_answers[1]*int_answers[2] + 0.12*int_answers[1]*int_answers[3] + 0.03*int_answers[1]*int_answers[4] - 0.04*int_answers[1]*int_answers[5] + 0.09*int_answers[2]*int_answers[3] - 0.03*int_answers[2]*int_answers[4] + 0.07*int_answers[2]*int_answers[5] + 0.15*int_answers[3]*int_answers[4] - 0.01*int_answers[3]*int_answers[5] + 0.04*int_answers[4]*int_answers[5]
    print(Y1)
    if round(Y1) in activities.keys():
        return "Вы прошли тест. Спасибо за ответы!\nНейросеть думает, что лучший вариант для вас это:\n"+activities[round(Y1)]
    else:
        return "Вы прошли тест. Спасибо за ответы!\nНейросеть думает, что лучший вариант для вас это:\n"+activities[12]

@bot.message_handler(commands=["start"])
def start_quiz(message):
    user_id = message.from_user.id
    if user_id in user_progress.keys() and user_progress[user_id]["last_message_id"]:
        bot.delete_message(message.chat.id, user_progress[user_id]["last_message_id"])
    user_progress[user_id] = {
        "current_q": 0,
        "answers": [],
        "last_message_id": None
    }
    send_question(message.chat.id, user_id)

@bot.message_handler(func=lambda m: True)
def remind_buttons(message):
    user_id = message.from_user.id
    if user_id in user_progress.keys():
        bot.send_message(message.chat.id, "Пожалуйста, выбери вариант ответа кнопкой под сообщением.")
    else:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("/start")
        bot.send_message(message.chat.id, "Привет! Я могу помочь тебе выбрать занятие на вечер. Ответь на пару вопросов. Напиши /start, если хочешь начать тест", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_click(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data

    if user_id not in user_progress:
        bot.answer_callback_query(call.id, "Напиши /start чтобы начать тест.")
        return

    progress = user_progress[user_id]

    if data == "back":
        if progress["current_q"] > 0:
            progress["current_q"] -= 1
            progress["answers"].pop()
        send_question(chat_id, user_id)
        return

    progress["answers"].append(data)
    progress["current_q"] += 1
    send_question(chat_id, user_id)

bot.polling()
