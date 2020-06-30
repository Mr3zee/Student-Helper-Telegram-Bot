from telegram import ParseMode, Bot
from telegram.ext import Updater, Dispatcher, Defaults

import FilmsBot.config as config
import log
import FilmsBot.handler as hdl


def connect_bot():
    log.log("Connecting bot...")
    bot = Bot(
        token=config.TG_TOKEN,
        defaults=Defaults(
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
        )
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )
    dispatcher = updater.dispatcher
    log.log_done()
    log.log_bot(updater.bot.get_me())
    return updater, dispatcher


def add_handlers(dispatcher: Dispatcher):
    for name, handler in hdl.handlers.items():
        log.log("Adding " + name + "_handler...")
        dispatcher.add_handler(handler)
        log.log_done()
    log.nl()


def start_bot(updater: Updater):
    log.log_nl("Starting bot")
    updater.start_polling()
    updater.idle()


def main():
    updater, dispatcher = connect_bot()

    add_handlers(dispatcher)

    start_bot(updater)


if __name__ == '__main__':
    main()
