from telegram import Update
from telegram.ext import CallbackContext

from message import get_text
from buttons import *

import keyboard
import user_parameters


def parameters_callback(update: Update, context: CallbackContext, data, language_code):
    if data == PARAMETERS_RETURN:
        return __return_callback(update, context, language_code)
    elif data == EVERYDAY_MESSAGE:
        return __everyday_msg_callback(update, context, language_code)
    elif data == COURSES:
        return __courses_callback(update, context, language_code)
    elif data == NAME:
        pass
    elif data == ATTENDANCE:
        pass


def __return_callback(update: Update, context: CallbackContext, language_code):
    user_id = update.effective_user.id
    update.callback_query.edit_message_text(
        text=get_text('parameters_text', language_code) % user_parameters.get_user(user_id),
        reply_markup=keyboard.parameters_keyboard(language_code),
    )


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


def __get_subject(data):
    for a in range(len(data)):
        if data[a] == '_':
            return data[:a]


def update_course(update: Update, context: CallbackContext, data, language_code):
    if data == ENG_NEXT:
        return __chg_page_eng(update, keyboard.eng2_keyboard, language_code)
    elif data == ENG_PREV:
        return __chg_page_eng(update, keyboard.eng1_keyboard, language_code)

    user_id = update.effective_user.id
    subject = __get_subject(data)
    new_course = data[:-7]
    user_parameters.set_course(user_id, subject, new_course)
    return __courses_callback(update, context, language_code)


def __chg_course_page(update: Update, course_name, course_keyboard, language_code):
    update.callback_query.edit_message_text(
        text=get_text(f'{course_name}_course_text', language_code),
        reply_markup=course_keyboard(language_code),
    )


def chg_course(update: Update, context: CallbackContext, data, language_code):
    if data == OS_TYPE:
        return __chg_course_page(update, 'os', keyboard.os_keyboard, language_code)
    elif data == SP_TYPE:
        return __chg_course_page(update, 'sp', keyboard.sp_keyboard, language_code)
    elif data == HISTORY_GROUP:
        return __chg_course_page(update, 'history', keyboard.history_keyboard, language_code)
    elif data == ENG_GROUP:
        return __chg_course_page(update, 'eng', keyboard.eng1_keyboard, language_code)
    elif data == COURSES_RETURN:
        return __courses_callback(update, context, language_code)
