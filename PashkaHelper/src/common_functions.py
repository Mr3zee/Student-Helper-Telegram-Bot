from telegram.ext import CallbackContext, MessageHandler, CommandHandler
from telegram import Update

import src.keyboard as keyboard
import src.database as database
from src import util
from src.timetable import get_timetable_by_index
from src.time_management import get_weekday
from src.log import log_function
from src.text import get_text

from datetime import timedelta
import logging

MESSAGE, COMMAND = range(2)

logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)


def send_today_timetable(context: CallbackContext, user_id, chat_id, language_code,
                         disable_notification=False):
    attendance, utcoffset = database.get_user_attrs(['attendance', 'utcoffset'], user_id=user_id).values()
    text = get_timetable_by_index(
        day=get_weekday(timedelta(hours=utcoffset)),
        subject_names=database.get_user_subject_names(user_id),
        attendance=attendance,
        language_code=language_code,
    )
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard.timetable_keyboard(language_code=language_code),
        disable_notification=disable_notification,
    )


def simple_handler(name, type, command=None, filters=None, reply_markup=None, ret_lvl=None):
    @log_function
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        chat_id = update.effective_chat.id

        text = get_text(f'{name}_text', language_code).text()

        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        )
        return ret_lvl

    if type == COMMAND:
        ret_handler = CommandHandler(command=(command if command else name), callback=inner)
    elif type == MESSAGE:
        ret_handler = MessageHandler(filters=filters, callback=inner)
    else:
        raise ValueError('Unsupported hdl type')
    return ret_handler


def manage_callback_query(update: Update):
    language_code = update.effective_user.language_code
    query = update.callback_query
    data = query.data
    query.answer()
    return data, language_code


def send_message(context: CallbackContext, text, language_code, user_nik=None, chat_id=None):
    chat_id = database.get_user_attr('chat_id', user_nik=user_nik) if chat_id is None else chat_id
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('notification_admin_text', language_code).text({'text': text}),
    )


def send_message_to_all(context: CallbackContext, text, sender_id, language_code):
    chat_ids = database.gat_all_attrs('chat_id')
    for chat_id in chat_ids:
        if chat_id == sender_id:
            continue
        send_message(context, text, chat_id=chat_id, language_code=language_code)
