from message import get_text
from config import service_file_path, timetable_url
from time_management import get_week_parity

import logging
import pprint
import pygsheets

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')

pp = pprint.PrettyPrinter()

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
subject_template_parity = '%(time)s | %(parity)s | %(subject)s | %(teacher)s | %(place)s'


def get_weekday_timetable(weekday: str, attendance, language_code):
    if weekday == 'sunday':
        return get_text('today_sunday_text', language_code=language_code)

    template = get_text('weekday_text', language_code)
    weekday_text = get_text(f'{weekday}_name', language_code)

    subjects1, subjects2, parity = SERVER.get_timetable(weekday=weekday, attendance=attendance)
    parity_text = get_text(f'{parity}_week_text', language_code=language_code)

    if not subjects1:
        happy_text = get_text('happy_text', language_code=language_code)
        return template.format(weekday_text, parity_text, happy_text)

    weekday_timetable = __put_together(subjects1, subjects2, attendance, subject_template, language_code)
    return template.format(weekday_text, parity_text, weekday_timetable)


def __put_together(subjects1, subjects2, attendance, template, language_code):
    timetable = get_text('{}_text'.format('intramural' if attendance != EXTRAMURAL else 'extramural'), language_code)
    timetable += '\n' + __make_timetable(subjects1, template)

    if subjects2:
        timetable += '\n\n' + get_text('extramural_text', language_code) + '\n'
        timetable += __make_timetable(subjects2, template)
    return timetable


def __make_timetable(subjects, template):
    return '\n'.join(list(map(lambda a: template % a, subjects)))


def get_timetable_by_index(day: int, attendance, language_code):
    return get_weekday_timetable(weekdays[day], attendance, language_code)


def get_subject_timetable(subject_type, attendance, language_code):
    subjects = SERVER.get_subject(subject_type, attendance)
    if not subjects:
        return ''

    template = get_text('subject_timetable_text', language_code=language_code)

    for weekday, [sub1, sub2] in subjects.items():
        weekday_name = get_text(f'{weekday}_name', language_code=language_code)
        day_template = get_text('subject_day_template_text', language_code=language_code)
        subject_timetable = __put_together(sub1, sub2, attendance, subject_template_parity, language_code)
        template += day_template.format(weekday_name, subject_timetable)

    return template


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

    __subject_name_map = {
        'matan': {'МатАн (лк)', 'МатАн (пр)'},
        'eng': {'Английский'},
        'algo': {'АиСД (лк)', 'АиСД (пр)'},
        'discra': {'Дискретка (лк)', 'Дискретка (пр)'},
        'diffur': {'Диффуры (лк)', 'Диффуры (пр)'},
        'os_lite': {'OC (лк)'},
        'os_adv': {'ОС-adv (лк)', 'ОС-adv (пр)'},
        'os': {'ОС-adv (лк)', 'ОС-adv (пр)', 'OC (лк)'},
        'sp_android_ios': {'Android / iOS'},
        'sp_web': {'СП - Web (лк)', 'СП - Web (пр)'},
        'sp_cpp': {'C++ (лк)', 'C++ (пр)'},
        'sp_kotlin': {'Kotlin (лк)', 'Kotlin (пр)'},
        'sp': {'Kotlin (лк)', 'Kotlin (пр)',
               'C++ (лк)', 'C++ (пр)',
               'СП - Web (лк)', 'СП - Web (пр)',
               'Android / iOS',
               },
        'history': {'История'},
        'bjd': {}
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

    def __get_values_from_table(self):
        return self.__wks.get_values(self.__top_left, self.__bottom_right)

    @staticmethod
    def __true_filter(*args, **kwargs):
        return True

    @staticmethod
    def __parse_and_make(values, start_row, end_row, attendance, week_parity=BOTH_PARITY, filter_sub=None):
        table = Server.__parse_table(values, start_row, end_row, attendance)
        return Server.__make_subject_dict(table, week_parity, filter_sub)

    def get_timetable(self, weekday, attendance):
        values = self.__get_values_from_table()
        start_row, end_row = Server.__find_weekday_table(values, weekday)
        week_parity = get_week_parity()
        if attendance == BOTH_ATTENDANCE:
            offline_dict = Server.__parse_and_make(values, start_row, end_row, INTRAMURAL, week_parity)
            online_dict = Server.__parse_and_make(values, start_row, end_row, EXTRAMURAL, week_parity)
            return offline_dict, online_dict, week_parity
        else:
            return Server.__parse_and_make(values, start_row, end_row, attendance, week_parity), None, week_parity

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
    def __accept_parity(sub_parity, week_parity):
        return sub_parity == week_parity or sub_parity == BOTH_PARITY or week_parity == BOTH_PARITY

    @staticmethod
    def __make_subject_dict(subjects, week_parity=BOTH_PARITY, subject_filter=None):
        if subject_filter is None:
            subject_filter = Server.__true_filter
        retval = []
        for row in subjects:
            subject_parity = Server.__week_parity_map[row[1]]
            if Server.__accept_parity(subject_parity, week_parity) and subject_filter(row):
                subject = {
                    'time': row[0],
                    'parity': row[1],
                    'subject': row[2],
                    'teacher': row[3],
                    'place': row[4]
                }
                retval.append(subject)
        return retval

    @staticmethod
    def __subject_compare(subject_set):
        def inner(row):
            return row[2] in subject_set
        return inner

    def get_subject(self, subject_name, attendance):
        subject_filter = Server.__subject_compare(Server.__subject_name_map[subject_name])
        values = self.__get_values_from_table()
        retval = {}
        for weekday in Server.__weekdays_map.keys():
            start_row, end_row = Server.__find_weekday_table(values, weekday)
            if attendance == BOTH_ATTENDANCE:
                offline_dict = Server.__parse_and_make(values, start_row, end_row, INTRAMURAL,
                                                       filter_sub=subject_filter)
                online_dict = Server.__parse_and_make(values, start_row, end_row, EXTRAMURAL, filter_sub=subject_filter)
                if offline_dict or online_dict:
                    retval[weekday] = [offline_dict, online_dict]
            else:
                sub_dict = Server.__parse_and_make(values, start_row, end_row, attendance, filter_sub=subject_filter)
                if sub_dict:
                    retval[weekday] = [sub_dict, None]
        return retval


SERVER = Server.get_instance()
