from flask import Flask, request
from flask_sslify import SSLify

from telegram import ParseMode, Bot, Update
from telegram.ext import Dispatcher, Defaults, JobQueue

import config
from src import handler as hdl

import logging
import os

from queue import Queue
from threading import Thread

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)
sslify = SSLify(app)


def connect_bot():
    logger.info('Connecting bot...')
    new_bot = Bot(
        token=config.BOT_TOKEN,
        defaults=Defaults(
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )
    )
    job_queue = JobQueue()
    queue = Queue()
    dp = Dispatcher(
        bot=new_bot,
        update_queue=queue,
        use_context=True,
        job_queue=job_queue,
    )
    job_queue.set_dispatcher(dp)
    job_queue.start()
    thread = Thread(target=dp.start)
    thread.start()
    logger.info('Bot connected successfully')
    return dp, new_bot, queue


def add_handlers():
    for name, handler in hdl.handlers.items():
        logger.info('Adding ' + name + ' handler')
        dispatcher.add_handler(handler)
        logger.info('Handler added successfully')


logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')

dispatcher, bot, update_queue = connect_bot()

add_handlers()


@app.route(f'/{config.BOT_TOKEN}', methods=['GET', 'POST'])
def get_updates():
    if request.method == 'POST':
        update = Update.de_json(request.json, bot)
        update_queue.put(update)
    return {'ok': True}


if __name__ == '__main__':

    logger.info('Staring bot...')

    app.run()

# TODO:
#  mark tasks in tables
#  make inline mode
#  fix buttons copypaste
#  make database
#  таблица отметки дз очно / заочно
#  fix /today +
#  fix /discra
#  fix dont show eng timetable when eng group set +
#  make auto parameters exit

