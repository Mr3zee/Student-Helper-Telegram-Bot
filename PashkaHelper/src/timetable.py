from src.subject import subjects
from src.message import get_text
from config import service_file_path, timetable_url
from src.time_management import get_week_parity

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

INTRAMURAL, EXTRAMURAL, BOTH_ATTENDANCE = 'offline', 'online', 'both'
EVEN, ODD, BOTH_PARITY = 'even', 'odd', 'both'
subject_template = '%(time)s | %(subject)s | %(teacher)s | %(place)s'
subject_template_parity = '%(time)s | %(parity)s | %(subject)s | %(teacher)s | %(place)s'


def __rm_blanks(subject_row):
    for a in range(len(subject_row) - 1, -1, -1):
        if not subject_row[a].isspace() and subject_row[a] != '|':
            return subject_row[:a + 1]


def get_weekday_timetable(weekday: str, subject_names, attendance, language_code):
    if weekday == 'sunday':
        return get_text('today_sunday_text', language_code=language_code)

    template = get_text('weekday_text', language_code)
    weekday_text = get_text(f'{weekday}_name', language_code)

    subjects1, subjects2, parity = SERVER.get_timetable(weekday=weekday, subject_names=subject_names,
                                                        attendance=attendance)
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


def __make_timetable(subjects_dict, template):
    return '\n'.join(list(map(lambda a: __rm_blanks(template % a), subjects_dict)))


def get_timetable_by_index(day: int, subject_names, attendance, language_code):
    return get_weekday_timetable(weekdays[day], subject_names, attendance, language_code)


def get_subject_timetable(sub_name, subtype, attendance, language_code):
    timetable = SERVER.get_subject_timetable(sub_name, subtype, attendance)
    if not timetable:
        return ''

    template = get_text('subject_timetable_text', language_code=language_code)

    for weekday, [sub1, sub2] in timetable.items():
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
    def __subject_compare(subject_set):
        def inner(row):
            return row[2] in subject_set

        return inner

    @staticmethod
    def __accept_parity(sub_parity, week_parity):
        return sub_parity == week_parity or sub_parity == BOTH_PARITY or week_parity == BOTH_PARITY

    def get_timetable(self, weekday, subject_names, attendance):
        values = self.__get_values_from_table()
        start_row, end_row = Server.__find_weekday_table(values, weekday)
        week_parity = get_week_parity()
        sub_filter = Server.__subject_compare(subject_names)
        if attendance == BOTH_ATTENDANCE:
            offline_dict = Server.__parse_and_make(values, start_row, end_row, INTRAMURAL, week_parity, sub_filter)
            online_dict = Server.__parse_and_make(values, start_row, end_row, EXTRAMURAL, week_parity, sub_filter)
            return offline_dict, online_dict, week_parity
        else:
            return Server.__parse_and_make(values, start_row, end_row, attendance, week_parity, sub_filter), None, week_parity

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
    def __parse_and_make(values, start_row, end_row, attendance, week_parity=BOTH_PARITY, sub_filter=None):
        table = Server.__parse_table(values, start_row, end_row, attendance)
        return Server.__make_subject_dict(table, week_parity, sub_filter)

    @staticmethod
    def __parse_table(table, start_row, end_row, attendance):
        [start_col, end_col] = Server.__attendance[attendance]
        retval = []
        for row in range(start_row, end_row):
            if table[row][start_col + 2] != '':
                retval.append(table[row][start_col + 1:end_col - Server.__number_of_cols])
        return retval

    @staticmethod
    def __make_subject_dict(raw_subjects, week_parity=BOTH_PARITY, subject_filter=None):
        if subject_filter is None:
            subject_filter = Server.__true_filter
        retval = []
        for row in raw_subjects:
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

    def get_subject_timetable(self, sub_name, subtype, attendance):
        subject_filter = Server.__subject_compare(subjects[sub_name].get_all_timetable_names(subtype))
        values = self.__get_values_from_table()
        retval = {}
        for weekday in Server.__weekdays_map.keys():
            start_row, end_row = Server.__find_weekday_table(values, weekday)
            if attendance == BOTH_ATTENDANCE:
                offline_dict = Server.__parse_and_make(values, start_row, end_row, INTRAMURAL,
                                                       sub_filter=subject_filter)
                online_dict = Server.__parse_and_make(values, start_row, end_row, EXTRAMURAL, sub_filter=subject_filter)
                if offline_dict or online_dict:
                    retval[weekday] = [offline_dict, online_dict]
            else:
                sub_dict = Server.__parse_and_make(values, start_row, end_row, attendance, sub_filter=subject_filter)
                if sub_dict:
                    retval[weekday] = [sub_dict, None]
        return retval


SERVER = Server.get_instance()
