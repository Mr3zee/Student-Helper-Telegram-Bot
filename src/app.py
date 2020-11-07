from flask import Flask, request
from flask_sslify import SSLify

from telegram import Update, Bot
from telegram.ext import Dispatcher

from static import config
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)
sslify = SSLify(app)


def get_app_route(bot: Bot, dispatcher: Dispatcher, user_updater):
    """
    Make web page to receive updates from Telegram
    bot: Bot class to make Update instance
    dispatcher: to process update
    user_updater: update main user info in case user nik or chat_id has changed
    """
    @app.route(f'/{config.BOT_TOKEN}', methods=['GET', 'POST'])
    def get_updates():
        if request.method == 'POST':
            update = Update.de_json(request.json, bot)
            user_updater(
                user_id=update.effective_user.id,
                user_nick=update.effective_user.username,
                chat_id=update.effective_chat.id,
                language_code=update.effective_user.language_code,
            )
            dispatcher.process_update(update)
        return {'ok': True}

    return get_updates


@app.route('/', methods=['GET'])
def hello_world():
    """default page for debug and monitoring"""
    return {'ok': 'yes but actually no'}
