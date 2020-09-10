from telegram import ParseMode, Bot
from telegram.ext import Updater, Dispatcher, Defaults

import PashkaHelper.config as config
import PashkaHelper.handler as hdl

import logging

logger = logging.getLogger(__name__)


def connect_bot():
    logger.info('Connecting bot...')
    bot = Bot(
        token=config.BOT_TOKEN,
        defaults=Defaults(
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )
    logger.info('Bot connected successfully')
    dispatcher = updater.dispatcher
    return updater, dispatcher


def add_handlers(dispatcher: Dispatcher):
    for name, handler in hdl.handlers.items():
        logger.info('Adding ' + name + ' handler')
        dispatcher.add_handler(handler)
        logger.info('Handler added successfully')


def start_bot(updater: Updater):
    logger.info('Starting bot...')
    updater.start_polling()
    updater.idle()


def main():
    logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')

    updater, dispatcher = connect_bot()

    add_handlers(dispatcher)

    start_bot(updater)


if __name__ == '__main__':
    main()
