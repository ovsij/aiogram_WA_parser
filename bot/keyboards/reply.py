from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def reply_kb_phone():
    text = 'Нажмите на кнопку внизу экрана, чтобы поделиться номером телефона.'
    reply_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    reply_kb.add(KeyboardButton('Поделиться номером телефона', request_contact=True))
    return text, reply_kb
    