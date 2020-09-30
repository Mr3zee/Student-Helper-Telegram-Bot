from datetime import timedelta

from telegram import ParseMode, Bot
from telegram.ext import Dispatcher, Defaults, JobQueue, BasePersistence

from static import config
from src import handler as hdl
from src.app import app, get_app_route
import src.database as db
import src.jobs as jobs

import logging

from queue import Queue
from threading import Thread

logger = logging.getLogger(__name__)


class PGPersistence(BasePersistence):

    def __init__(self):
        super(PGPersistence, self).__init__(store_user_data=False, store_chat_data=False, store_bot_data=False)
        self.conversations = None
        self.on_flush = False

    def get_conversations(self, name):
        if not self.conversations:
            self.conversations = db.get_conversations()
        return self.conversations.get(name, {}).copy()

    def update_conversation(self, name, key, new_state):
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return
        self.conversations[name][key] = new_state
        if not self.on_flush:
            db.update_conversations(self.conversations)

    def flush(self):
        if self.conversations:
            db.update_conversations(self.conversations)

    def get_user_data(self):
        pass

    def get_chat_data(self):
        pass

    def get_bot_data(self):
        pass

    def update_user_data(self, user_id, data):
        pass

    def update_chat_data(self, chat_id, data):
        pass

    def update_bot_data(self, data):
        pass


def connect_bot():
    logger.info('Connecting bot...')
    new_bot = Bot(
        token=config.BOT_TOKEN,
        defaults=Defaults(
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )
    )
    jq = JobQueue()
    queue = Queue()
    persistence = PGPersistence()
    dp = Dispatcher(
        bot=new_bot,
        update_queue=queue,
        use_context=True,
        job_queue=jq,
        persistence=persistence,
    )
    jq.set_dispatcher(dp)
    jq.start()
    thread = Thread(target=dp.start)
    thread.start()
    logger.info('Bot connected successfully')
    return dp, new_bot, queue, jq


def add_handlers():
    for name, handler in hdl.handlers.items():
        logger.info('Adding ' + name + ' handler')
        dispatcher.add_handler(handler)
        logger.info('Handler added successfully')


# defining logger
logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')

# setting bot
dispatcher, bot, update_queue, job_queue = connect_bot()

# setting error handler
dispatcher.add_error_handler(callback=hdl.error_callback)

# load saved jobs
jobs.load_jobs(job_queue)

job_queue.run_repeating(callback=jobs.save_jobs_job, interval=timedelta(minutes=1), name='util')

# add handlers to dispatcher
add_handlers()

# making webhook process function
get_app_route(bot, update_queue, db.update_user_info)


if __name__ == '__main__':

    logger.info('Staring bot...')

    app.run()

    jobs.save_jobs(job_queue)

# TODO:
#  mark tasks in tables
#  fix buttons copypaste
#  add to /today links
#  teachers info
#  make 'all' a special name
#  make online info available for offline and vice versa
#  ! replace with Nikita's text
#  add deadlines
#  add everyday deadlines
#  mailing and parameters collision
#  make comments
#  make normal logging
#  make chat_data persistent
#  ! make /doc
#  optimize database
#  ! /report +

