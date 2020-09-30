import sys
import traceback

from telegram import Update, error
from telegram.ext import MessageHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler, \
    ConversationHandler
from telegram.utils.helpers import mention_html

from src import keyboard, buttons, database, common_functions as cf

import src.parameters_hdl as ptrs
import src.jobs as jobs

from src.log import log_function
from src.text import get_text
from src.timetable import get_weekday_timetable
from src.subject import subjects

handlers = {}

ADMIN_NOTIFY, = range(1)


@log_function
def start(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    database.add_user(user_id, update.effective_user.username, chat_id)

    jobs.set_mailing_job(user_id=user_id, chat_id=chat_id, context=context, language_code=language_code)

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


def timetable_args_error(context: CallbackContext, chat_id, error_type, language_code):
    context.bot.send_message(
        chat_id=chat_id,
        text=get_text('timetable_args_error_text', language_code).text({'error_type': error_type}),
    )


def timetable(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    args = context.args

    if len(args) > 1:
        return timetable_args_error(context, chat_id, 'many', language_code)
    elif len(args) == 1:
        try:
            day = int(args[0])
        except ValueError:
            return timetable_args_error(context, chat_id, 'type', language_code)
        if day > 6 or day < 0:
            return timetable_args_error(context, chat_id, 'value', language_code)
        text = cf.get_timetable_by_index(
            day=day,
            subject_names=database.get_user_subject_names(user_id),
            attendance=database.get_user_attr(user_id, 'attendance'),
            language_code=language_code,
        )
    else:
        text = get_text('timetable_text', language_code).text()

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=(keyboard.timetable_keyboard(language_code)),
    )


@log_function
def today(update: Update, context: CallbackContext):
    cf.send_today_timetable(
        context=context,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        language_code=update.effective_user.language_code,
    )


def error_callback(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('error_handler_user_text', language_code).text()
    )
    data = {'trace': "".join(traceback.format_tb(sys.exc_info()[2])), 'error': str(context.error)}
    if update.effective_user:
        data['user'] = mention_html(update.effective_user.id, update.effective_user.first_name)
    else:
        data['user'] = 'unavailable'

    text = get_text('error_handler_dev_text', language_code)
    for dev_id in database.get_all_admins_chat_ids():
        try:
            context.bot.send_message(
                chat_id=dev_id,
                text=text.text(data),
            )
        except error.BadRequest:
            data['trace'] = 'Traceback is unavailable'
            context.bot.send_message(
                chat_id=dev_id,
                text=text.text(data),
            )
    raise


@log_function
def admin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    args = context.args
    if not database.is_admin(user_id=update.effective_user.id):
        text = get_text('unauthorized_user_admin_text', language_code).text()
        ret_lvl = ConversationHandler.END
    elif len(args) == 0:
        text = get_text('no_args_admin_text', language_code).text()
        ret_lvl = ConversationHandler.END
    elif args[0] == '-n':
        if len(args) == 1:
            text = get_text('no_args_notify_admin_text', language_code).text()
            ret_lvl = ConversationHandler.END
        elif args[1] == '--all':
            if len(args) > 2:
                text = get_text('too_many_args_notify_admin_text', language_code).text()
                ret_lvl = ConversationHandler.END
            else:
                text = get_text('all_users_notify_admin_text', language_code).text()
                ret_lvl = ADMIN_NOTIFY
        elif args[1] == '--user':
            if len(args) == 3:
                user_nik = args[2]
                if database.check_user_nik(user_nik):
                    context.chat_data['notify_username_admin'] = args[2]
                    text = get_text('user_notify_admin_text', language_code).text()
                    ret_lvl = ADMIN_NOTIFY
                else:
                    text = get_text('invalid_username_notify_admin_text', language_code).text()
                    ret_lvl = ConversationHandler.END
            elif len(args < 3):
                text = get_text('empty_user_id_notify_admin_text', language_code)
                ret_lvl = ConversationHandler.END
            else:
                text = get_text('too_many_args_notify_admin_text', language_code).text()
                ret_lvl = ConversationHandler.END
        else:
            text = get_text('unavailable_flag_notify_admin_text', language_code).text()
            ret_lvl = ConversationHandler.END
    else:
        text = get_text('unavailable_flag_admin_text', language_code).text()
        ret_lvl = ConversationHandler.END
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )
    return ret_lvl


@log_function
def admin_notify(update: Update, context: CallbackContext):
    user_nik = context.chat_data.get('notify_username_admin')
    context.chat_data.pop('notify_username_admin', None)
    notification_text = update.message.text
    if user_nik is not None:
        cf.send_message(context, user_nik=user_nik, text=notification_text)
    else:
        cf.send_message_to_all(context, text=notification_text)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('notification_sent_notify_admin_text', update.effective_user.language_code).text()
    )
    return ConversationHandler.END


handlers['admin'] = ConversationHandler(
    entry_points=[
        CommandHandler(command='admin', callback=admin),
    ],
    states={
        ADMIN_NOTIFY: [
            MessageHandler(filters=Filters.all, callback=admin_notify),
        ],
    },
    fallbacks=[],
    persistent=True,
    name='admin',
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
            MessageHandler(filters=Filters.all, callback=ptrs.tzinfo_parameters, pass_chat_data=True,
                           pass_job_queue=True),
            ptrs.parameters_error('tzinfo'),
        ],
    },
    fallbacks=[],
    persistent=True,
    name='parameters',
)

handlers['start'] = CommandHandler(command='start', callback=start, pass_chat_data=True, pass_job_queue=True)

handlers['help'] = cf.simple_handler('help', cf.COMMAND)
handlers['timetable'] = CommandHandler(command='timetable', callback=timetable)

handlers['today'] = CommandHandler(command='today', callback=today)

handlers['callback'] = CallbackQueryHandler(callback=callback)

for sub in subjects:
    handlers[sub] = cf.subject_handler(sub)

handlers['echo_command'] = cf.simple_handler('echo_command', cf.MESSAGE, filters=Filters.command)
handlers['echo_message'] = cf.simple_handler('echo_message', cf.MESSAGE, filters=Filters.all)
