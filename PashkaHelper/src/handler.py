from telegram import Update, error
from telegram.ext import MessageHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler, \
    ConversationHandler

from src import keyboard, buttons, user_parameters, common_functions as cf
from src.parameters_hdl import parameters, parameters_callback, parameters_error, \
    name_parameters, tzinfo_parameters, time_message_parameters, exit_parameters_hdl, \
    MAIN_LVL, NAME_LVL, TIME_LVL, TZINFO_LVL

from src.log import log_handler
from src.message import get_text
from src.timetable import get_weekday_timetable

handlers = {}


@log_handler
def start(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user_parameters.set_default_user_parameters(user_id)

    cf.set_morning_message(user_id=user_id, chat_id=chat_id, context=context, language_code=language_code)

    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('start_text', language_code=language_code),
    )


@log_handler
def callback(update: Update, context: CallbackContext):
    data, language_code = cf.manage_callback_query(update)
    if data in buttons.WEEKDAYS_SET:
        return timetable_callback(update, context, data, language_code)


@log_handler
def timetable_callback(update: Update, context: CallbackContext, data, language_code):
    subject_names = user_parameters.get_user_subject_names(user_id=update.effective_user.id)
    try:
        update.callback_query.edit_message_text(
            text=get_weekday_timetable(
                weekday=data[:-7],
                subject_names=subject_names,
                attendance=user_parameters.get_user_attendance(update.effective_user.id),
                language_code=language_code,
            ),
            reply_markup=keyboard.timetable_keyboard(language_code=language_code)
        )
    except error.BadRequest:
        pass


@log_handler
def today(update: Update, context: CallbackContext):
    cf.send_today_timetable(
        context=context,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        language_code=update.effective_user.language_code,
    )


handlers['parameters'] = ConversationHandler(
    entry_points=[
        CommandHandler(command='parameters', callback=parameters)
    ],
    states={
        MAIN_LVL: [
            CallbackQueryHandler(callback=parameters_callback, pass_chat_data=True, pass_job_queue=True),
            exit_parameters_hdl,
            parameters_error('main'),
        ],
        NAME_LVL: [
            exit_parameters_hdl,
            MessageHandler(filters=Filters.all, callback=name_parameters),
        ],
        TIME_LVL: [
            exit_parameters_hdl,
            MessageHandler(filters=Filters.all, callback=time_message_parameters, pass_chat_data=True,
                           pass_job_queue=True),
        ],
        TZINFO_LVL: [
            exit_parameters_hdl,
            MessageHandler(filters=Filters.all, callback=tzinfo_parameters, pass_chat_data=True, pass_job_queue=True),
            parameters_error('tzinfo'),
        ],
    },
    fallbacks=[],
)

handlers['start'] = CommandHandler(command='start', callback=start, pass_chat_data=True, pass_job_queue=True)

handlers['help'] = cf.simple_handler('help', cf.COMMAND)
handlers['timetable'] = cf.simple_handler('timetable', cf.COMMAND, get_reply_markup=keyboard.timetable_keyboard)

handlers['today'] = CommandHandler(command='today', callback=today)

handlers['callback'] = CallbackQueryHandler(callback=callback)

for sub in cf.subjects:
    handlers[sub] = cf.subject_handler(sub)

handlers['echo_command'] = cf.simple_handler('echo_command', cf.MESSAGE, filters=Filters.command)
handlers['echo_message'] = cf.simple_handler('echo_message', cf.MESSAGE, filters=Filters.all)
