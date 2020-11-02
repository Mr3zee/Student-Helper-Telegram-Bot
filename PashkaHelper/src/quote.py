from src.server import Server
from src.text import get_text

from static import consts

SERVER = Server.get_instance()


def random_quote(language_code):
    quote, author = SERVER.get_random_quote()
    return get_text('quote_text', language_code).text({
        consts.QUOTE: quote,
        consts.AUTHOR: author,
    })
