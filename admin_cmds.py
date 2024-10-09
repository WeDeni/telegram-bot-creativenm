from database import bot
import re


# ДОБАВИТЬ КОМАНДУ ДЛЯ ДОБАВЛЕНИЯ СОБЫТИЯ В КАРТУ СОБЫТИЙ

# ДОБАВИТЬ КОМАНДУ ДЛЯ ИЗМЕНЕНИЯ СОБЫТИЯ В КАРТЕ СОБЫТИЙ

# ДОБАВИТЬ КАОМНДУ ДЛЯ УДАЛЕНИЯ СОБЫТИЯ В КАРТЕ СОБЫТИЙ

# ДОБАВИТЬ КАОМНДУ ДЛЯ УДАЛЕНИЯ УСТАРЕВШИХ СОБЫТИй В КАРТЕ СОБЫТИЙ
# Пусть выпадает список событий для удаления, я жму ПОДТВЕРДИТЬ или ОТКОЛНИТЬ


@bot.message_handler(func=lambda message: message.text.strip().lower() == 'new event') # Обработчик команды с текстом 'new event'
def handle_event(msg):
    if msg.from_user.id == 696557284:
        bot.send_message(msg.chat.id, 'Вы решили создать ссылку на мероприятие. Введите дату мероприятия в формате ДД-ММ-ГГ.')
        bot.register_next_step_handler(msg, step_1_date_request) # Переход к запросу даты
    else:
        bot.send_message(msg.chat.id, 'У вас недостаточно прав на создание ссылки для записи на мероприятие.')


def step_1_date_request(msg): # Запрашиваем дату
    date = msg.text
    if re.match(r'^\d{2}-\d{2}-\d{2}$', date): # Проверяем соответствие формату даты ДД-ММ-ГГ
        bot.send_message(msg.chat.id, 'Введите время мероприятия в формате ЧЧ-ММ.')
        bot.register_next_step_handler(msg, step_2_time_request, date) # Переход к запросу времени, передаем дату
    else:
        bot.send_message(msg.chat.id, 'Неправильный формат даты. Попробуйте снова.')
        bot.register_next_step_handler(msg, step_1_date_request) # Повторно запрашиваем дату


def step_2_time_request(msg, date): # Запрашиваем время
    time = msg.text
    if re.match(r'^\d{2}-\d{2}$', time): # Проверяем соответствие формату времени ЧЧ-ММ
        event = f'event_{date}_{time}'
        bot.send_message(msg.chat.id, f'Ссылка для записи на мероприятие:\nhttps://t.me/CreativeNM_bot?start={event}')
    else:
        bot.send_message(msg.chat.id, 'Неправильный формат времени. Попробуйте снова.')
        bot.register_next_step_handler(msg, step_2_time_request, date) # Повторно запрашиваем время