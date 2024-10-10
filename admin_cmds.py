import re
from datetime import datetime
# Мои модули:
from database import bot, bot_name, event_map, month_mapping
import database as db



@bot.message_handler(func=lambda message: message.text.strip().lower() == 'new event') # Обработчик команды с текстом 'new event'
def handle_event(msg):
    if msg.from_user.id == 696557284:
        bot.send_message(msg.chat.id, 'Вы решили создать ссылку для записи на мероприятие 🤗\nВведите дату мероприятия в формате:\n*ДД-ММ-ГГ*', 'Markdown')
        bot.register_next_step_handler(msg, new_event_step_1_date_request)
    else:
        bot.send_message(msg.chat.id, '🚫 У вас недостаточно прав на создание ссылки для записи на мероприятие.')



def new_event_step_1_date_request(msg):
    user_message = msg.text
    if user_message.lower() == 'cancel':
        bot.send_message(msg.chat.id, 'Вы вышли из режима создания ссылки для записи на мероприятие.')
        return
    
    if re.match(r'^\d{2}-\d{2}-\d{2}$', user_message):
        day, month, year = map(int, user_message.split('-'))
        error = False
        incorrect_date = ''
        if not (1 <= day <= 31):
            incorrect_date = f'{incorrect_date}❌ *Некорректный день*\n'
            error = True
        if not (1 <= month <= 12):
            incorrect_date = f'{incorrect_date}❌ *Некорректный месяц*\n'
            error = True
        if not (24 <= year <= 25):
            incorrect_date = f'{incorrect_date}❌ *Некорректный год*\n'
            error = True
        if error:
            message_text = f'{incorrect_date}\nНе пытайтесь обмануть 🧐\nНе указывайте невозможные даты!\nПопробуйте еще раз или введите *cancel* для отмены. Напоминаю формат:\n*ДД-ММ-ГГ*'
            bot.send_message(msg.chat.id, message_text, 'Markdown')
            bot.register_next_step_handler(msg, new_event_step_1_date_request)
            return
        
        try:
            datetime(year=2000 + year, month=month, day=day)
        except ValueError:
            message_text = '❗️ Укажите существующие даты в диапозоне 2024-2025 годов.'
            bot.send_message(msg.chat.id, message_text, 'Markdown')
            bot.register_next_step_handler(msg, new_event_step_1_date_request)
            return
        
        bot.send_message(msg.chat.id, 'Введите время мероприятия в формате:\n*ЧЧ-ММ*', 'Markdown')
        bot.register_next_step_handler(msg, new_event_step_2_time_request, user_message)
    
    else:
        message_text = '❗️ Неправильный формат даты\nПравильынй формат:\n*ДД-ММ-ГГ*\nПопробуйте снова или введите *cancel* для выхода, если готовы сдаться.'
        bot.send_message(msg.chat.id, message_text, 'Markdown')
        bot.register_next_step_handler(msg, new_event_step_1_date_request)



def new_event_step_2_time_request(msg, date):
    user_message = msg.text
    if user_message.lower() == 'cancel':
        bot.send_message(msg.chat.id, 'Вы вышли из режима создания ссылки для записи на мероприятие.')
        return
    
    if re.match(r'^\d{2}-\d{2}$', user_message):
        hour, minutes = map(int, user_message.split('-'))
        error = False
        incorrect_time = ''
        if not (0 <= hour <= 23):
            incorrect_time = f'{incorrect_time}❌ *Некорректные часы*\n'
            error = True
        if not (0 <= minutes <= 59):
            incorrect_time = f'{incorrect_time}❌ *Некорректные минуты*\n'
            error = True
        if error:
            message_text = f'{incorrect_time}\nОбман ни к чему 🤓\nНе указывайте невозможное время!\nПопробуйте еще раз или введите *cancel* для отмены. Напоминаю формат:\n*ЧЧ-ММ*'
            bot.send_message(msg.chat.id, message_text, 'Markdown')
            bot.register_next_step_handler(msg, new_event_step_2_time_request, date)
            return

        event_id = f'event_{date}_{user_message}'
        day = event_id[6:8].lstrip('0')
        month = month_mapping.get(event_id[9:11], 'несуществующего месяца')
        time = event_id[15:].replace('-', ':')
        event_date = f'{day} {month} в {time}'
        message_text = f'❗️ Проверьте дату мероприятия, если есть ошибка, выйдите, отправив *cancel*, и начните процесс заново.\n\n📅 *{event_date}*\n\nЕсли все верно, напишите название мероприятия ✏️'
        bot.send_message(msg.chat.id, message_text, 'Markdown')
        bot.register_next_step_handler(msg, new_event_step_3_final, event_id, event_date)

    else:
        message_text = '❗️ Неправильный формат времени\nПравильный формат:\n*ЧЧ-ММ*\nПопробуйте снова или введите *cancel* для выхода.'
        bot.send_message(msg.chat.id, message_text, 'Markdown')
        bot.register_next_step_handler(msg, new_event_step_2_time_request, date)
    

def new_event_step_3_final(msg, event_id, event_date):
    user_message = msg.text
    if user_message.lower() == 'cancel':
        bot.send_message(msg.chat.id, 'Вы вышли из режима создания ссылки для записи на мероприятие.')
        return
    else:
        db.add_event_for_admins(event_id, user_message)
        event_map[event_id] = user_message
        message_text = f'✅ Все готово! 🥳\n\nСсылка для записи на мероприятие:\nhttps://t.me/{bot_name}?start={event_id}\n\nБот будет отображать так:\n{user_message}\n📅 {event_date}'
        bot.send_message(msg.chat.id, message_text, disable_web_page_preview=True)
        print(event_map)