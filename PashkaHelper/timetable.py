from message import get_text
from config import service_file_path, timetable_url
from time_management import get_week_parity

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

INTRAMURAL, EXTRAMURAL, BOTH_ATTENDANCE = range(3)
EVEN, ODD, BOTH_PARITY = 'even', 'odd', 'both'
subject_template = '%(time)s | %(subject)s | %(teacher)s | %(place)s'


def get_timetable(weekday: str, attendance, language_code):
    if weekday == 'sunday':
        return get_text('today_sunday_text', language_code=language_code)

    template = get_text('weekday_text', language_code)
    subjects1, subjects2, parity = SERVER.get_timetable(weekday=weekday, attendance=attendance)
    parity_text = get_text(f'{parity}_week_text', language_code=language_code)
    timetable = get_text('{}_text'.format('intramural' if attendance != EXTRAMURAL else 'extramural'), language_code)
    timetable += '\n' + __make_timetable(subjects1)
    if subjects2:
        timetable += '\n\n' + get_text('extramural_text', language_code) + '\n'
        timetable += __make_timetable(subjects2)
    weekday_text = get_text(f'{weekday}_name', language_code)
    return template.format(weekday_text, parity_text, timetable)


def __make_timetable(subjects):
    return '\n'.join(list(map(lambda a: subject_template % a, subjects)))


def get_timetable_by_index(day: int, attendance, language_code):
    return get_timetable(weekdays[day], attendance, language_code)


class Server:
    __instance = None

    __top_left = 'B1'

    __bottom_right = 'O49'

    __number_of_cols = 14

    __attendance = {
        INTRAMURAL: [0, 6],
        EXTRAMURAL: [7, 13],
        BOTH_ATTENDANCE: [0, 13],
    }

    __weekdays_map = {
        'monday': 'пн',
        'tuesday': 'вт',
        'wednesday': 'ср',
        'thursday': 'чт',
        'friday': 'пт',
        'saturday': 'сб',
    }

    __week_parity_map = {
        'ч': 'even',
        'н': 'odd',
        'нч': 'both',
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
        week_parity = get_week_parity()
        if attendance == BOTH_ATTENDANCE:
            offline = Server.__parse_table(values, start_row, end_row, INTRAMURAL)
            online = Server.__parse_table(values, start_row, end_row, EXTRAMURAL)
            offline_dict = Server.__make_subject_dict(offline, week_parity)
            online_dict = Server.__make_subject_dict(online, week_parity)
            return offline_dict, online_dict, week_parity
        else:
            subjects = Server.__parse_table(values, start_row, end_row, attendance)
            return Server.__make_subject_dict(subjects, week_parity), None, week_parity

    @staticmethod
    def __find_weekday_table(table, weekday):
        table_weekday = Server.__weekdays_map[weekday]
        found = False
        start_row = None
        end_row = None
        for row in range(len(table)):
            if found and (table[row][0] in Server.__weekdays_map.values() or row == len(table) - 1):
                end_row = row
                break
            if table[row][0] == table_weekday:
                start_row = row + 1
                found = True
        return start_row, end_row

    @staticmethod
    def __parse_table(table, start_row, end_row, attendance):
        [start_col, end_col] = Server.__attendance[attendance]
        subjects = []
        for row in range(start_row, end_row):
            if table[row][start_col + 2] != '':
                subjects.append(table[row][start_col + 1:end_col - Server.__number_of_cols])
        return subjects

    @staticmethod
    def __make_subject_dict(subjects, week_parity):
        retval = []
        for row in subjects:
            subject_parity = Server.__week_parity_map[row[1]]
            if subject_parity == BOTH_PARITY or  subject_parity == week_parity:
                subject = {
                    'time': (row[0] if row[0] != '' else ' ' * 10),
                    'parity': row[1],
                    'subject': row[2],
                    'teacher': row[3],
                    'place': row[4]
                }
                retval.append(subject)
        return retval


SERVER = Server.get_instance()
