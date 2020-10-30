from telegram.ext import CallbackContext, MessageHandler, CommandHandler
from telegram import Update, error

import src.keyboard as keyboard
import src.database as database
from src import timetable as tt
from src import time_management as tm
from src.text import get_text

from static import consts


def send_weekday_timetable(context: CallbackContext, user_id, chat_id, weekday, language_code,
                           disable_notification=False, footer=None):
    """
    Sends timetable for specified day
    """

    # get user parameters
    attendance, utcoffset = database.get_user_attrs([consts.ATTENDANCE, consts.UTCOFFSET], user_id=user_id).values()

    if weekday == consts.TODAY:
        # get current day
        weekday = tm.get_today_weekday(utcoffset)

    week_parity = tm.get_week_parity()

    timetable = tt.get_weekday_timetable(
        weekday=weekday,
        subject_names=database.get_user_subject_names(user_id),
        attendance=attendance,
        week_parity=week_parity,
        language_code=language_code,
        footer=footer,
    )

    context.bot.send_message(
        chat_id=chat_id,
        text=timetable,
        reply_markup=keyboard.timetable_keyboard(
            weekday=weekday,
            attendance=attendance,
            week_parity=week_parity,
            language_code=language_code
        ),
        disable_notification=disable_notification,
    )


def send_today_timetable(context: CallbackContext, user_id, chat_id, language_code,
                         disable_notifications=False, footer=None):
    """Sends timetable for current day"""
    return send_weekday_timetable(
        context=context,
        user_id=user_id,
        chat_id=chat_id,
        weekday=consts.TODAY,
        language_code=language_code,
        disable_notification=disable_notifications,
        footer=footer,
    )


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

        context.bot.send_message(
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


def send_message(context: CallbackContext, text, language_code, user_nick=None, chat_id=None):
    """Send simple message"""
    chat_id = database.get_user_attr(consts.CHAT_ID, user_nick=user_nick) if chat_id is None else chat_id
    try:
        context.bot.send_message(
            chat_id=chat_id,
            text=get_text('notification_admin_text', language_code).text({consts.TEXT: text}),
        )
    except error.Unauthorized:
        pass


def send_message_to_all(context: CallbackContext, text, sender_id, language_code):
    """Send simple message to all users except sender"""
    chat_ids = database.gat_attr_column(consts.CHAT_ID)
    for chat_id in chat_ids:
        if chat_id == sender_id:
            continue
        send_message(context, text, chat_id=chat_id, language_code=language_code)


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
