from telegram import Update, error
from telegram.ext import CallbackContext

from message import get_text
from buttons import *

import keyboard
import user_parameters


def parameters_callback(update: Update, context: CallbackContext, data, language_code):
    if data in MAIN_SET:
        return __main_callback(update, context, data, language_code)
    elif data in COURSES_SET:
        return __chg_course(update, context, data, language_code)
    elif is_course_update(data):
        return __update_course(update, context, data, language_code)
    elif data in ATTENDANCE_SET:
        return __update_attendance(update, context, data, language_code)


def __main_callback(update: Update, context: CallbackContext, data, language_code):
    if data == PARAMETERS_RETURN:
        return __return_callback(update, context, language_code)
    elif data == EVERYDAY_MESSAGE:
        return __everyday_msg_callback(update, context, language_code)
    elif data == COURSES:
        return __courses_callback(update, context, language_code)
    elif data == NAME:
        pass
    elif data == ATTENDANCE:
        return __chg_parameters_page(update, 'attendance', keyboard.attendance_keyboard, language_code)


def __return_callback(update: Update, context: CallbackContext, language_code):
    user_id = update.effective_user.id
    try:
        update.callback_query.edit_message_text(
            text=get_text('parameters_text', language_code) % user_parameters.get_user(user_id),
            reply_markup=keyboard.parameters_keyboard(language_code),
        )
    except error.BadRequest:
        pass


def __everyday_msg_callback(update: Update, context: CallbackContext, language_code):
    user_id = update.effective_user.id
    current_status = user_parameters.get_user_status(user_id)
    update.callback_query.edit_message_text(
        text=get_text('everyday_message_text', language_code),
        reply_markup=keyboard.everyday_message_keyboard(current_status, language_code),
    )


def __courses_callback(update: Update, context: CallbackContext, language_code):
    update.callback_query.edit_message_text(
        text=get_text('courses_text', language_code),
        reply_markup=keyboard.courses_keyboard(language_code),
    )


def __chg_page_eng(update: Update, eng_keyboard, language_code):
    update.callback_query.edit_message_text(
        text=get_text('eng_course_text', language_code),
        reply_markup=eng_keyboard(language_code),
    )


def __get_button_name(data):
    for a in range(len(data)):
        if data[a] == '_':
            return data[:a]


def __update_course(update: Update, context: CallbackContext, data, language_code):
    if data == ENG_NEXT:
        return __chg_page_eng(update, keyboard.eng2_keyboard, language_code)
    elif data == ENG_PREV:
        return __chg_page_eng(update, keyboard.eng1_keyboard, language_code)

    user_id = update.effective_user.id
    subject = __get_button_name(data)
    new_course = data[:-7]
    user_parameters.set_user_course(user_id, subject, new_course)
    return __courses_callback(update, context, language_code)


def __chg_parameters_page(update: Update, course_name, parameters_keyboard, language_code):
    update.callback_query.edit_message_text(
        text=get_text(f'{course_name}_parameters_text', language_code),
        reply_markup=parameters_keyboard(language_code),
    )


def __chg_course(update: Update, context: CallbackContext, data, language_code):
    if data == OS_TYPE:
        return __chg_parameters_page(update, 'os', keyboard.os_keyboard, language_code)
    elif data == SP_TYPE:
        return __chg_parameters_page(update, 'sp', keyboard.sp_keyboard, language_code)
    elif data == HISTORY_GROUP:
        return __chg_parameters_page(update, 'history', keyboard.history_keyboard, language_code)
    elif data == ENG_GROUP:
        return __chg_parameters_page(update, 'eng', keyboard.eng1_keyboard, language_code)
    elif data == COURSES_RETURN:
        return __courses_callback(update, context, language_code)


def __update_attendance(update: Update, context: CallbackContext, data, language_code):
    user_id = update.effective_user.id
    new_attendance = __get_button_name(data)
    user_parameters.set_user_attendance(user_id, new_attendance)
    return __return_callback(update, context, language_code)
