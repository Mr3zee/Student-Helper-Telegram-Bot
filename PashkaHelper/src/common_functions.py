from telegram.ext import CallbackContext, MessageHandler, CommandHandler
from telegram import Update, error

import src.database as database
from src.text import get_text

from static import consts


def simple_handler(name, type, command=None, filters=None, reply_markup=None, ret_state=None):
    """
    Make simple handler
     - type: COMMAND - CommandHandler, MESSAGE - MessageHandler
     - command: command for CommandHandler. If None when name uses instead
     - ret_state: state to return
    """

    # Make callback function
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        chat_id = update.effective_chat.id

        text = get_text(f'{name}_text', language_code).text()

        send_message(
            context=context,
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        )
        return ret_state

    # make handler
    if type == consts.COMMAND:
        ret_handler = CommandHandler(command=(command if command else name), callback=inner)
    elif type == consts.MESSAGE:
        ret_handler = MessageHandler(filters=filters, callback=inner)
    else:
        raise ValueError('Unsupported hdl type')
    return ret_handler


def manage_callback_query(update: Update):
    """Answers callback query and returns callback data and language code"""
    language_code = update.effective_user.language_code
    query = update.callback_query
    data = query.data
    query.answer()
    return data, language_code


def send_notification(context: CallbackContext, text, language_code, user_nick=None, chat_id=None):
    """Send simple message"""
    chat_id = database.get_user_attr(consts.CHAT_ID, user_nick=user_nick) if chat_id is None else chat_id
    send_message(
        context=context,
        chat_id=chat_id,
        text=get_text('notification_admin_text', language_code).text({consts.TEXT: text}),
    )


def send_notification_to_all(context: CallbackContext, text, sender_id, language_code):
    """Send simple message to all users except sender"""
    chat_ids = database.gat_attr_column(consts.CHAT_ID)
    for chat_id in chat_ids:
        if chat_id == sender_id:
            continue
        send_notification(context, text, chat_id=chat_id, language_code=language_code)


def send_message(context: CallbackContext, chat_id, text, reply_markup=None, disable_notification=None):
    """wrapper for context.bot.send_message that ignores Unauthorized error"""
    try:
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            disable_notification=disable_notification,
        )
    except error.Unauthorized:
        pass


def edit_message(update: Update, text, reply_markup=None):
    """python-telegram-bot lib has strange error when text didn't so edit message, so here we are"""
    try:
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
        )
    except error.BadRequest:
        pass


def pretty_user_parameters(user_parameters: dict, language_code):
    """make parameters readable for users"""
    retval = {}
    for attr_name, attr_value in user_parameters.items():
        # attrs without modifications
        if (attr_name == consts.USERNAME and attr_value) or (attr_name == consts.MAILING_TIME):
            retval[attr_name] = attr_value
            continue
        # add sign to utcoffset
        elif attr_name == consts.UTCOFFSET:
            retval[attr_name] = (str(attr_value) if attr_value < 0 else f'+{attr_value}')
            continue
        # get readable values
        text = get_text(f'{attr_name}_{attr_value}_user_data_text', language_code).text()
        # attach group's number to general name
        if attr_name == consts.ENG and attr_value != consts.ALL:
            text = get_text('eng_std_user_data_text', language_code).text({consts.ENG: text})
        retval[attr_name] = text
    return retval
