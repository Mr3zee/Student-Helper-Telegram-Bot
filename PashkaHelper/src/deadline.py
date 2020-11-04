import re
from datetime import timedelta, datetime

from telegram import Update
from telegram.ext import CallbackContext

from src.server import Server
from src import keyboard, time_management as tm, database as db, common_functions as cf
from src.text import get_text

from static import consts

SERVER = Server.get_instance()


def deadline(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text, reply_markup = make_deadline(update, consts.TODAY)
    cf.send_message(context, chat_id, text, reply_markup)


def deadline_callback(update: Update, data):
    text, reply_markup = make_deadline(update, data)
    cf.edit_message(update, text, reply_markup)
    return consts.MAIN_STATE


def make_deadline(update: Update, day: str):
    language_code = update.effective_user.language_code
    user_id = update.effective_user.id
    utcoffset = timedelta(hours=int(db.get_user_attr(consts.UTCOFFSET, user_id=user_id)))
    deadlines = get_deadlines(day, utcoffset, language_code)
    return deadlines, keyboard.deadlines(utcoffset, language_code)


def get_deadlines(day: str, utcoffset, language_code):
    """request deadlines from server and returns them as readable text"""

    today = tm.get_today(utcoffset)

    # str_day: date in readable format; day: datetime.date for requested day
    if day == consts.TODAY:
        day = today
        str_day = day.strftime(consts.DEADLINE_DAY_FORMAT)
    else:
        str_day = day
        day = datetime.strptime(day, consts.DEADLINE_DAY_FORMAT)
        day = day.replace(year=today.year)

    deadlines, weekday = SERVER.get_deadlines(day.toordinal())

    template = get_text('deadline_text', language_code).text({
        consts.DATE: str_day,
        consts.WEEKDAY: weekday,
        consts.DEADLINE: pretty_deadlines(deadlines, language_code),
    })
    return template


def pretty_deadlines(deadlines, language_code):
    lst = []
    for subject, dl in deadlines:
        lst.append(get_text('dl_template_text', language_code).text({
            consts.DEADLINE: re.sub('\n', ' ', dl),
            consts.SUBJECT: subject,
        }))
    if not lst:
        return get_text('no_deadlines_text', language_code).text()
    return '\n\n'.join(lst)
