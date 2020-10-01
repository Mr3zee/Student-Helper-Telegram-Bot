from flask import Flask, request
from flask_sslify import SSLify

from telegram import Update
from telegram.ext import Dispatcher

from static import config
import os

PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)
sslify = SSLify(app)


def get_app_route(bot, dispatcher: Dispatcher, user_updater):
    @app.route(f'/{config.BOT_TOKEN}', methods=['GET', 'POST'])
    def get_updates():
        if request.method == 'POST':
            update = Update.de_json(request.json, bot)
            user_updater(
                user_id=update.effective_user.id,
                user_nik=update.effective_user.username,
                chat_id=update.effective_chat.id,
            )
            dispatcher.process_update(update)
        return {'ok': True}

    return get_updates


@app.route('/', methods=['GET'])
def hello_world():
    return {'ok': 'yes but actually no'}
