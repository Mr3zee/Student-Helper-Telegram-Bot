from datetime import timedelta

from telegram import Update
from telegram.ext import CallbackContext

from src.server import Server
from src import keyboard, time_management as tm, database as db, common_functions as cf
from src.text import get_text

from static import consts

SERVER = Server.get_instance()


def deadline(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    utcoffset = db.get_user_attr(consts.UTCOFFSET, user_id=user_id)

    deadlines = get_deadlines(tm.today_id(timedelta(hours=int(utcoffset))), language_code)
    cf.send_message(
        context=context,
        chat_id=chat_id,
        text=deadlines,
        reply_markup=keyboard.deadlines(language_code),
    )
    return consts.MAIN_STATE


def get_deadlines(day, language_code):
    date, deadlines = SERVER.get_deadlines(day)

    template = get_text('', language_code).text({
        consts.DATE: date,
        consts.DEADLINES: pretty_deadlines(deadlines, language_code),
    })
    return template, date


def pretty_deadlines(deadlines, language_code):
    print(deadlines)
    return 'no deadlines'
