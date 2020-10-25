from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from util import util
from src.text import get_text

from static import consts, buttons


def make_button(button, language_code):
    """Make standard Inline Button"""
    return InlineKeyboardButton(text=get_text(button, language_code).text(), callback_data=button)


def make_timetable_button(weekday, current_state, language_code):
    """
    Make timetable button according to current page state
    current_state: dict with 3 parameters: attendance, week_parity, weekday
    """
    return InlineKeyboardButton(
        text=get_text(buttons.WEEKDAY_BUTTON % {consts.WEEKDAY: weekday}, language_code).text(),
        callback_data=buttons.TIMETABLE_BUTTON % dict(current_state, weekday=weekday),
    )


def timetable_keyboard(weekday, attendance, week_parity, language_code):
    """
    Make weekday timetable key board
    3 rows of buttons: 2 for weekdays and 1 to change attendance and week_parity
    """

    # for weekday buttons current_state is the same except weekday
    current_state = {
        consts.ATTENDANCE: attendance,
        consts.WEEK_PARITY: week_parity,
        consts.WEEKDAY: weekday,
    }
    # invert attendance and week_parity
    not_attendance = util.to_not_attendance(attendance)
    not_week_parity = util.to_not_week_parity(week_parity)

    # for attendance and week parity buttons callback changing respectively, weekday stays the same
    attendance_callback = buttons.TIMETABLE_BUTTON % dict(current_state, attendance=not_attendance)
    week_parity_callback = buttons.TIMETABLE_BUTTON % dict(current_state, week_parity=not_week_parity)
    keyboard = [
        [
            make_timetable_button(consts.MONDAY, current_state, language_code),
            make_timetable_button(consts.TUESDAY, current_state, language_code),
            make_timetable_button(consts.WEDNESDAY, current_state, language_code),
            make_timetable_button(consts.THURSDAY, current_state, language_code),
            make_timetable_button(consts.FRIDAY, current_state, language_code),
            make_timetable_button(consts.SATURDAY, current_state, language_code),
        ],
        [
            # buttons names and callback according to current states
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
    """Make keyboard for parameters"""
    keyboard = [
        [
            make_button(buttons.NAME, language_code),
            make_button(buttons.ATTENDANCE, language_code),
            make_button(buttons.COURSES, language_code),
        ],
        [
            make_button(buttons.EXIT_PARAMETERS, language_code),
            make_button(buttons.EVERYDAY_MESSAGE, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def mailing_keyboard(mailing_status, notification_status, language_code):
    """Make keyboard for mailing parameters"""
    keyboard = [
        [
            # buttons names and callback according to current states
            make_button(
                (buttons.ALLOW_MESSAGE
                 if mailing_status == consts.MAILING_FORBIDDEN
                 else buttons.FORBID_MESSAGE),
                language_code,
            ),
            make_button(
                (buttons.DISABLE_NOTIFICATION_MESSAGE
                 if notification_status == consts.NOTIFICATION_ENABLED
                 else buttons.ENABLE_NOTIFICATION_MESSAGE),
                language_code,
            ),
        ],
        [
            make_button(buttons.MESSAGE_TIME, language_code),
            make_button(buttons.TZINFO, language_code),
        ],
        [
            make_button(buttons.EXIT_PARAMETERS, language_code),
            make_button(buttons.PARAMETERS_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def courses_keyboard(language_code):
    """Make keyboard for changing courses in parameters"""
    keyboard = [
        [
            make_button(buttons.ENG_GROUP, language_code),
            make_button(buttons.SP_TYPE, language_code),
            make_button(buttons.OS_TYPE, language_code),
        ],
        [
            make_button(buttons.EXIT_PARAMETERS, language_code),
            make_button(buttons.PARAMETERS_RETURN, language_code),
            make_button(buttons.HISTORY_GROUP, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def os_keyboard(language_code):
    """Make keyboard for changing os in parameters"""
    keyboard = [
        [
            make_button(buttons.OS_ADV, language_code),
            make_button(buttons.OS_LITE, language_code),
        ],
        [
            make_button(buttons.EXIT_PARAMETERS, language_code),
            make_button(buttons.COURSES_RETURN, language_code),
            make_button(buttons.OS_ALL, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def sp_keyboard(language_code):
    """Make keyboard for changing sp in parameters"""
    keyboard = [
        [
            make_button(buttons.SP_KOTLIN, language_code),
            make_button(buttons.SP_WEB, language_code),
        ],
        [
            make_button(buttons.SP_ANDROID, language_code),
            make_button(buttons.SP_IOS, language_code),
        ],
        [
            make_button(buttons.SP_CPP, language_code),
            make_button(buttons.SP_ALL, language_code),
        ],
        [
            make_button(buttons.EXIT_PARAMETERS, language_code),
            make_button(buttons.COURSES_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def eng1_keyboard(language_code):
    """Make first keyboard for changing eng in parameters"""
    keyboard = [
        [
            make_button(buttons.ENG_B11_1, language_code),
            make_button(buttons.ENG_B11_2, language_code),
            make_button(buttons.ENG_B12_1, language_code),
            make_button(buttons.ENG_B12_2, language_code),
        ],
        [
            make_button(buttons.ENG_B2_1, language_code),
            make_button(buttons.ENG_B2_2, language_code),
            make_button(buttons.ENG_NEXT, language_code),
        ],
        [
            make_button(buttons.EXIT_PARAMETERS, language_code),
            make_button(buttons.COURSES_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def eng2_keyboard(language_code):
    """Make second keyboard for changing eng in parameters"""
    keyboard = [
        [
            make_button(buttons.ENG_C2_1, language_code),
            make_button(buttons.ENG_C2_2, language_code),
            make_button(buttons.ENG_C2_3, language_code),
            make_button(buttons.ENG_C1_1, language_code),
            make_button(buttons.ENG_C1_2, language_code),
        ],
        [
            make_button(buttons.ENG_B2_3, language_code),
            make_button(buttons.ENG_ALL, language_code),
            make_button(buttons.ENG_PREV, language_code),
        ],
        [
            make_button(buttons.EXIT_PARAMETERS, language_code),
            make_button(buttons.COURSES_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def history_keyboard(language_code):
    """Make keyboard for changing history in parameters"""
    keyboard = [
        [
            make_button(buttons.HISTORY_INTERNATIONAL, language_code),
        ],
        [
            make_button(buttons.HISTORY_SCIENCE, language_code),
        ],
        [
            make_button(buttons.HISTORY_EU_PROBLEMS, language_code),
        ],
        [
            make_button(buttons.HISTORY_CULTURE, language_code),
        ],
        [
            make_button(buttons.HISTORY_REFORMS, language_code),
        ],
        [
            make_button(buttons.HISTORY_STATEHOOD, language_code),
        ],
        [
            make_button(buttons.HISTORY_ALL, language_code),
        ],
        [
            make_button(buttons.EXIT_PARAMETERS, language_code),
            make_button(buttons.COURSES_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def attendance_keyboard(language_code):
    """Make keyboard for changing attendance in parameters"""
    keyboard = [
        [
            make_button(buttons.ATTENDANCE_ONLINE, language_code),
            make_button(buttons.ATTENDANCE_OFFLINE, language_code),
            make_button(buttons.ATTENDANCE_BOTH, language_code),
        ],
        [
            make_button(buttons.EXIT_PARAMETERS, language_code),
            make_button(buttons.PARAMETERS_RETURN, language_code),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def subject_keyboard(subject, page, attendance, language_code):
    """Make keyboard for subject pages: main and timetable page"""

    # current page, attendance and subject
    current_state = {
        consts.PAGE: page,
        consts.ATTENDANCE: attendance,
        consts.SUBJECT: subject
    }
    # invert states
    not_page = util.to_not_help_page(page)
    not_attendance = util.to_not_attendance(attendance)

    attendance_callback = buttons.SUBJECT % dict(current_state, attendance=not_attendance)
    page_callback = buttons.SUBJECT % dict(current_state, page=not_page)
    keyboard = [
        [
            # buttons names and callback according to current states
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
    """Make keyboard for help page: main and additional"""
    button = (buttons.HELP_MAIN if page_type == consts.ADDITIONAL_PAGE else buttons.HELP_ADDITIONAL)
    keyboard = [
        [
            make_button(button, language_code)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
