from PashkaHelper.message import get_text
from PashkaHelper.config import service_file_path, timetable_url

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

INTRAMURAL, EXTRAMURAL = range(2)


def get_timetable(day: str, language_code):
    return get_text('timetable_day_text', language_code).format(get_text(day + '_name', language_code), 'в разработке')


def get_timetable_by_index(day: int, language_code):
    return get_timetable(weekdays[day], language_code)


class Server:
    __instance = None

    __top_left = 'B1'

    __bottom_right = 'M49'

    __number_of_cols = 12

    __attendance = {
        INTRAMURAL: [0, 5],
        EXTRAMURAL: [6, 11],
    }

    __weekdays_in_table = {
        'monday': 'пн',
        'tuesday': 'вт',
        'wednesday': 'ср',
        'thursday': 'чт',
        'friday': 'пт',
        'saturday': 'сб',
    }

    def __init__(self):
        logger.info('Starting Server...')
        if not Server.__instance:
            self.__gc = pygsheets.authorize(service_file=service_file_path)
            self.__sh_timetable = self.__gc.open_by_url(timetable_url)
            self.__wks = self.__sh_timetable.sheet1

        logger.info('Server started successfully')

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Server()
        return cls.__instance

    def get_timetable(self, weekday, attendance):
        values = self.__wks.get_values(self.__top_left, self.__bottom_right)
        start_row, end_row = Server.__find_weekday_table(values, weekday)
        [start_col, end_col] = Server.__attendance[attendance]
        subjects = Server.__parse_table(values, start_row, end_row, start_col, end_col)
        print(subjects)

    @staticmethod
    def __find_weekday_table(table, weekday):
        table_weekday = Server.__weekdays_in_table[weekday]
        found = False
        start_row = None
        end_row = None
        for row in range(len(table)):
            if found and (table[row][0] in Server.__weekdays_in_table.values() or row == len(table) - 1):
                end_row = row
                break
            if table[row][0] == table_weekday:
                start_row = row + 1
                found = True
        return start_row, end_row

    @staticmethod
    def __parse_table(table, start_row, end_row, start_col, end_col):
        subjects = []
        for row in range(start_row, end_row):
            if table[row][start_col + 2] != '':
                subjects.append(table[row][start_col + 1:end_col - Server.__number_of_cols])
        return subjects


SERVER = Server.get_instance()
SERVER.get_timetable('saturday', INTRAMURAL)
