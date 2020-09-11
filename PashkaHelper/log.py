import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')

offset = ' ' * 4
DEBUG = False


def log_handler(f):
    if not DEBUG:
        return f

    def inner(*args, **kwargs):
        message = f'Handler \'{f.__name__}\' called \n{offset}User: {args[0].effective_user}\n'
        if args[0].message:
            pass
            message += f'{offset}Message: {args[0].message.text}\n'
        elif args[0].callback_query:
            pass
            message += f'{offset}Query: {str(args[0].callback_query.data)}\n'
        message += f'{offset}Result: '
        try:
            retval = f(*args, **kwargs)
            logger.info(message + 'DONE')
            return retval
        except Exception as e:
            logger.info(message + 'FAILED')
            raise e
    return inner
