import datetime


def log(message):
    print(message, end="")


def log_nl(message):
    log(message)
    nl()


def log_done():
    log_nl(" - OK")


def nl():
    log('\n')


def log_bot(bot):
    log("Bot: " + str(bot) + "\n\n")


def log_fail(e):
    log_nl(" - FAILED (" + str(e) + ")")


def log_sep():
    nl()
    log_nl("-"*115)


DEBUG = 1


def log_handler(f):
    if not DEBUG:
        return lambda *args, **kwargs: f(*args, **kwargs)

    def inner(*args, **kwargs):
        log_sep()
        log_nl("Date: " + datetime.datetime.now().isoformat())
        log_nl("User: " + str(args[0].effective_user))
        if args[0].message:
            log_nl("Message:  " + args[0].message.text)
        elif args[0].callback_query:
            log_nl("Query: " + str(args[0].callback_query.data))
        log("Process: \'" + f.__name__ + "\' handler called...")
        try:
            retval = f(*args, **kwargs)
            log_done()
            return retval
        except Exception as e:
            log_fail(e)
            raise e
    return inner
