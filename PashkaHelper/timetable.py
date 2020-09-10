from PashkaHelper.message import get_text
from PashkaHelper.config import service_file_path, timetable_name

import logging
import pygsheets

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')

weekdays = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    3: 'thursday',
    4: 'friday',
    5: 'saturday',
    6: 'sunday',
}


def get_timetable(day: str, language_code):
    return get_text('timetable_day_text', language_code).format(get_text(day + '_name', language_code), 'в разработке')


def get_timetable_by_index(day: int, language_code):
    return get_timetable(weekdays[day], language_code)


class Server:
    __instance = None

    def __init__(self):
        logger.info('Starting Server...')
        if not Server.__instance:
            self.__gc = pygsheets.authorize(service_file=service_file_path)
            # self.__sh_timetable = self.__gc.open(timetable_name)
            # self.__wks = self.__sh_timetable.sheet1

        logger.info('Server started successfully')

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Server()
        return cls.__instance


SERVER = Server.get_instance()
