import datetime
from datetime import timedelta

from telegram import Update
from telegram.ext import CallbackContext

from src.server import Server
from src import keyboard, time_management as tm, database as db, common_functions as cf
from src.text import get_text

from static import consts

SERVER = Server.get_instance()


def deadline(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text, reply_markup = send_deadline(update, consts.TODAY)
    cf.send_message(context, chat_id, text, reply_markup)


def deadline_callback(update: Update, data):
    text, reply_markup = send_deadline(update, data)
    cf.edit_message(update, text, reply_markup)
    return consts.MAIN_STATE


def send_deadline(update: Update, day):
    language_code = update.effective_user.language_code
    user_id = update.effective_user.id
    utcoffset = timedelta(hours=int(db.get_user_attr(consts.UTCOFFSET, user_id=user_id)))

    # get requested date
    if day == consts.TODAY:
        day = tm.get_today(utcoffset)
    else:
        day = datetime.datetime.strptime(day, consts.DEADLINE_FORMAT)

    # deadlines = get_deadlines(day, language_code)
    deadlines = 'deadlines'
    return deadlines, keyboard.deadlines(utcoffset, language_code)


def get_deadlines(day: datetime.date, language_code):
    date, deadlines = SERVER.get_deadlines(day)

    template = get_text('', language_code).text({
        consts.DATE: date,
        consts.DEADLINE: pretty_deadlines(deadlines, language_code),
    })
    return template, date


def pretty_deadlines(deadlines, language_code):
    print(deadlines)
    return 'no deadlines'
