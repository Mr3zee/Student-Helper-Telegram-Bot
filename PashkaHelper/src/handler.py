from telegram import Update, error
from telegram.ext import MessageHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler, \
    ConversationHandler

from src import keyboard, buttons, database, common_functions as cf
import src.parameters_hdl as ptrs
from src.log import log_function
from src.text import get_text
from src.timetable import get_weekday_timetable
from src.subject import subjects

handlers = {}


@log_function
def start(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    database.add_user(user_id)

    cf.set_morning_message(user_id=user_id, chat_id=chat_id, context=context, language_code=language_code)

    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('start_text', language_code=language_code).text(),
    )


@log_function
def callback(update: Update, context: CallbackContext):
    data, language_code = cf.manage_callback_query(update)
    if data in buttons.WEEKDAYS_SET:
        return timetable_callback(update, context, data, language_code)


@log_function
def timetable_callback(update: Update, context: CallbackContext, data, language_code):
    subject_names = database.get_user_subject_names(user_id=update.effective_user.id)
    try:
        update.callback_query.edit_message_text(
            text=get_weekday_timetable(
                weekday=data[:-7],
                subject_names=subject_names,
                attendance=database.get_user_attr(update.effective_user.id, 'attendance'),
                language_code=language_code,
            ),
            reply_markup=keyboard.timetable_keyboard(language_code=language_code)
        )
    except error.BadRequest:
        pass


@log_function
def today(update: Update, context: CallbackContext):
    cf.send_today_timetable(
        context=context,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        language_code=update.effective_user.language_code,
    )


handlers['parameters'] = ConversationHandler(
    entry_points=[
        CommandHandler(command='parameters', callback=ptrs.parameters)
    ],
    states={
        ptrs.MAIN_LVL: [
            CallbackQueryHandler(callback=ptrs.parameters_callback, pass_chat_data=True, pass_job_queue=True),
            ptrs.exit_parameters_hdl,
            ptrs.parameters_error('main'),
        ],
        ptrs.NAME_LVL: [
            ptrs.exit_parameters_hdl,
            MessageHandler(filters=Filters.all, callback=ptrs.name_parameters),
        ],
        ptrs.TIME_LVL: [
            ptrs.exit_parameters_hdl,
            MessageHandler(filters=Filters.all, callback=ptrs.time_message_parameters, pass_chat_data=True,
                           pass_job_queue=True),
        ],
        ptrs.TZINFO_LVL: [
            ptrs.exit_parameters_hdl,
            MessageHandler(filters=Filters.all, callback=ptrs.tzinfo_parameters, pass_chat_data=True, pass_job_queue=True),
            ptrs.parameters_error('tzinfo'),
        ],
    },
    fallbacks=[],
    persistent=True,
    name='parameters',
)

handlers['start'] = CommandHandler(command='start', callback=start, pass_chat_data=True, pass_job_queue=True)

handlers['help'] = cf.simple_handler('help', cf.COMMAND)
handlers['timetable'] = cf.simple_handler('timetable', cf.COMMAND, get_reply_markup=keyboard.timetable_keyboard)

handlers['today'] = CommandHandler(command='today', callback=today)

handlers['callback'] = CallbackQueryHandler(callback=callback)

for sub in subjects:
    handlers[sub] = cf.subject_handler(sub)

handlers['echo_command'] = cf.simple_handler('echo_command', cf.MESSAGE, filters=Filters.command)
handlers['echo_message'] = cf.simple_handler('echo_message', cf.MESSAGE, filters=Filters.all)
