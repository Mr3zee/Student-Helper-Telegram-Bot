from telegram import ParseMode, Bot
from telegram.ext import Dispatcher, Defaults, JobQueue

from static import config
from src import handler as hdl
from src.app import app, get_app_route

import logging

from queue import Queue
from threading import Thread

logger = logging.getLogger(__name__)


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

get_app_route(bot, update_queue)

if __name__ == '__main__':

    logger.info('Staring bot...')

    app.run()

# TODO:
#  mark tasks in tables
#  fix buttons copypaste
#  ! make notification on/off in parameters
#  ! make auto exit parameters
#  ! add to /today links
#  ! error handler
#  teachers info
#  /timetable [n]
#  ! mlw eng all looks bad +
#  ! add return timetable links to weekdays messages
#  make 'all' special name
#  mlw parser all cases in one (found in eng_text)
#  make online info available for offline and vice versa

