import sqlite3
import os
import telebot


bot = telebot.TeleBot('7599854882:AAFUkOqXaCSmNNroYqQlhnP6PBCKgD7Ndr0')

month_mapping = {
    '01': 'января',
    '02': 'февраля',
    '03': 'марта',
    '04': 'апреля',
    '05': 'мая',
    '06': 'июня',
    '07': 'июля',
    '08': 'августа',
    '09': 'сентября',
    '10': 'октября',
    '11': 'ноября',
    '12': 'декабря'
}
event_map = {
    'event_12-10-24_19-00': '🎥 Киноклуб Режиссерский почерк с Настей Ушаковой', 
    'event_19-10-24_19-00': '🎥 Киноклуб с Милой Соколовой', 
    'event_26-10-24_19-00': '🎥 Киноклуб последний в этом месяце', 
    'event_02-11-24_19-00': '🎥 Киноклуб первый в этом месяце'
}


# Функция для подключения к базе данных
def connection_to_database():
    script_dir = os.path.dirname(os.path.realpath(__file__)) # Получаем путь к директории, где находится текущий скрипт
    db_path = os.path.join(script_dir, 'main_database.db') # Формируем полный путь к базе данных с добавлением имени базы данных
    return sqlite3.connect(db_path)


# Изменить конкретную ячейку
def change_cell(target_column: str, new_value, user_id: int, event_id: str, table: str = 'events'):
    with connection_to_database() as conn:
        cursor = conn.cursor()
        SQL_query = f'UPDATE {table} SET {target_column} = ? WHERE user_id = ? AND event_id = ?'
        cursor.execute(SQL_query, (new_value, user_id, event_id))
        conn.commit()


# Проверка записи
def get_reg_info(event_id: str, user_id: int, table: str = 'events') -> bool:
    with connection_to_database() as conn:
        cursor = conn.cursor()
        SQL_query = f'SELECT * FROM {table} WHERE event_id = ? AND user_id = ?'
        cursor.execute(SQL_query, (event_id, user_id))
        row = cursor.fetchone()
        return row


# Записать пользователя на событие
def register_user(
        event_id: str, 
        user_id: int, 
        tickets: int, 
        notification: int = 0, 
        when_to_notify: int = 0, 
        table: str = 'events' 
        ):
    with connection_to_database() as conn:
        cursor = conn.cursor()
        SQL_query = f'SELECT * FROM {table} WHERE event_id = ? AND user_id = ?'
        cursor.execute(SQL_query, (event_id, user_id))
        row = cursor.fetchone()
        if not row:
            SQL_insert = f'INSERT INTO {table} (event_id, user_id, tickets, notification, when_to_notify) VALUES (?, ?, ?, ?, ?)'
            cursor.execute(SQL_insert, (event_id, user_id, tickets, notification, when_to_notify))
            conn.commit()


# Снять запись пользователя на событие
def deregister_user(event_id: str, user_id: int, table: str = 'events'):
    with connection_to_database() as conn:
        cursor = conn.cursor()
        # Проверка наличия строки для удаления
        SQL_check = f'SELECT 1 FROM {table} WHERE event_id = ? AND user_id = ?'
        cursor.execute(SQL_check, (event_id, user_id))
        row = cursor.fetchone()
        if row: # Если строка найдена, то удаляем
            SQL_delete = f'DELETE FROM {table} WHERE event_id = ? AND user_id = ?'
            cursor.execute(SQL_delete, (event_id, user_id))
            conn.commit()