from typing import Tuple
# Мои модули
import database as db
from database import bot, month_mapping, event_map
import admin_cmds
import menu


def check_registration(event_id, user_id): # Проверка не записан ли еще, дабы избежать записи через старую кнопку, когда уже записались в другой кнопке
    try: # Попытка взять запись из ДБ, если записи нет, значит Null
        row = db.get_reg_info(event_id, user_id)
    except:
        row = None
    return row


def get_event_id(calldata: str, cut = 0) -> Tuple[str, str]:
    event_id = calldata[cut:]
    day = event_id[6:8].lstrip('0')
    month = month_mapping.get(event_id[9:11], 'несуществующего месяца')
    time = event_id[15:].replace('-', ':')
    event_date = f'*{day} {month}* в *{time}*'
    return event_date, event_id


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_reg_'))
def call_cancel_reg(call):
    event_date, event_id = get_event_id(call.data, 11)
    db.deregister_user(event_id, call.from_user.id)
    message_text = f'❗️Вы отказались от записи на *{event_map[event_id]}*, который будет {event_date}\n\n_Перейдите по ссылке еще раз, если это было случайно_ 😉'
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=None)


@bot.callback_query_handler(func=lambda call: call.data.startswith('reg_'))
def call_reg(call):
    event_date, event_id = get_event_id(call.data, 4)
    row = check_registration(event_id, call.from_user.id)
    message_text = f'*{event_map[event_id]}*\n📅 {event_date}\n\nСколько вас ждать? 🤗'
    if not row: # Если запись не найдена
        db.register_user(event_id, call.from_user.id, 1)
    markup = menu.how_many_with_you(event_id)
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('new_tickets_'))
def call_reg(call):
    event_date, event_id = get_event_id(call.data, 12)
    row = check_registration(event_id, call.from_user.id)
    if row: # Если запись найдена
        message_text = f'*{event_map[event_id]}*\n📅 {event_date}\n\nСколько вас ждать? 🤗'
        markup = menu.how_many_with_you(event_id)
    else: # Если запись не найдена
        message_text = f'❗️Вы не записаны на *{event_map[event_id]}*, который будет {event_date}\n\n_Перейдите по ссылке из поста для записи на мероприятие_ 😉'
        markup = None
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('close_dereg'))
def call_close_dereg(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('visitors_'))
def call_visitors(call):
    event_date, event_id = get_event_id(call.data, 11)
    row = check_registration(event_id, call.from_user.id)
    tickets = int(call.data[9:10])
    if row: # Если запись найдена
        db.change_cell('tickets', tickets, call.from_user.id, event_id)
        message_text = f'✅ Вы записаны\n*{event_map[event_id]}*\n📅 {event_date}\n🎟 Билетиков: *{tickets}*\n\nУведомить за 1 час до мероприятия?'
        markup = menu.notification(event_id)
        bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    else: # Если запись не найдена
        bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('notify_'))
def call_notify(call):
    notification_mode = int(call.data[7:8])
    event_date, event_id = get_event_id(call.data, 9)
    db.change_cell('notification', notification_mode, call.from_user.id, event_id)
    bot.edit_message_text('✅', call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=None)
    if notification_mode == 1:
        text_variant = '🔔 Бот отправит уведомление за 1 час до мероприятия'
    elif notification_mode == 2:
        text_variant = '🔕 Бот отправит уведомление *без звука* за 1 час до мероприятия'
    else:
        text_variant = '🚫 Бот не будет вас беспокоить'
    row = check_registration(event_id, call.from_user.id)
    try:
        tickets = row[2]
        message_text = f'✅ Вы успешно записаны!\n*{event_map[event_id]}*\n📅 {event_date}\n🎟 Билетиков: *{tickets}*\n\n{text_variant}'
        bot.send_message(call.message.chat.id, message_text, 'Markdown')
    except: # Если запись не найдена
        bot.delete_message(call.message.chat.id, call.message.message_id)



@bot.message_handler(commands=['start'])
def handle_start(msg):
    key = msg.text.split()[1] if len(msg.text.split()) > 1 else None # Получаем key, который идет после команды start
    
    if key == None: # Если нажали просто /start
        # ДОДЕЛАТЬ ОТОБРАЖЕНИЕ СОБЫТИЙ ГДЕ ЕСТЬ ЗАПИСЬ У ЮЗЕРА ! ! !
        user_event_list = '⬇️ Список мероприятий, куда вы записаны.'
        for event_id in event_map:
            if db.get_reg_info(event_id, msg.from_user.id):
                row = check_registration(event_id, msg.from_user.id)
                event = event_map[event_id]
                tickets = row[2]
                day = event_id[6:8].lstrip('0')
                month = month_mapping.get(event_id[9:11], 'несуществующего месяца')
                time = event_id[15:].replace('-', ':')
                event_date = f'*{day} {month}* в *{time}*'
                notification_mode = row[3]
                if notification_mode == 1: icon = '🔔'
                elif notification_mode == 2: icon = '🔕'
                else: icon = '🚫'
                user_event_list = user_event_list + f'*\n\n{event}*\n📅 {event_date} ({icon})\n🎟 Билетиков: *{tickets}* ([Изменить](https://t.me/CreativeNM_bot?start={event_id}))'
        bot.send_message(msg.chat.id, user_event_list, 'Markdown', disable_web_page_preview=True)

    elif key in event_map: # Если перешли по ссылке с ключем ивента
        event_date, event_id = get_event_id(key)
        row = check_registration(event_id, msg.from_user.id)
        if row: # Если запись найдена
            tickets = row[2]
            message_text = f'✅ Ваша запись:\n*{event_map[event_id]}*\n📅 {event_date}\n🎟 Билетиков: *{tickets}*'
            markup = menu.change_of_registration(event_id)
            bot.send_message(msg.chat.id, message_text, 'Markdown', reply_markup=markup)
        else: # Если запись не найдена
            message_text = f'*{event_map[event_id]}*\n📅 {event_date}\n\nХотите записаться?'
            markup = menu.event_registration(event_id)
            bot.send_message(msg.chat.id, message_text, 'Markdown', reply_markup=markup)
    else:
        message_text = f'Такого мероприятия не существует 🤷‍♂️\nУточните ссылку 🧐'
        bot.send_message(msg.chat.id, message_text, 'Markdown')


# Запуск бота в нонстоп режиме
bot.infinity_polling()