from telegram.ext import MessageHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler
from telegram import Update

from PashkaHelper.log import log_handler
from PashkaHelper.message import get_text
import PashkaHelper.keyboard as keyboard
from PashkaHelper.timetable import get_timetable, get_timetable_by_index

from datetime import datetime


handlers = {}


@log_handler
def start(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('start_text', language_code),
    )


@log_handler
def timetable(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('timetable_text', language_code),
        reply_markup=keyboard.timetable_keyboard(language_code),
    )


@log_handler
def timetable_callback(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    query = update.callback_query
    data = query.data
    query.answer()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_timetable(data[:-7], language_code),
    )


@log_handler
def today(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_timetable_by_index(day=datetime.today().weekday(), language_code=language_code),
    )


@log_handler
def help_(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('help_text', language_code),
    )


@log_handler
def algo(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('algo_text', language_code),
    )


@log_handler
def matan(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('matan_text', language_code),
    )


@log_handler
def kotlin(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('kotlin_text', language_code),
    )


@log_handler
def os(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('os_text', language_code),
    )


@log_handler
def diffur(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('diffur_text', language_code),
    )


@log_handler
def discra(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('discra_text', language_code),
    )


@log_handler
def eng(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('eng_text', language_code),
    )


@log_handler
def echo_command(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('echo_command_text', language_code),
    )


@log_handler
def echo_message(update: Update, context: CallbackContext):
    language_code = update.effective_user.language_code
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_text('echo_message_text', language_code),
    )


handlers['start'] = CommandHandler(command='start', callback=start)
handlers['help'] = CommandHandler(command='help', callback=help_)
handlers['algo'] = CommandHandler(command='algo', callback=algo)
handlers['discra'] = CommandHandler(command='discra', callback=discra)
handlers['diffur'] = CommandHandler(command='diffur', callback=diffur)
handlers['os'] = CommandHandler(command='os', callback=os)
handlers['kotlin'] = CommandHandler(command='kotlin', callback=kotlin)
handlers['matan'] = CommandHandler(command='matan', callback=matan)
handlers['eng'] = CommandHandler(command='eng', callback=eng)
handlers['timetable'] = CommandHandler(command='timetable', callback=timetable)
handlers['today'] = CommandHandler(command='today', callback=today)
handlers['timetable_callback'] = CallbackQueryHandler(callback=timetable_callback)

handlers['echo_command'] = MessageHandler(filters=Filters.command, callback=echo_command)
handlers['echo_message'] = MessageHandler(filters=Filters.all, callback=echo_message)
