from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import FilmsBot.data as data
import FilmsBot.message as message

# todo fix it
keys_users = {}


def clear_keys_users():
    keys_users.clear()


def all_users(username):
    return True


def usernames_keyboard(users=data.get_users()):
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
USERNAME_BUTTON = 'username'
PASSWORD_BUTTON = 'password'

keyboard_buttons = {
    COMPLETE_BUTTON: message.complete_button,
    CONFIRM_BUTTON: message.confirm_button,
    CANCEL_BUTTON: message.cancel_button,
    USERNAME_BUTTON: message.username_button,
    PASSWORD_BUTTON: message.password_button,
}

marked_buttons = set()

list_of_films = set()


def done_marked_buttons():
    marked_buttons.clear()


def tick_keyboard(user_data=None):
    keyboard = []
    if user_data:
        marked_buttons.add(user_data[4:])
    for lnum in range(10):
        callback_data = 'tick' + str(lnum)
        button_text = (str(lnum) + (message.ticked_mark if str(lnum) in marked_buttons else ''))
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=callback_data,
            )
        ])
    # todo list of films
    keyboard.append([InlineKeyboardButton(keyboard_buttons[COMPLETE_BUTTON], callback_data=COMPLETE_BUTTON)])
    return InlineKeyboardMarkup(keyboard)


def untick_keyboard(user_data=None):
    keyboard = []
    if user_data:
        marked_buttons.add(user_data[6:])
    for lnum in range(10):
        callback_data = 'untick' + str(lnum)
        button_text = (str(lnum) + (message.unticked_mark if str(lnum) in marked_buttons else ''))
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=callback_data,
            )
        ])
    # todo list of films
    keyboard.append([InlineKeyboardButton(keyboard_buttons[COMPLETE_BUTTON], callback_data=COMPLETE_BUTTON)])
    return InlineKeyboardMarkup(keyboard)


def remove_keyboard(user_data=None):
    keyboard = []
    if user_data:
        marked_buttons.add(user_data[6:])
    for lnum in range(10):
        callback_data = 'remove' + str(lnum)
        button_text = (str(lnum) + (message.removed_mark if str(lnum) in marked_buttons else ''))
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=callback_data,
            )
        ])
    # todo list of films
    keyboard.append([InlineKeyboardButton(keyboard_buttons[COMPLETE_BUTTON], callback_data=COMPLETE_BUTTON)])
    return InlineKeyboardMarkup(keyboard)


def change_user_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(keyboard_buttons[USERNAME_BUTTON], callback_data=USERNAME_BUTTON),
            InlineKeyboardButton(keyboard_buttons[PASSWORD_BUTTON], callback_data=PASSWORD_BUTTON),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def confirm_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(keyboard_buttons[CONFIRM_BUTTON], callback_data=CONFIRM_BUTTON),
            InlineKeyboardButton(keyboard_buttons[CANCEL_BUTTON], callback_data=CANCEL_BUTTON),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
