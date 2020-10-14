from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from util import util
from src.text import get_text

from static.buttons import *


def make_button(button, language_code):
    return InlineKeyboardButton(text=get_text(button, language_code).text(), callback_data=button)


def make_timetable_button(weekday, current_state, language_code):
    return InlineKeyboardButton(
        text=get_text(WEEKDAY_BUTTON % {'weekday': weekday}, language_code).text(),
        callback_data=TIMETABLE_BUTTON % dict(current_state, weekday=weekday),
    )


def timetable_keyboard(weekday, attendance, week_parity, language_code):
    not_attendance = util.to_not_attendance(attendance)
    not_week_parity = util.to_not_week_parity(week_parity)
    current_state = {
        'attendance': attendance,
        'week_parity': week_parity,
        'weekday': weekday,
    }
    attendance_callback = TIMETABLE_BUTTON % dict(current_state, attendance=not_attendance)
    week_parity_callback = TIMETABLE_BUTTON % dict(current_state, week_parity=not_week_parity)
    keyboard = [
        [
            make_timetable_button('monday', current_state, language_code),
            make_timetable_button('tuesday', current_state, language_code),
            make_timetable_button('wednesday', current_state, language_code),
        ],
        [
            make_timetable_button('thursday', current_state, language_code),
            make_timetable_button('friday', current_state, language_code),
            make_timetable_button('saturday', current_state, language_code),
        ],
        [
            InlineKeyboardButton(
                text=get_text(f'timetable_{not_week_parity}_week_button', language_code).text(),
                callback_data=week_parity_callback,
            ),
            InlineKeyboardButton(
                text=get_text(f'timetable_{not_attendance}_attendance_button', language_code).text(),
                callback_data=attendance_callback,
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def parameters_keyboard(language_code):
    keyboard = [
        [
            make_button(NAME, language_code),
            make_button(ATTENDANCE, language_code),
            make_button(COURSES, language_code),
        ],
        [
            make_button(EXIT_PARAMETERS, language_code),
            make_button(EVERYDAY_MESSAGE, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def mailing_keyboard(mailing_status, notification_status, language_code):
    keyboard = [
        [
            make_button((ALLOW_MESSAGE if mailing_status == 'forbidden' else FORBID_MESSAGE), language_code),
            make_button((DISABLE_NOTIFICATION_MESSAGE if notification_status == 'enabled'
                         else ENABLE_NOTIFICATION_MESSAGE), language_code),
        ],
        [
            make_button(MESSAGE_TIME, language_code),
            make_button(TZINFO, language_code),
        ],
        [
            make_button(EXIT_PARAMETERS, language_code),
            make_button(PARAMETERS_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def courses_keyboard(language_code):
    keyboard = [
        [
            make_button(ENG_GROUP, language_code),
            make_button(SP_TYPE, language_code),
            make_button(OS_TYPE, language_code),
        ],
        [
            make_button(EXIT_PARAMETERS, language_code),
            make_button(PARAMETERS_RETURN, language_code),
            make_button(HISTORY_GROUP, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def os_keyboard(language_code):
    keyboard = [
        [
            make_button(OS_ADV, language_code),
            make_button(OS_LITE, language_code),
        ],
        [
            make_button(EXIT_PARAMETERS, language_code),
            make_button(COURSES_RETURN, language_code),
            make_button(OS_ALL, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def sp_keyboard(language_code):
    keyboard = [
        [
            make_button(SP_KOTLIN, language_code),
            make_button(SP_WEB, language_code),
        ],
        [
            make_button(SP_ANDROID, language_code),
            make_button(SP_IOS, language_code),
        ],
        [
            make_button(SP_CPP, language_code),
            make_button(SP_ALL, language_code),
        ],
        [
            make_button(EXIT_PARAMETERS, language_code),
            make_button(COURSES_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def eng1_keyboard(language_code):
    keyboard = [
        [
            make_button(ENG_B11_1, language_code),
            make_button(ENG_B11_2, language_code),
            make_button(ENG_B12_1, language_code),
            make_button(ENG_B12_2, language_code),
        ],
        [
            make_button(ENG_B2_1, language_code),
            make_button(ENG_B2_2, language_code),
            make_button(ENG_NEXT, language_code),
        ],
        [
            make_button(EXIT_PARAMETERS, language_code),
            make_button(COURSES_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def eng2_keyboard(language_code):
    keyboard = [
        [
            make_button(ENG_C2_1, language_code),
            make_button(ENG_C2_2, language_code),
            make_button(ENG_C2_3, language_code),
            make_button(ENG_C1_1, language_code),
            make_button(ENG_C1_2, language_code),
        ],
        [
            make_button(ENG_B2_3, language_code),
            make_button(ENG_ALL, language_code),
            make_button(ENG_PREV, language_code),
        ],
        [
            make_button(EXIT_PARAMETERS, language_code),
            make_button(COURSES_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def history_keyboard(language_code):
    keyboard = [
        [
            make_button(HISTORY_INTERNATIONAL, language_code),
        ],
        [
            make_button(HISTORY_SCIENCE, language_code),
        ],
        [
            make_button(HISTORY_EU_PROBLEMS, language_code),
        ],
        [
            make_button(HISTORY_CULTURE, language_code),
        ],
        [
            make_button(HISTORY_REFORMS, language_code),
        ],
        [
            make_button(HISTORY_STATEHOOD, language_code),
        ],
        [
            make_button(HISTORY_ALL, language_code),
        ],
        [
            make_button(EXIT_PARAMETERS, language_code),
            make_button(COURSES_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def attendance_keyboard(language_code):
    keyboard = [
        [
            make_button(ATTENDANCE_ONLINE, language_code),
            make_button(ATTENDANCE_OFFLINE, language_code),
            make_button(ATTENDANCE_BOTH, language_code),
        ],
        [
            make_button(EXIT_PARAMETERS, language_code),
            make_button(PARAMETERS_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def subject_keyboard(sub_name, page, attendance, language_code):
    not_page = util.to_not_page(page)
    not_attendance = util.to_not_attendance(attendance)
    current_state = {
        'page': page,
        'attendance': attendance,
        'sub_name': sub_name
    }
    attendance_callback = SUBJECT_BUTTON % dict(current_state, attendance=not_attendance)
    page_callback = SUBJECT_BUTTON % dict(current_state, page=not_page)
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text(f'subject_{not_page}_page_button', language_code).text(),
                callback_data=page_callback,
            ),
            InlineKeyboardButton(
                text=get_text(f'subject_{not_attendance}_attendance_button', language_code).text(),
                callback_data=attendance_callback,
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def help_keyboard(page_type, language_code):
    button = (HELP_MAIN if page_type == 'additional' else HELP_ADDITIONAL)
    keyboard = [
        [
            make_button(button, language_code)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
