from telegram import Update
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html

from src.text import get_text
from src import database, common_functions as cf

from static import consts


def admin(update: Update, context: CallbackContext):
    """
    admin's control panel
    current functions:
    '/admin -ls' - list of all users
    '/admin -n < --user [user_nick] | --all >' - send a notification to the specified user or to all users
    '/admin < -m |-um > < [user_nick] | --all >' - mute/unmute reports from user
    """
    language_code = update.effective_user.language_code
    args = context.args
    ret_lvl = consts.MAIN_STATE

    # unauthorized user tries to access admin panel
    if not database.get_user_attr('admin', user_id=update.effective_user.id):
        text = get_text('unauthorized_user_admin_text', language_code).text()

    # empty args
    elif len(args) == 0:
        text = get_text('no_args_admin_text', language_code).text()

    # notifications
    elif args[0] == '-n':
        text, ret_lvl = admin_request_notify(context, args, language_code)

    # list of the users
    elif args[0] == '-ls':
        text, ret_lvl = admin_ls(args, language_code)

    # mute/unmute users
    elif args[0] == '-m' or args[0] == '-um':
        text, ret_lvl = admin_mute(args, language_code)
    else:
        text = get_text('unavailable_flag_admin_text', language_code).text()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )
    return ret_lvl


def admin_request_notify(context: CallbackContext, args, language_code):
    """send request for notification"""
    ret_lvl = consts.MAIN_STATE
    if len(args) == 1:
        text = get_text('no_args_notify_admin_text', language_code).text()
    elif args[1] == '--all':
        if len(args) > 2:
            text = get_text('too_many_args_admin_text', language_code).text()
        else:
            text = get_text('all_users_notify_admin_text', language_code).text()
            ret_lvl = consts.ADMIN_NOTIFY_STATE
    elif args[1] == '--user':
        if len(args) == 3:
            user_nick = args[2]
            if database.has_user(user_nick):
                context.chat_data['notify_username_admin'] = args[2]
                text = get_text('user_notify_admin_text', language_code).text()
                ret_lvl = consts.ADMIN_NOTIFY_STATE
            else:
                text = get_text('invalid_username_admin_text', language_code).text()
        elif len(args) < 3:
            text = get_text('empty_user_id_notify_admin_text', language_code)
        else:
            text = get_text('too_many_args_admin_text', language_code).text()
    else:
        text = get_text('unavailable_flag_notify_admin_text', language_code).text()
    return text, ret_lvl


def admin_notify(update: Update, context: CallbackContext):
    """sends provided text to specified users"""
    language_code = update.effective_user.language_code

    user_nick = context.chat_data.get('notify_username_admin')
    context.chat_data.pop('notify_username_admin', None)

    notification_text = update.message.text

    # send notification
    if user_nick is not None:
        cf.send_message(
            context=context,
            user_nick=user_nick,
            text=notification_text, language_code=language_code,
        )
    else:
        cf.send_message_to_all(
            context=context,
            sender_id=update.effective_user.id,
            text=notification_text, language_code=language_code,
        )

    # notify sender that everything is ok
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('notification_sent_notify_admin_text', language_code).text()
    )
    return consts.MAIN_STATE


def admin_ls(args, language_code):
    """list all users"""
    if len(args) > 1:
        text = get_text('too_many_args_admin_text', language_code).text()
    else:
        users = database.get_all_users()
        text = get_text('ls_admin_text', language_code).text(
            {'users': '\n'.join(map(lambda pair: mention_html(pair[0], pair[1]), users))}
        )
    return text, consts.MAIN_STATE


def admin_mute(args, language_code):
    """mute/unmute users"""
    if len(args) > 2:
        text = get_text('too_many_args_admin_text', language_code).text()
    elif len(args) < 2:
        text = get_text('empty_user_id_admin_text', language_code).text()
    else:
        if args[0] != '-m' and args[0] != '-um':
            raise ValueError(f'Invalid flag: {args[0]}')
        flag = consts.MUTE if args[0] == '-m' else consts.UNMUTE
        target = args[1]
        if target == '--all':
            text = get_text(f'{flag}_all_users_admin_text', language_code).text()
            database.set_attr_to_all(consts.MUTED, flag == consts.MUTE)
        elif not database.has_user(target):
            text = get_text('invalid_username_admin_text', language_code).text()
        else:
            database.set_user_attrs(user_nick=target, attrs={consts.MUTED: flag == consts.MUTE})
            text = get_text(f'{flag}_user_admin_text', language_code).text()
    return text, consts.MAIN_STATE
