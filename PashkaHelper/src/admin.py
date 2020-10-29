from telegram import Update
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html

from src.text import get_text
from src import database, common_functions as cf, keyboard

from static import consts


def admin(update: Update, context: CallbackContext):
    """
    admin's control panel
    current functions:
    '/admin [-ls]' - list of all users
    '/admin [-n <--user=user_nick | --all>]' - send a notification to the specified user or to all users
    '/admin [-m |-um <--user=user_nick | --all>]' - mute/unmute reports from user
    """
    language_code = update.effective_user.language_code
    args = context.args
    ret_lvl = consts.MAIN_STATE
    reply_markup = None

    # unauthorized user tries to access admin panel
    if not database.get_user_attr('admin', user_id=update.effective_user.id):
        text = get_text('unauthorized_user_admin_text', language_code).text()

    # empty args
    elif len(args) == 0:
        text = get_text('no_args_admin_text', language_code).text()

    # notifications
    elif args[0] == '-n':
        text, ret_lvl, reply_markup = admin_request_notify(context, args, language_code)

    # list of the users
    elif args[0] == '-ls':
        text, ret_lvl, reply_markup = admin_ls(0, language_code)

    # mute/unmute users
    elif args[0] == '-m' or args[0] == '-um':
        text, ret_lvl = admin_mute(args, language_code)
    else:
        text = get_text('invalid_flag_admin_text', language_code).text()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup,
    )
    return ret_lvl


def admin_callback(update: Update, parsed_data, language_code):
    if parsed_data[1] == 'ls':
        text, _, reply_markup = admin_ls(parsed_data[2], language_code)
        cf.edit_message(
            update=update,
            text=text,
            reply_markup=reply_markup,
        )
    else:
        raise ValueError(f"Invalid admin callback: {parsed_data[1]}")


def admin_request_notify(context: CallbackContext, args, language_code):
    """send request for notification"""
    ret_lvl = consts.MAIN_STATE
    reply_markup = None
    if len(args) == 1:
        text = get_text('no_args_notify_admin_text', language_code).text()
    else:
        params = args[1].split('=')
        ret_lvl = consts.ADMIN_NOTIFY_STATE
        reply_markup = keyboard.cancel_operation(consts.ADMIN_NOTIFY_STATE)(language_code)
        if params[0] == '--all':
            text = get_text('all_users_notify_admin_text', language_code).text()
        elif params[0] == '--user':
            if len(params) == 2 and database.has_user(params[1]):
                context.chat_data['notify_username_admin'] = params[1]
                text = get_text('user_notify_admin_text', language_code).text()
            else:
                text = get_text('invalid_username_admin_text', language_code).text()
        else:
            ret_lvl, reply_markup = consts.MAIN_STATE, None
            text = get_text('invalid_flag_admin_text', language_code).text()
    return text, ret_lvl, reply_markup


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


USERS_ON_PAGE = 12


def admin_ls(page_number, language_code):
    """list all users"""

    # get page of users (left/right bound)
    page_number = int(page_number)
    users = database.get_all_users()
    count = len(users)
    page_number = min((count - 1) // USERS_ON_PAGE, page_number)

    lb = page_number * USERS_ON_PAGE
    rb = lb + USERS_ON_PAGE

    text = get_text('ls_admin_text', language_code).text({
        consts.USERS: '\n'.join(map(lambda pair: mention_html(pair[0], pair[1]), users[lb:rb])),
        consts.LB: lb + 1,
        consts.RB: min(rb, count),
        consts.TOTAL: count
    })

    # detect page type
    if lb == 0 and rb >= count:
        page_type = consts.SINGLE_PAGE
    else:
        page_type = (
            consts.FIRST_PAGE if lb == 0
            else (consts.LAST_PAGE if rb >= count else consts.MIDDLE_PAGE)
        )
    reply_markup = keyboard.admin_ls(page_number, page_type, language_code)

    return text, consts.MAIN_STATE, reply_markup


def admin_mute(args, language_code):
    """mute/unmute users"""
    if len(args) < 2:
        text = get_text('empty_user_id_admin_text', language_code).text()
    else:
        if args[0] != '-m' and args[0] != '-um':
            raise ValueError(f'Invalid flag: {args[0]}')
        flag = consts.MUTE if args[0] == '-m' else consts.UNMUTE
        target = args[1].split('=')
        if target[0] == '--all':
            text = get_text(f'{flag}_all_users_admin_text', language_code).text()
            database.set_attr_to_all(consts.MUTED, flag == consts.MUTE)
        elif target[0] == '--user':
            if len(target) == 2 and database.has_user(target[1]):
                database.set_user_attrs(user_nick=target, attrs={consts.MUTED: flag == consts.MUTE})
                text = get_text(f'{flag}_user_admin_text', language_code).text()
            else:
                text = get_text('invalid_username_admin_text', language_code).text()
        else:
            text = get_text('invalid_flag_admin_text', language_code).text()
    return text, consts.MAIN_STATE
