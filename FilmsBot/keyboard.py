from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import FilmsBot.server as server
from FilmsBot.message import get_text

# todo fix it
keys_users = {}


def clear_keys_users():
    keys_users.clear()


def all_users(username):
    return True


def usernames_keyboard(users=server.get_users()):
    clear_keys_users()
    keyboard = []
    row = []
    user_num = 0
    for user in users:
        if len(row) == 3:
            keyboard.append(row)
            row = []
        user_id = 'USER{}'.format(user_num)
        keys_users[user_id] = user
        row.append(InlineKeyboardButton(user, callback_data=user_id))
        user_num += 1
    if len(row) > 0:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


COMPLETE_BUTTON = 'complete_button'
CONFIRM_BUTTON = 'confirm_button'
CANCEL_BUTTON = 'cancel_button'
USERNAME_BUTTON = 'username_button'
PASSWORD_BUTTON = 'password_button'
TICKED_MARK = 'ticked_mark'
UNTICKED_MARK = 'unticked_mark'
REMOVED_MARK = 'removed_mark'


marked_buttons = set()

list_of_films = set()


def done_marked_buttons():
    marked_buttons.clear()


def tick_keyboard(language_code, user_data=None):
    keyboard = []
    if user_data:
        marked_buttons.add(user_data[4:])
    for lnum in range(10):
        callback_data = 'tick' + str(lnum)
        button_text = (str(lnum) + (get_text(TICKED_MARK, language_code) if str(lnum) in marked_buttons else ''))
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=callback_data,
            )
        ])
    # todo list of films
    keyboard.append([InlineKeyboardButton(get_text(COMPLETE_BUTTON, language_code), callback_data=COMPLETE_BUTTON)])
    return InlineKeyboardMarkup(keyboard)


def untick_keyboard(language_code, user_data=None):
    keyboard = []
    if user_data:
        marked_buttons.add(user_data[6:])
    for lnum in range(10):
        callback_data = 'untick' + str(lnum)
        button_text = (str(lnum) + (get_text(UNTICKED_MARK, language_code) if str(lnum) in marked_buttons else ''))
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=callback_data,
            )
        ])
    # todo list of films
    keyboard.append([InlineKeyboardButton(get_text(COMPLETE_BUTTON, language_code), callback_data=COMPLETE_BUTTON)])
    return InlineKeyboardMarkup(keyboard)


def remove_keyboard(language_code, user_data=None):
    keyboard = []
    if user_data:
        marked_buttons.add(user_data[6:])
    for lnum in range(10):
        callback_data = 'remove' + str(lnum)
        button_text = (str(lnum) + (get_text(REMOVED_MARK, language_code) if str(lnum) in marked_buttons else ''))
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=callback_data,
            )
        ])
    # todo list of films
    keyboard.append([InlineKeyboardButton(get_text(COMPLETE_BUTTON, language_code), callback_data=COMPLETE_BUTTON)])
    return InlineKeyboardMarkup(keyboard)


def change_user_admin_keyboard(language_code):
    keyboard = [
        [
            InlineKeyboardButton(get_text(USERNAME_BUTTON, language_code), callback_data=USERNAME_BUTTON),
            InlineKeyboardButton(get_text(PASSWORD_BUTTON, language_code), callback_data=PASSWORD_BUTTON),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def confirm_admin_keyboard(language_code):
    keyboard = [
        [
            InlineKeyboardButton(get_text(CONFIRM_BUTTON, language_code), callback_data=CONFIRM_BUTTON),
            InlineKeyboardButton(get_text(CANCEL_BUTTON, language_code), callback_data=CANCEL_BUTTON),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
