from telegram import Update, error
from telegram.ext import CallbackContext

from log import log_handler
from message import get_text
from buttons import *

import keyboard
import user_parameters

# ConversationHandler's states:
MAIN_LVL, NAME_LVL, TIME_LVL, TZINFO_LVL = range(4)


@log_handler
def parameters(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    user_id = update.effective_user.id
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('parameters_text', language_code) % user_parameters.get_user(user_id),
        reply_markup=keyboard.parameters_keyboard(language_code),
    )
    return MAIN_LVL


def manage_callback_query(update: Update):
    language_code = update.effective_user.language_code
    query = update.callback_query
    data = query.data
    query.answer()
    return data, language_code


@log_handler
def __chg_parameters_page(update: Update, page_name, language_code, parameters_keyboard=None, ret_lvl=MAIN_LVL):
    update.callback_query.edit_message_text(
        text=get_text(f'{page_name}_parameters_text', language_code),
        reply_markup=(parameters_keyboard(language_code) if parameters_keyboard else None),
    )
    return ret_lvl


def parameters_callback(update: Update, context: CallbackContext):
    data, language_code = manage_callback_query(update)
    if data in MAIN_SET:
        return __main_callback(update, context, data, language_code)
    elif data in COURSES_SET:
        return __chg_course(update, context, data, language_code)
    elif is_course_update(data):
        return __update_course(update, context, data, language_code)
    elif data in ATTENDANCE_SET:
        return __update_attendance(update, context, data, language_code)
    elif data in EVERYDAY_MESSAGE_SET:
        return __update_everyday_msg(update, context, data, language_code)


def __main_callback(update: Update, context: CallbackContext, data, language_code):
    if data == PARAMETERS_RETURN:
        return __return_callback(update, context, language_code)
    elif data == EVERYDAY_MESSAGE:
        return __everyday_msg_callback(update, context, language_code)
    elif data == COURSES:
        return __chg_parameters_page(update, 'courses', language_code, keyboard.courses_keyboard)
    elif data == NAME:
        return __chg_parameters_page(update, 'name', language_code=language_code, ret_lvl=NAME_LVL)
    elif data == ATTENDANCE:
        return __chg_parameters_page(update, 'attendance', language_code, keyboard.attendance_keyboard)


@log_handler
def __return_callback(update: Update, context: CallbackContext, language_code):
    user_id = update.effective_user.id
    try:
        update.callback_query.edit_message_text(
            text=get_text('parameters_text', language_code) % user_parameters.get_user(user_id),
            reply_markup=keyboard.parameters_keyboard(language_code),
        )
    finally:
        return MAIN_LVL


@log_handler
def __everyday_msg_callback(update: Update, context: CallbackContext, language_code, edited=''):
    user_id = update.effective_user.id
    current_status = user_parameters.get_user_message_status(user_id)
    update.callback_query.edit_message_text(
        text=get_text('everyday_message_text', language_code).format(edited),
        reply_markup=keyboard.everyday_message_keyboard(current_status, language_code),
    )
    return MAIN_LVL


def __get_button_name(data):
    for a in range(len(data)):
        if data[a] == '_':
            return data[:a]


def __update_course(update: Update, context: CallbackContext, data, language_code):
    if data == ENG_NEXT:
        return __chg_parameters_page(update, 'eng', language_code, keyboard.eng2_keyboard)
    elif data == ENG_PREV:
        return __chg_parameters_page(update, 'eng', language_code, keyboard.eng1_keyboard)

    user_id = update.effective_user.id
    subject = __get_button_name(data)
    new_course = data[:-7]
    user_parameters.set_user_course(user_id, subject, new_course)
    return __chg_parameters_page(update, 'courses', language_code, keyboard.courses_keyboard)


def __chg_course(update: Update, context: CallbackContext, data, language_code):
    if data == OS_TYPE:
        return __chg_parameters_page(update, 'os', language_code, keyboard.os_keyboard)
    elif data == SP_TYPE:
        return __chg_parameters_page(update, 'sp', language_code, keyboard.sp_keyboard)
    elif data == HISTORY_GROUP:
        return __chg_parameters_page(update, 'history', language_code, keyboard.history_keyboard)
    elif data == ENG_GROUP:
        return __chg_parameters_page(update, 'eng', language_code, keyboard.eng1_keyboard)
    elif data == COURSES_RETURN:
        return __chg_parameters_page(update, 'courses', language_code, keyboard.courses_keyboard)


def __update_attendance(update: Update, context: CallbackContext, data, language_code):
    user_id = update.effective_user.id
    new_attendance = __get_button_name(data)
    user_parameters.set_user_attendance(user_id, new_attendance)
    return __return_callback(update, context, language_code)


@log_handler
def name(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    new_name = update.message.text
    user_parameters.set_user_name(user_id, new_name)
    return parameters(update, context)


def __update_everyday_msg(update, context, data, language_code):
    user_id = update.effective_user.id
    if data == ALLOW_MESSAGE or data == FORBID_MESSAGE:
        new_status = __get_button_name(data)
        user_parameters.set_user_message_status(user_id, new_status)
        return __everyday_msg_callback(update, context, language_code, f'message status updated: {new_status}')
    elif data == TZINFO:
        return __chg_parameters_page(update, 'tzinfo', language_code=language_code, ret_lvl=TZINFO_LVL)
    elif data == MESSAGE_TIME:
        return __chg_parameters_page(update, 'time', language_code=language_code, ret_lvl=TIME_LVL)


@log_handler
def tzinfo(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    new_tzinfo = update.message.text
    if user_parameters.valid_tzinfo(new_tzinfo):
        user_id = update.effective_user.id
        user_parameters.set_tzinfo(user_id, new_tzinfo)
        current_status = user_parameters.get_user_message_status(user_id)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_text('everyday_message_text', language_code).format('tzinfo updated'),
            reply_markup=keyboard.everyday_message_keyboard(current_status, language_code),
        )
        return MAIN_LVL
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('tzinfo_error_parameters_text', language_code),
    )
    return TZINFO_LVL
