from telegram import Update, error
from telegram.ext import MessageHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler

import keyboard as keyboard

from log import log_handler
from message import get_text
from time_management import get_weekday, MORNING_MESSAGE_TIME
from timetable import get_weekday_timetable, get_timetable_by_index, BOTH_ATTENDANCE, get_subject_timetable
from user_parameters import get_user_parameters

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


def simple_handler(name, hdl_type, need_subject_timetable=False, reply_markup_func=None, filters=None):
    @log_handler
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        chat_id = update.effective_chat.id

        reply_markup = (reply_markup_func(language_code=language_code) if reply_markup_func else None)
        main_info = get_text(f"{name}_text", language_code=language_code)
        if need_subject_timetable:
            subject_type, attendance = get_user_parameters(chat_id, name)
            additional_info = f'\n{get_subject_timetable(subject_type, attendance, language_code)}'
            print(additional_info)
            main_info = main_info.format(additional_info)
        context.bot.send_message(
            chat_id=chat_id,
            text=main_info,
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
simple_handler('timetable', COMMAND, reply_markup_func=keyboard.timetable_keyboard)

handlers['today'] = CommandHandler(command='today', callback=today)
handlers['callback'] = CallbackQueryHandler(callback=callback)

subjects = ['algo', 'discra', 'diffur', 'os', 'sp', 'history', 'matan', 'eng', 'bjd']

for sub in subjects:
    simple_handler(sub, COMMAND, need_subject_timetable=True)


simple_handler('echo_command', MESSAGE, filters=Filters.command)
simple_handler('echo_message', MESSAGE, filters=Filters.all)
