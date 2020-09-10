from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from message import get_text

MONDAY = 'monday_button'
TUESDAY = 'tuesday_button'
WEDNESDAY = 'wednesday_button'
THURSDAY = 'thursday_button'
FRIDAY = 'friday_button'
SATURDAY = 'saturday_button'


def timetable_keyboard(language_code):
    keyboard = [
        [
            InlineKeyboardButton(text=get_text(MONDAY, language_code), callback_data=MONDAY),
            InlineKeyboardButton(text=get_text(TUESDAY, language_code), callback_data=TUESDAY),
            InlineKeyboardButton(text=get_text(WEDNESDAY, language_code), callback_data=WEDNESDAY),
        ],
        [
            InlineKeyboardButton(text=get_text(THURSDAY, language_code), callback_data=THURSDAY),
            InlineKeyboardButton(text=get_text(FRIDAY, language_code), callback_data=FRIDAY),
            InlineKeyboardButton(text=get_text(SATURDAY, language_code), callback_data=SATURDAY),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
