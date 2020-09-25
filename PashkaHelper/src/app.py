from flask import Flask, request
from flask_sslify import SSLify

from telegram import Update

from static import config
import os

PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)
sslify = SSLify(app)


def get_app_route(bot, update_queue):
    @app.route(f'/{config.BOT_TOKEN}', methods=['GET', 'POST'])
    def get_updates():
        if request.method == 'POST':
            update = Update.de_json(request.json, bot)
            update_queue.put(update)
        return {'ok': True}

    return get_updates
