import sys
import traceback

from telegram import Update, error
from telegram.ext import MessageHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler, \
    ConversationHandler
from telegram.utils.helpers import mention_html

import src.keyboard as keyboard
import src.database as database
import src.common_functions as cf
from static.conversarion_states import *

import src.parameters_hdl as ptrs
import src.jobs as jobs
import src.subject as subject

from src.log import log_function
from src.text import get_text
from src.timetable import get_weekday_timetable

handlers = {}

DOC_COMMANDS = {'doc', 'help', 'parameters', 'today', 'timetable', 'report'}

CONVERSATIONS = {'admin', 'parameters', 'report'}


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
    return MAIN


@log_function
def callback(update: Update, context: CallbackContext):
    data, language_code = cf.manage_callback_query(update)
    parsed_data = data.split('_')
    if parsed_data[0] == 'timetable':
        return timetable_callback(update, context, parsed_data, language_code)
    elif parsed_data[0] == 'subject':
        return subject.subject_callback(update, context, parsed_data, language_code)
    elif parsed_data[0] == 'help':
        return help_callback(update, context, parsed_data, language_code)
    else:
        return unknown_callback(update, context)


@log_function
def help(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('help_main_text', language_code).text(),
        reply_markup=keyboard.help_keyboard('main', language_code),
    )


@log_function
def help_callback(update: Update, context: CallbackContext, data: list, language_code):
    if data[1] in {'main', 'additional'}:
        text = get_text(f'help_{data[1]}_text', language_code).text()
    else:
        raise ValueError(f'Invalid help callback: {data[0]}')
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard.help_keyboard(data[1], language_code),
    )


@log_function
def unknown_callback(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('unknown_callback_text', language_code).text()
    )


@log_function
def timetable_callback(update: Update, context: CallbackContext, data: list, language_code):
    subject_names = database.get_user_subject_names(user_id=update.effective_user.id)
    try:
        update.callback_query.edit_message_text(
            text=get_weekday_timetable(
                weekday=data[1],
                subject_names=subject_names,
                attendance=database.get_user_attr('attendance', update.effective_user.id),
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


@log_function
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
            attendance=database.get_user_attr('attendance', user_id),
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
    if not database.get_user_attr('admin', user_id=update.effective_user.id):
        text = get_text('unauthorized_user_admin_text', language_code).text()
        ret_lvl = MAIN
    elif len(args) == 0:
        text = get_text('no_args_admin_text', language_code).text()
        ret_lvl = MAIN
    elif args[0] == '-n':
        if len(args) == 1:
            text = get_text('no_args_notify_admin_text', language_code).text()
            ret_lvl = MAIN
        elif args[1] == '--all':
            if len(args) > 2:
                text = get_text('too_many_args_admin_text', language_code).text()
                ret_lvl = MAIN
            else:
                text = get_text('all_users_notify_admin_text', language_code).text()
                ret_lvl = ADMIN_NOTIFY
        elif args[1] == '--user':
            if len(args) == 3:
                user_nik = args[2]
                if database.has_user(user_nik):
                    context.chat_data['notify_username_admin'] = args[2]
                    text = get_text('user_notify_admin_text', language_code).text()
                    ret_lvl = ADMIN_NOTIFY
                else:
                    text = get_text('invalid_username_admin_text', language_code).text()
                    ret_lvl = MAIN
            elif len(args) < 3:
                text = get_text('empty_user_id_notify_admin_text', language_code)
                ret_lvl = MAIN
            else:
                text = get_text('too_many_args_admin_text', language_code).text()
                ret_lvl = MAIN
        else:
            text = get_text('unavailable_flag_notify_admin_text', language_code).text()
            ret_lvl = MAIN
    elif args[0] == '-ls':
        if len(args) > 1:
            text = get_text('too_many_args_admin_text', language_code).text()
        else:
            users = database.get_all_users()
            text = get_text('ls_admin_text', language_code).text(
                {'users': '\n'.join(map(lambda pair: mention_html(pair[0], pair[1]), users))}
            )
        ret_lvl = MAIN
    elif args[0] == '-m' or args[0] == '-um':
        if len(args) > 2:
            text = get_text('too_many_args_admin_text', language_code).text()
        elif len(args) < 2:
            text = get_text('empty_user_id_admin_text', language_code).text()
        else:
            user_nik = args[1]
            if not database.has_user(user_nik):
                text = get_text('invalid_username_admin_text', language_code).text()
            elif args[0] == '-m':
                database.set_user_attrs(user_nik=user_nik, attrs={'muted': True})
                text = get_text('mute_user_admin_text', language_code).text()
            else:
                database.set_user_attrs(user_nik=user_nik, attrs={'muted': False})
                text = get_text('unmute_user_admin_text', language_code).text()
        ret_lvl = MAIN
    else:
        text = get_text('unavailable_flag_admin_text', language_code).text()
        ret_lvl = MAIN
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )
    return ret_lvl


@log_function
def admin_notify(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    user_nik = context.chat_data.get('notify_username_admin')
    context.chat_data.pop('notify_username_admin', None)
    notification_text = update.message.text
    if user_nik is not None:
        cf.send_message(context, user_nik=user_nik, text=notification_text)
    else:
        cf.send_message_to_all(context, notification_text, update.effective_user.id, language_code)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('notification_sent_notify_admin_text', language_code).text()
    )
    return MAIN


@log_function
def doc(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    args = context.args
    if len(args) > 2:
        text = get_text('quantity_error_doc_text', language_code).text()
    else:
        if len(args) == 0:
            text = get_text('doc_text', language_code).text({'command': 'all'})
        else:
            if args[0] not in DOC_COMMANDS:
                text = get_text('wrong_command_error_doc_text', language_code).text()
            else:
                text = get_text('doc_text', language_code).text({'command': args[0]})
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )


@log_function
def report(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    if database.get_user_attr('muted', update.effective_user.id):
        text = get_text('cannot_send_report_text', language_code).text()
        ret_lvl = MAIN
    else:
        text = get_text('report_text', language_code).text()
        ret_lvl = REPORT_MESSAGE
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )
    return ret_lvl


@log_function
def report_sent(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    data = {
        'report_text': update.message.text,
        'user': mention_html(update.effective_user.id, update.effective_user.first_name),
    }
    for admin_id in database.get_all_admins_chat_ids():
        context.bot.send_message(
            chat_id=admin_id,
            text=get_text('report_template_text', language_code).text(data),
        )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('report_sent_text', language_code).text(),
    )
    return MAIN


cancel_main = cf.simple_handler(name='cancel_main', type=cf.COMMAND, command='cancel', ret_lvl=MAIN)

main_hdl = []

for sub in subject.subjects:
    main_hdl.append(subject.subject_handler(sub))

main_hdl.extend([
    CommandHandler(command='parameters', callback=ptrs.parameters),
    CommandHandler(command='help', callback=help),

    CommandHandler(command='timetable', callback=timetable),
    CommandHandler(command='today', callback=today),

    CommandHandler(command='admin', callback=admin),
    CommandHandler(command='doc', callback=doc),
    CommandHandler(command='report', callback=report),

    CallbackQueryHandler(callback=callback),

    cf.simple_handler('echo_command', cf.MESSAGE, filters=Filters.command),
    cf.simple_handler('echo_message', cf.MESSAGE, filters=Filters.all),
])

handlers['main'] = ConversationHandler(
    entry_points=[
        CommandHandler(command='start', callback=start, pass_chat_data=True, pass_job_queue=True),
    ],
    states={
        MAIN: main_hdl,

        PARAMETERS_MAIN: [
            CommandHandler(command='parameters', callback=ptrs.parameters),
            CallbackQueryHandler(callback=ptrs.parameters_callback, pass_chat_data=True, pass_job_queue=True),
            ptrs.exit_parameters,
            ptrs.cancel_parameters,
            ptrs.parameters_error('main'),
        ],
        PARAMETERS_NAME: [
            ptrs.exit_parameters,
            ptrs.cancel_parameters,
            MessageHandler(filters=Filters.all, callback=ptrs.name_parameters),
        ],
        PARAMETERS_TIME: [
            ptrs.exit_parameters,
            ptrs.cancel_parameters,
            MessageHandler(filters=Filters.all, callback=ptrs.time_message_parameters, pass_chat_data=True,
                           pass_job_queue=True),
        ],
        PARAMETERS_TZINFO: [
            ptrs.exit_parameters,
            ptrs.cancel_parameters,
            MessageHandler(filters=Filters.all, callback=ptrs.tzinfo_parameters, pass_chat_data=True,
                           pass_job_queue=True),
            ptrs.parameters_error('tzinfo'),
        ],
        REPORT_MESSAGE: [
            cancel_main,
            MessageHandler(filters=Filters.all, callback=report_sent),
        ],
        ADMIN_NOTIFY: [
            cancel_main,
            MessageHandler(filters=Filters.all, callback=admin_notify),
        ],
    },
    fallbacks=[],
    persistent=True,
    name='main',
    allow_reentry=True,
)

handlers['extra_report'] = ConversationHandler(
    entry_points=[
        cf.simple_handler('report', cf.COMMAND, ret_lvl=REPORT_MESSAGE),
    ],
    states={
        REPORT_MESSAGE: [
            MessageHandler(filters=Filters.all, callback=report_sent),
        ],
    },
    fallbacks=[],
    persistent=True,
    name='extra_report',
)

handlers['not_start'] = cf.simple_handler(name='not_start', type=cf.MESSAGE, filters=Filters.all)

# Bot father commands
# help - главное меню
# parameters - окно настроек
# today - расписание на сегодня
# timetable - окно расписания
# doc - документация
# report - сообщение разработчикам
# algo - алгосики
# discra - дискретка
# diffur - диффуры
# matan - матан
# bjd - я тебе покушать принес
# eng - английский
# history - история
# sp - современная прога
# os - операционки
