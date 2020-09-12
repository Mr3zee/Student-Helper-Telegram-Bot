from telegram.ext import MessageHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler
from telegram import Update, error

from log import log_handler
from message import get_text
import keyboard as keyboard
from timetable import get_weekday_timetable, get_timetable_by_index, BOTH_ATTENDANCE

from time_management import get_weekday, MORNING_MESSAGE_TIME

handlers = {}

MESSAGE, COMMAND = range(2)


def send_morning_message(context: CallbackContext):
    job = context.job
    send_today_timetable(
        context=context,
        chat_id=job.context[0],
        language_code=job.context[1]
    )


def set_morning_message(context: CallbackContext, chat_id, language_code):
    job_name = 'morning_message'
    if job_name not in context.chat_data:
        new_job = context.job_queue.run_daily(
            callback=send_morning_message,
            time=MORNING_MESSAGE_TIME,
            days=(0, 1, 2, 3, 4, 5),
            context=[chat_id, language_code],
            name=job_name,
        )
        context.chat_data[job_name] = new_job
        return new_job


@log_handler
def start(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id

    new_job = set_morning_message(chat_id=chat_id, context=context, language_code=language_code)

    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('start_text', language_code=language_code),
    )


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
    try:
        update.callback_query.edit_message_text(
            text=get_weekday_timetable(
                weekday=data[:-7],
                attendance=BOTH_ATTENDANCE,
                language_code=language_code,
            ),
            reply_markup=keyboard.timetable_keyboard(language_code=language_code)
        )
    except error.BadRequest:
        pass


def send_today_timetable(context: CallbackContext, chat_id, language_code):
    context.bot.send_message(
        chat_id=chat_id,
        text=get_timetable_by_index(
            day=get_weekday(),
            attendance=BOTH_ATTENDANCE,
            language_code=language_code,
        ),
        reply_markup=keyboard.timetable_keyboard(language_code=language_code),
    )


@log_handler
def today(update: Update, context: CallbackContext):
    send_today_timetable(
        context=context,
        chat_id=update.effective_chat.id,
        language_code=update.effective_user.language_code
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


handlers['start'] = CommandHandler(command='start', callback=start, pass_chat_data=True, pass_job_queue=True)

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

simple_handler('echo_command', MESSAGE, filters=Filters.command)
simple_handler('echo_message', MESSAGE, filters=Filters.all)
