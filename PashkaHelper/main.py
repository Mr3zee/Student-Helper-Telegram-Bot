from telegram import ParseMode, Bot
from telegram.ext import Dispatcher, Defaults, JobQueue, BasePersistence

from static import config
import src.handler as hdl
from src.app import app, get_app_route, PORT
import src.database as db
import src.jobs as jobs

import logging

logger = logging.getLogger(__name__)


class PGPersistence(BasePersistence):
    """Persistence class for dispatcher"""

    def __init__(self):
        super(PGPersistence, self).__init__(store_user_data=False, store_chat_data=False, store_bot_data=False)
        self.conversations = None
        self.on_flush = False

    def get_conversations(self, name):
        """get conversations from database as dict"""
        if not self.conversations:
            self.conversations = db.get_conversations()
        return self.conversations.get(name, {}).copy()

    def update_conversation(self, name, key, new_state):
        """update conversation with new key, value and load to database"""
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return
        self.conversations[name][key] = new_state
        if not self.on_flush:
            db.update_conversations(self.conversations)

    def flush(self):
        """load conversations into database when received stop signal"""
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
    """
    Make new bot with default parse mode to HTML and disabled web page preview
    Make Dispatcher with PGPersistence and set JobQueue

    Return value: (dispatcher, bot, job_queue)
    """
    logger.info('Connecting bot...')
    new_bot = Bot(
        token=config.BOT_TOKEN,
        defaults=Defaults(
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )
    )
    jq = JobQueue()
    persistence = PGPersistence()
    dp = Dispatcher(
        bot=new_bot,
        update_queue=None,
        use_context=True,
        job_queue=jq,
        persistence=persistence,
    )
    jq.set_dispatcher(dp)
    jq.start()
    logger.info('Bot connected successfully')
    return dp, new_bot, jq


def add_handlers(dp: Dispatcher):
    for name, handler in hdl.handlers.items():
        logger.info('Adding ' + name + ' handler')
        dp.add_handler(handler)
        logger.info('Handler added successfully')


# defining logger
logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')

# setting bot
dispatcher, bot, job_queue = connect_bot()

# setting error handler
dispatcher.add_error_handler(callback=hdl.error_callback)

# add handlers to dispatcher
add_handlers(dispatcher)

# load saved jobs from database
jobs.load_jobs(job_queue)

# set up web page to receive updates from Telegram
get_app_route(bot, dispatcher, db.update_user_info)

logger.info('Staring bot...')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PORT)

# TODO:
#  CLIENT
#  missing links (10/20)
#  mark tasks in tables
#  add to /today links
#  teachers info
#  add deadlines
#  add everyday deadlines
#  PE self timetable
#  other groups
#  make ls pages +
#  SERVER
#  make enums
#  mlw_tools normal errors
#  fix buttons copypaste
#  make chat_data persistent
#  nosql -> sql
#  language_code sometimes is null

# TODO heroku:
#  all done by now
