from telegram import Update, error
from telegram.ext import MessageHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler, \
    ConversationHandler

import keyboard
import buttons
import user_parameters
import job
from parameters_hdl import parameters, parameters_callback, manage_callback_query, name, tzinfo, time_message, \
    MAIN_LVL, NAME_LVL, TIME_LVL, TZINFO_LVL

from log import log_handler
from message import get_text
from timetable import get_weekday_timetable, BOTH_ATTENDANCE, get_subject_timetable

handlers = {}

MESSAGE, COMMAND = range(2)


@log_handler
def start(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user_parameters.set_default_user_parameters(user_id)

    job.set_morning_message(user_id=user_id, chat_id=chat_id, context=context, language_code=language_code)

    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('start_text', language_code=language_code),
    )


@log_handler
def callback(update: Update, context: CallbackContext):
    data, language_code = manage_callback_query(update)
    if data in buttons.WEEKDAYS_SET:
        return timetable_callback(update, context, data, language_code)


@log_handler
def timetable_callback(update: Update, context: CallbackContext, data, language_code):
    try:
        update.callback_query.edit_message_text(
            text=get_weekday_timetable(
                weekday=data[:-7],
                attendance=user_parameters.get_user_attendance(update.effective_user.id),
                language_code=language_code,
            ),
            reply_markup=keyboard.timetable_keyboard(language_code=language_code)
        )
    except error.BadRequest:
        pass


@log_handler
def today(update: Update, context: CallbackContext):
    job.send_today_timetable(
        context=context,
        chat_id=update.effective_chat.id,
        language_code=update.effective_user.language_code
    )


def simple_handler(hdl_name, hdl_type, need_subject_timetable=False, reply_markup_func=None, filters=None):
    @log_handler
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        reply_markup = (reply_markup_func(language_code=language_code) if reply_markup_func else None)
        main_info = get_text(f"{hdl_name}_text", language_code=language_code)
        if need_subject_timetable:
            subject_type, attendance = user_parameters.get_user_course(user_id, hdl_name)
            additional_info = f'\n{get_subject_timetable(subject_type, attendance, language_code)}'
            main_info = main_info.format(additional_info)
        context.bot.send_message(
            chat_id=chat_id,
            text=main_info,
            reply_markup=reply_markup,
        )

    if hdl_type == COMMAND:
        handler = CommandHandler(command=hdl_name, callback=inner)
    elif hdl_type == MESSAGE:
        handler = MessageHandler(filters, callback=inner)
    else:
        raise ValueError('Invalid type')
    handlers[hdl_name] = handler


handlers['start'] = CommandHandler(command='start', callback=start, pass_chat_data=True, pass_job_queue=True)

simple_handler('help', COMMAND)
simple_handler('timetable', COMMAND, reply_markup_func=keyboard.timetable_keyboard)

handlers['today'] = CommandHandler(command='today', callback=today)

handlers['parameters'] = ConversationHandler(
    entry_points=[
        CommandHandler(command='parameters', callback=parameters)
    ],
    states={
        MAIN_LVL: [
            CallbackQueryHandler(callback=parameters_callback, pass_chat_data=True, pass_job_queue=True),
        ],
        NAME_LVL: [
            MessageHandler(filters=Filters.all, callback=name),
        ],
        TIME_LVL: [
            MessageHandler(filters=Filters.all, callback=time_message),
        ],
        TZINFO_LVL: [
            MessageHandler(filters=Filters.all, callback=tzinfo),
        ],
    },
    fallbacks=[],
)

handlers['callback'] = CallbackQueryHandler(callback=callback)

subjects = ['algo', 'discra', 'diffur', 'os', 'sp', 'history', 'matan', 'eng', 'bjd']

for sub in subjects:
    simple_handler(sub, COMMAND, need_subject_timetable=True)

simple_handler('echo_command', MESSAGE, filters=Filters.command)
simple_handler('echo_message', MESSAGE, filters=Filters.all)
