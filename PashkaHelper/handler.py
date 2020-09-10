from telegram.ext import MessageHandler, CallbackContext, Filters
from telegram import Update

from PashkaHelper.log import log_handler
from PashkaHelper.message import text


handlers = {}


@log_handler
def echo(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text['ru']['help_text'],
    )
    return 0


handlers['echo'] = MessageHandler(filters=Filters.all, callback=echo)
