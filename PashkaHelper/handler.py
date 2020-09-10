from telegram.ext import MessageHandler, CommandHandler, CallbackContext, Filters
from telegram import Update

from PashkaHelper.log import log_handler
from PashkaHelper.message import text


handlers = {}


@log_handler
def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['start_text'],
    )


@log_handler
def timetable(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['timetable_text'],
    )


@log_handler
def help_(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['help_text'],
    )


@log_handler
def algo(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['algo_text'],
    )


@log_handler
def matan(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['matan_text'],
    )


@log_handler
def kotlin(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['kotlin_text'],
    )


@log_handler
def os(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['os_text'],
    )


@log_handler
def diffur(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['diffur_text'],
    )


@log_handler
def discra(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['discra_text'],
    )


@log_handler
def eng(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['eng_text'],
    )


@log_handler
def echo_command(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['echo_command_text'],
    )


@log_handler
def echo_message(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['echo_message_text'],
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

handlers['echo_command'] = MessageHandler(filters=Filters.command, callback=echo_command)
handlers['echo_message'] = MessageHandler(filters=Filters.all, callback=echo_message)
