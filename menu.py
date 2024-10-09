from telebot import types



def event_registration(event_id):
    markup = types.InlineKeyboardMarkup()
    btn01 = types.InlineKeyboardButton('Хочу!', callback_data=f'reg_{event_id}')
    btn02 = types.InlineKeyboardButton('Не хочу 😁', callback_data=f'cancel_reg_{event_id}')
    markup.row(btn01, btn02)
    return markup


def how_many_with_you(event_id):
    markup = types.InlineKeyboardMarkup()
    btn01 = types.InlineKeyboardButton('Я один', callback_data=f'visitors_1_{event_id}')
    btn02 = types.InlineKeyboardButton('Нас двое', callback_data=f'visitors_2_{event_id}')
    btn03 = types.InlineKeyboardButton('3', callback_data=f'visitors_3_{event_id}')
    btn04 = types.InlineKeyboardButton('4', callback_data=f'visitors_4_{event_id}')
    btn05 = types.InlineKeyboardButton('5', callback_data=f'visitors_5_{event_id}')
    markup.row(btn01, btn02)
    markup.row(btn03, btn04, btn05)
    return markup


def notification(event_id):
    markup = types.InlineKeyboardMarkup()
    btn01 = types.InlineKeyboardButton('Да 🔔', callback_data=f'notify_1_{event_id}')
    btn02 = types.InlineKeyboardButton('Нет 🚫', callback_data=f'notify_0_{event_id}')
    btn03 = types.InlineKeyboardButton('Да, но беззвучно 🔕', callback_data=f'notify_2_{event_id}')
    markup.row(btn01, btn02)
    markup.row(btn03)
    return markup


def change_of_registration(event_id):
    markup = types.InlineKeyboardMarkup()
    btn01 = types.InlineKeyboardButton('Изменить количество билетов', callback_data=f'new_tickets_{event_id}')
    btn02 = types.InlineKeyboardButton('Отменить запись', callback_data=f'cancel_reg_{event_id}')
    btn03 = types.InlineKeyboardButton('Закрыть', callback_data=f'close_dereg')
    markup.row(btn01)
    markup.row(btn02, btn03)
    return markup