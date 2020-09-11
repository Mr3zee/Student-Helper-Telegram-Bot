from telegram.ext import MessageHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler
from telegram import Update

from log import log_handler
from message import get_text
import keyboard as keyboard
from timetable import get_timetable, get_timetable_by_index, INTRAMURAL, EXTRAMURAL, BOTH

from datetime import datetime
import pytz

handlers = {}

MESSAGE, COMMAND = range(2)


@log_handler
def callback(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    query = update.callback_query
    data = query.data
    query.answer()
    if data in keyboard.weekdays:
        return timetable_callback(update, context, data, language_code)


@log_handler
def timetable_callback(update: Update, context: CallbackContext, data, language_code):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_timetable(data[:-7], attendance=BOTH, language_code=language_code),
    )


def timezone_converter(input_dt, current_tz='UTC', target_tz='Europe/Moscow'):
    current_tz = pytz.timezone(current_tz)
    target_tz = pytz.timezone(target_tz)
    target_dt = current_tz.localize(input_dt).astimezone(target_tz)
    return target_tz.normalize(target_dt)


@log_handler
def today(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_timetable_by_index(
            day=timezone_converter(datetime.utcnow()).weekday(), attendance=BOTH,
            language_code=language_code
        ),
        reply_markup=keyboard.timetable_keyboard(language_code=language_code),
    )


def simple_handler(name, hdl_type, reply_markup_func=None, filters=None):
    @log_handler
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        reply_markup = (reply_markup_func(language_code=language_code) if reply_markup_func else None)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_text(name + '_text', language_code),
            reply_markup=reply_markup,
        )

    if hdl_type == COMMAND:
        handler = CommandHandler(command=name, callback=inner)
    elif hdl_type == MESSAGE:
        handler = MessageHandler(filters, callback=inner)
    else:
        raise ValueError('Invalid type')
    handlers[name] = handler


simple_handler('start', COMMAND)
simple_handler('help', COMMAND)
simple_handler('algo', COMMAND)
simple_handler('discra', COMMAND)
simple_handler('diffur', COMMAND)
simple_handler('os', COMMAND)
simple_handler('sp', COMMAND)
simple_handler('history', COMMAND)
simple_handler('matan', COMMAND)
simple_handler('eng', COMMAND)
simple_handler('bjd', COMMAND)
simple_handler('timetable', COMMAND, keyboard.timetable_keyboard)

handlers['today'] = CommandHandler(command='today', callback=today)

handlers['callback'] = CallbackQueryHandler(callback=callback)

simple_handler('echo_command', MESSAGE, Filters.command)
simple_handler('echo_message', MESSAGE, Filters.all)
