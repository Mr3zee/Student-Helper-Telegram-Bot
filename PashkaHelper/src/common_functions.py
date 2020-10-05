from telegram.ext import CallbackContext, MessageHandler, CommandHandler
from telegram import Update

from src import keyboard, database
from src.timetable import get_timetable_by_index, get_subject_timetable
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


def simple_handler(name, type, command=None, filters=None, get_reply_markup=None, ret_lvl=None):
    @log_function
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        chat_id = update.effective_chat.id

        text = get_text(f'{name}_text', language_code).text()

        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=(get_reply_markup(language_code) if get_reply_markup else None),
        )
        return ret_lvl

    if type == COMMAND:
        ret_handler = CommandHandler(command=(command if command else name), callback=inner)
    elif type == MESSAGE:
        ret_handler = MessageHandler(filters=filters, callback=inner)
    else:
        raise ValueError('Unsupported hdl type')
    return ret_handler


def get_subject_info(sub_name, user_id, language_code):
    subtype, attendance = database.get_user_attrs([sub_name, 'attendance'], user_id=user_id).values()
    print(sub_name, subtype)
    timetable = get_subject_timetable(sub_name, subtype, attendance, language_code)
    return get_text(f'{sub_name}_subject_text', language_code).text({
        'course': subtype,
        'timetable': timetable,
        'attendance': attendance,
    })


def subject_handler(sub_name):
    @log_function
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        main_info = get_subject_info(sub_name, user_id, language_code)
        context.bot.send_message(
            chat_id=chat_id,
            text=main_info,
        )

    return CommandHandler(command=sub_name, callback=inner)


def manage_callback_query(update: Update):
    language_code = update.effective_user.language_code
    query = update.callback_query
    data = query.data
    query.answer()
    return data, language_code


def send_message(context: CallbackContext, user_nik, text):
    chat_id = database.get_user_attr('chat_id', user_nik=user_nik)
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
    )


def send_message_to_all(context: CallbackContext, text, sender_id, language_code):
    chat_ids = database.gat_all_attrs('chat_id')
    for chat_id in chat_ids:
        if chat_id == sender_id:
            continue
        context.bot.send_message(
            chat_id=chat_id,
            text=get_text('notification_admin_text', language_code).text({'text': text}),
        )
