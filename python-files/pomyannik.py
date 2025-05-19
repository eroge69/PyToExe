# ---------- database.py ----------
from peewee import *
from datetime import datetime

db = SqliteDatabase('pomynnik.db')

class BaseModel(Model):
    class Meta:
        database = db

class Note(BaseModel):
    user_id = IntegerField()
    full_name = CharField()
    note_type = CharField()
    status = CharField(default='open')  # open/done/archived
    paid = BooleanField(default=False)
    repeats = IntegerField(null=True)
    target_date = DateTimeField()
    created_at = DateTimeField(default=datetime.now)
    payment_comment = CharField(null=True)
    closed_by = IntegerField(null=True)
    closed_at = DateTimeField(null=True)

class BankAccount(BaseModel):
    card_number = CharField()
    card_holder = CharField()
    bank_name = CharField()
    comment_template = TextField(default="Поминок #{id}")
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)

class Template(BaseModel):
    user_id = IntegerField()
    name = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.now)

db.create_tables([Note, BankAccount, Template], safe=True)

# ---------- config.py ----------
import pytz

class Config:
    TIMEZONE = pytz.timezone('Europe/Moscow')
    SERVICE_DAY_START_HOUR = 16
    ADMIN_CHAT_ID = -1001234567890
    BANK_ACCOUNT_ID = 1
    REPORT_TYPES = {
        'health': 'О здравии',
        'repose': 'Об упокоении',
        'sorokoust': 'Сорокоуст'
    }

# ---------- bot.py ----------
import logging
import pandas as pd
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Updater, CommandHandler, CallbackContext,
    ConversationHandler, CallbackQueryHandler,
    MessageHandler, Filters
)
from database import *
from config import Config
import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Состояния диалога
(
    TYPE, DATE, NAME, TEMPLATE,
    PAYMENT, REPORT_TYPE, CONFIRM_CLOSE
) = range(7)

def generate_note_info(note: Note) -> str:
    return (
        f"📌 Записка #{note.id}\n"
        f"👤 Подано: {note.full_name}\n"
        f"📅 Дата: {note.target_date.strftime('%d.%m.%Y')}\n"
        f"🔖 Тип: {Config.REPORT_TYPES.get(note.note_type, note.note_type)}\n"
        f"🔄 Повторов: {note.repeats or 1}\n"
        f"💬 Комментарий: {note.payment_comment}"
    )

def start(update: Update, context: CallbackContext):
    buttons = [
        [InlineKeyboardButton("Новая записка", callback_data='new_note')],
        [InlineKeyboardButton("Мои шаблоны", callback_data='templates')],
        [InlineKeyboardButton("Выгрузка записок", callback_data='report')]
    ]
    update.message.reply_text(
        "Главное меню:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return TYPE

def handle_new_note(update: Update, context: CallbackContext):
    query = update.callback_query
    buttons = [
        [InlineKeyboardButton("О здравии", callback_data='health'),
         InlineKeyboardButton("Об упокоении", callback_data='repose')],
        [InlineKeyboardButton("Сорокоуст (40 дней)", callback_data='sorokoust')]
    ]
    query.edit_message_text(
        text="Выберите тип поминовения:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return TYPE

def handle_type(update: Update, context: CallbackContext):
    query = update.callback_query
    note_type = query.data
    context.user_data['note_type'] = note_type
    
    # Генерация календаря
    today = datetime.datetime.now(Config.TIMEZONE)
    buttons = []
    for i in range(7):
        date = today + datetime.timedelta(days=i)
        buttons.append([InlineKeyboardButton(
            date.strftime('%d.%m.%Y'),
            callback_data=date.strftime('%Y-%m-%d')
        )])
    
    query.edit_message_text(
        text="Выберите дату поминовения:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return DATE

def handle_date(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['target_date'] = query.data
    
    templates = Template.select().where(Template.user_id == query.from_user.id)
    if templates.exists():
        buttons = [[InlineKeyboardButton(t.name, callback_data=f'template_{t.id}')] for t in templates]
        buttons.append([InlineKeyboardButton("Новый текст", callback_data='new_text')])
        query.edit_message_text(
            text="Выберите шаблон или создайте новый текст:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return TEMPLATE
    else:
        query.edit_message_text("Введите имена для поминовения (через запятую):")
        return NAME

def handle_template(update: Update, context: CallbackContext):
    query = update.callback_query
    template_id = int(query.data.split('_')[1])
    template = Template.get_by_id(template_id)
    return process_names(update, context, template.content)

def process_names(update: Update, context: CallbackContext, names: str = None):
    if not names:
        names = update.message.text
    
    if len(names) > 500:
        update.message.reply_text("Слишком длинный текст. Максимум 500 символов.")
        return NAME
    
    context.user_data['names'] = names
    
    account = BankAccount.get_by_id(Config.BANK_ACCOUNT_ID)
    comment = account.comment_template.format(id=Note.select().count()+1)
    
    msg = (
        "💳 Реквизиты для оплаты:\n\n"
        f"Номер карты: `{account.card_number[-4:].rjust(16, '*')}`\n"
        f"Владелец: {account.card_holder}\n"
        f"Банк: {account.bank_name}\n"
        f"Комментарий: {comment}\n\n"
        "После оплаты подтвердите платеж:"
    )
    
    buttons = [
        [InlineKeyboardButton("✅ Подтвердить оплату", callback_data='confirm_payment')],
        [InlineKeyboardButton("❌ Отменить", callback_data='cancel')]
    ]
    
    if update.callback_query:
        update.callback_query.edit_message_text(
            text=msg,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        update.message.reply_text(
            text=msg,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    context.user_data['payment_comment'] = comment
    return PAYMENT

def confirm_payment(update: Update, context: CallbackContext):
    query = update.callback_query
    note = Note.create(
        user_id=query.from_user.id,
        full_name=context.user_data['names'],
        note_type=context.user_data['note_type'],
        target_date=context.user_data['target_date'],
        payment_comment=context.user_data['payment_comment'],
        repeats=40 if context.user_data['note_type'] == 'sorokoust' else None
    )
    
    # Отправка админу
    admin_msg = generate_note_info(note) + "\n\n⚠ Требуется подтверждение оплаты"
    admin_buttons = [
        [InlineKeyboardButton("Подтвердить", callback_data=f"approve_{note.id}"),
         InlineKeyboardButton("Отклонить", callback_data=f"reject_{note.id}")]
    ]
    context.bot.send_message(
        chat_id=Config.ADMIN_CHAT_ID,
        text=admin_msg,
        reply_markup=InlineKeyboardMarkup(admin_buttons)
    )
    
    query.edit_message_text("Записка подана! Ожидайте подтверждения оплаты.")
    return ConversationHandler.END

def handle_admin_approval(update: Update, context: CallbackContext):
    query = update.callback_query
    action, note_id = query.data.split('_')
    note = Note.get_by_id(note_id)
    
    if action == 'approve':
        note.paid = True
        note.save()
        context.bot.send_message(
            chat_id=note.user_id,
            text=f"Записка #{note.id} подтверждена!\nДата поминовения: {note.target_date.strftime('%d.%m.%Y')}"
        )
        query.answer("Оплата подтверждена")
    else:
        note.delete_instance()
        context.bot.send_message(
            chat_id=note.user_id,
            text=f"Записка #{note_id} отклонена"
        )
        query.answer("Записка отклонена")
    
    query.message.delete()

def start_report(update: Update, context: CallbackContext):
    context.user_data['selected_types'] = []
    buttons = [
        [InlineKeyboardButton(f"{'✅ ' if t in context.user_data['selected_types'] else ''}{name}", 
         callback_data=f"toggle_{t}")] 
        for t, name in Config.REPORT_TYPES.items()
    ]
    buttons.append([InlineKeyboardButton("📤 Выгрузить", callback_data='generate')])
    update.message.reply_text(
        "Выберите типы записок для выгрузки:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return REPORT_TYPE

def handle_report_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data.split('_')[1]
    
    if data in Config.REPORT_TYPES:
        if data in context.user_data['selected_types']:
            context.user_data['selected_types'].remove(data)
        else:
            context.user_data['selected_types'].append(data)
        
        # Обновление кнопок
        buttons = [
            [InlineKeyboardButton(f"{'✅ ' if t in context.user_data['selected_types'] else ''}{name}", 
             callback_data=f"toggle_{t}")] 
            for t, name in Config.REPORT_TYPES.items()
        ]
        buttons.append([InlineKeyboardButton("📤 Выгрузить", callback_data='generate')])
        
        query.edit_message_text(
            text="Выберите типы записок для выгрузки:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data == 'generate':
        return generate_report(update, context)
    
    return REPORT_TYPE

def generate_report(update: Update, context: CallbackContext):
    selected_types = context.user_data['selected_types']
    
    query = Note.select().where(Note.status == 'open')
    if 'all' not in selected_types:
        query = query.where(Note.note_type << selected_types)
    
    notes = list(query)
    
    if not notes:
        update.callback_query.answer("Нет записок для выгрузки")
        return ConversationHandler.END
    
    # Создание Excel
    df = pd.DataFrame([{
        'ID': note.id,
        'Тип': Config.REPORT_TYPES.get(note.note_type),
        'Имена': note.full_name,
        'Дата': note.target_date.strftime('%d.%m.%Y'),
        'Повторы': note.repeats,
        'Комментарий': note.payment_comment
    } for note in notes])
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    
    output.seek(0)
    
    # Отправка файла
    context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=InputFile(output, filename='report.xlsx'),
        caption=f"Выгружено записок: {len(notes)}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Закрыть все записки", callback_data='close_all')]
        ])
    )
    
    context.user_data['report_notes'] = [n.id for n in notes]
    return CONFIRM_CLOSE

def close_all_notes(update: Update, context: CallbackContext):
    query = update.callback_query
    note_ids = context.user_data.get('report_notes', [])
    
    for nid in note_ids:
        note = Note.get_by_id(nid)
        note.status = 'done'
        note.closed_by = query.from_user.id
        note.closed_at = datetime.datetime.now()
        note.save()
    
    query.answer(f"Закрыто записок: {len(note_ids)}")
    query.message.edit_reply_markup()

def setup_handlers(dispatcher):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TYPE: [CallbackQueryHandler(handle_new_note, pattern='^new_note')],
            DATE: [CallbackQueryHandler(handle_date)],
            TEMPLATE: [CallbackQueryHandler(handle_template, pattern='^template_')],
            NAME: [MessageHandler(Filters.text & ~Filters.command, process_names)],
            PAYMENT: [CallbackQueryHandler(confirm_payment, pattern='^confirm_payment')],
            REPORT_TYPE: [CallbackQueryHandler(handle_report_selection, pattern='^toggle_|generate')],
            CONFIRM_CLOSE: [CallbackQueryHandler(close_all_notes, pattern='^close_all')]
        },
        fallbacks=[CallbackQueryHandler(lambda u,c: u.effective_message.delete(), pattern='^cancel')]
    )
    
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(handle_admin_approval, pattern='^(approve|reject)_'))

def main():
    updater = Updater("8165471594:AAG3MqjwIKXENOSyNOxMZ0As9yqE9H-5tvw")
    setup_handlers(updater.dispatcher)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

# ---------- admin.py ----------
from flask import Flask, render_template, request, redirect, url_for
from database import Note, BankAccount

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def dashboard():
    stats = {
        'total_notes': Note.select().count(),
        'open_notes': Note.select().where(Note.status == 'open').count(),
        'total_donations': sum(n.paid for n in Note.select())
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/notes')
def notes():
    notes = Note.select().order_by(Note.target_date.desc())
    return render_template('notes.html', notes=notes)

@app.route('/notes/close', methods=['POST'])
def close_notes():
    note_ids = request.form.getlist('note_ids')
    for nid in note_ids:
        note = Note.get_by_id(nid)
        note.status = 'done'
        note.save()
    return redirect(url_for('notes'))

@app.route('/bank_accounts', methods=['GET', 'POST'])
def bank_accounts():
    if request.method == 'POST':
        BankAccount.create(
            card_number=request.form['card_number'],
            card_holder=request.form['card_holder'],
            bank_name=request.form['bank_name'],
            comment_template=request.form['comment_template']
        )
    accounts = BankAccount.select()
    return render_template('bank_accounts.html', accounts=accounts)

if __name__ == '__main__':
    app.run(debug=True)

# ---------- templates/dashboard.html ----------
<!DOCTYPE html>
<html>
<head>
    <title>Панель управления</title>
</head>
<body>
    <h1>Статистика</h1>
    <div>
        <p>Всего записок: {{ stats.total_notes }}</p>
        <p>Открытых записок: {{ stats.open_notes }}</p>
        <p>Подтвержденных пожертвований: {{ stats.total_donations }}</p>
    </div>
</body>
</html>

# ---------- templates/notes.html ----------
<!DOCTYPE html>
<html>
<head>
    <title>Управление записками</title>
</head>
<body>
    <h2>Список записок</h2>
    <form method="post" action="/notes/close">
        <table border="1">
            <tr>
                <th>ID</th>
                <th>Тип</th>
                <th>Имена</th>
                <th>Дата</th>
                <th>Закрыть</th>
            </tr>
            {% for note in notes %}
            <tr>
                <td>{{ note.id }}</td>
                <td>{{ note.note_type }}</td>
                <td>{{ note.full_name }}</td>
                <td>{{ note.target_date.strftime('%d.%m.%Y') }}</td>
                <td><input type="checkbox" name="note_ids" value="{{ note.id }}"></td>
            </tr>
            {% endfor %}
        </table>
        <button type="submit">Закрыть выбранные</button>
    </form>
</body>
</html>

# ---------- requirements.txt ----------
python-telegram-bot==13.7
peewee==3.14.4
pytz==2021.3
Flask==2.0.1
pandas==1.3.5
xlsxwriter==3.0.3
openpyxl==3.0.10