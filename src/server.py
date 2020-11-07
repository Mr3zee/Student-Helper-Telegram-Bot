import datetime
import random
import re
from abc import ABC, abstractmethod
from typing import List

import pygsheets
from pygsheets import Cell
from pygsheets.client import Client
from pygsheets.worksheet import Worksheet

from static import consts
from static.config import TIMETABLE_URL, QUOTES_URL, DEADLINES_URL, service_file_path
import src.subject as sub

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')

EMPTY_WEEKDAY_TIMETABLE = {'online': [], 'offline': []}


class Server(ABC):
    """Abstract Server class is responsible for talking with Google Sheet API"""
    __gc: Client = pygsheets.authorize(service_file=service_file_path)
    __instance = None

    # need to be specified in child classes
    @property
    @abstractmethod
    def _url(self):
        pass

    def __init__(self, url):
        if not self.__instance:
            logger.info(f'Starting {self.__class__.__name__} server...')
            self._sh = self.__gc.open_by_url(url)
            self._wks: Worksheet = self._sh.sheet1
            logger.info('Server started')

    # Server is singleton
    @classmethod
    def get_instance(cls, url=None):
        if cls.__instance is None:
            if url is None and cls._url is None:
                raise ValueError(f'Url for server class {cls.__name__} isn\'t specified')
            cls.__instance = cls(url or cls._url)
        return cls.__instance


class Timetable(Server):
    """Server class for timetable"""
    _url = TIMETABLE_URL

    # timetable rectangle
    __top_left = 'B1'
    __bottom_right = 'O49'

    # wight of timetable
    __number_of_cols = 14

    # timetable columns by attendance
    __attendance_cols = {
        consts.ATTENDANCE_OFFLINE: [0, 6],
        consts.ATTENDANCE_ONLINE: [7, 13],
        consts.ATTENDANCE_BOTH: [0, 13],
    }

    # weekdays in timetable
    __weekdays_map = {
        consts.MONDAY: 'пн',
        consts.TUESDAY: 'вт',
        consts.WEDNESDAY: 'ср',
        consts.THURSDAY: 'чт',
        consts.FRIDAY: 'пт',
        consts.SATURDAY: 'сб',
    }

    # parity in timetable
    __week_parity_map = {
        'ч': consts.WEEK_EVEN,
        'н': consts.WEEK_ODD,
        'ч/нч': consts.WEEK_BOTH,
    }

    def get_weekday_timetable(self, weekday, valid_subject_names, attendance, week_parity) -> dict:
        """returns weekday as dict {attendance: list of subjects}"""

        # get all values
        values = self.__get_tt_values()
        # get the filter for user's subjects
        subject_filter = Timetable.__subject_compare(valid_subject_names)

        return Timetable.__make_weekday_table(
            values=values, weekday=weekday,
            attendance=attendance, week_parity=week_parity,
            subject_filter=subject_filter,
        )

    def get_subject_timetable(self, subject, subtype, attendance) -> dict:
        """get timetable for specified subject"""

        # get all values
        values = self.__get_tt_values()
        # get the filter for the subject
        subject_filter = Timetable.__subject_compare(subject_set=sub.SUBJECTS[subject].get_all_timetable_names(subtype))
        # dict {weekday: {online: tt, offline: tt}} - values maybe None
        retval = {}
        for weekday in Timetable.__weekdays_map.keys():
            weekday_table = Timetable.__make_weekday_table(
                values=values, weekday=weekday,
                attendance=attendance, week_parity=consts.WEEK_BOTH,
                subject_filter=subject_filter,
            )
            if weekday_table != EMPTY_WEEKDAY_TIMETABLE:
                retval[weekday] = weekday_table
        return retval

    @staticmethod
    def __make_weekday_table(values, weekday, attendance, subject_filter, week_parity=consts.WEEK_BOTH) -> dict:
        """returns dict {'online': tt1, 'offline': tt2}"""

        # get weekday frame
        start_row, end_row = Timetable.__find_weekday_frame(values, weekday)

        # make dicts according to attendance
        online_dict = (Timetable.__parse_and_make(
            values=values,
            start_row=start_row, end_row=end_row,
            attendance=consts.ATTENDANCE_ONLINE, week_parity=week_parity,
            subject_filter=subject_filter,
        ) if attendance != consts.ATTENDANCE_OFFLINE else [])
        offline_dict = (Timetable.__parse_and_make(
            values=values,
            start_row=start_row, end_row=end_row,
            attendance=consts.ATTENDANCE_OFFLINE, week_parity=week_parity,
            subject_filter=subject_filter,
        ) if attendance != consts.ATTENDANCE_ONLINE else [])

        return {'online': online_dict, 'offline': offline_dict}

    def __get_tt_values(self):
        """gets timetable from google sheets"""
        return self._wks.get_values(self.__top_left, self.__bottom_right)

    @staticmethod
    def __true_filter(*args, **kwargs):
        """returns True"""
        return True

    @staticmethod
    def __subject_compare(subject_set: set):
        """filter for subjects, checks if provided row is for valid subject"""

        # row: [time, parity, subject, teacher, place]
        def inner(row):
            return row[2] in subject_set

        return inner

    @staticmethod
    def __accept_parity(sub_parity, required_parity) -> bool:
        """checks if subject's parity meets the requirements"""
        return sub_parity == required_parity or sub_parity == consts.WEEK_BOTH or required_parity == consts.WEEK_BOTH

    @staticmethod
    def __find_weekday_frame(table, weekday):
        """finds frame for weekday in timetable"""
        table_weekday = Timetable.__weekdays_map[weekday]
        found_start = False
        start_row = None
        end_row = None
        # [start_row, end_row)
        for row in range(len(table)):
            # first row of next weekday or the ending of the table
            if found_start and (table[row][0] in Timetable.__weekdays_map.values() or row == len(table) - 1):
                end_row = row
                break
            # first row of the frame
            if table[row][0] == table_weekday:
                start_row = row + 1
                found_start = True
        return start_row, end_row

    @staticmethod
    def __parse_and_make(values, start_row, end_row, attendance, week_parity=consts.WEEK_BOTH, subject_filter=None):
        """takes rows from weekday frame and makes dict"""
        table = Timetable.__parse_table(values, start_row, end_row, attendance)
        return Timetable.__make_subject_dict(table, week_parity, subject_filter)

    @staticmethod
    def __parse_table(table, start_row, end_row, attendance):
        """takes not empty rows from weekday's frame"""
        [start_col, end_col] = Timetable.__attendance_cols[attendance]
        # cols: [id, time, parity, subject, teacher, place]
        retval = []
        for row in range(start_row, end_row):
            # check if subject's row is empty, as time col might be empty
            if table[row][start_col + 2] != '':
                retval.append(table[row][start_col + 1:end_col - Timetable.__number_of_cols])
        return retval

    @staticmethod
    def __make_subject_dict(raw_subjects, week_parity=consts.WEEK_BOTH, subject_filter=None) -> list:
        """makes as dict out of each row"""
        if subject_filter is None:
            subject_filter = Timetable.__true_filter
        retval = []
        for row in raw_subjects:
            subject_parity = Timetable.__week_parity_map[row[1]]
            if Timetable.__accept_parity(subject_parity, week_parity) and subject_filter(row):
                subject = {
                    'time': row[0],
                    'parity': row[1],
                    'subject': row[2],
                    'teacher': row[3],
                    'place': row[4]
                }
                retval.append(subject)
        return retval


class Deadlines(Server):
    """Server class for deadlines"""
    _url = DEADLINES_URL

    __column_frame = ('4', '14')  # dl frame
    __offset = 1  # index of the first dl column
    __zero_day_id = datetime.date(2020, 10, 26).toordinal()  # first day in table
    __subject_col = 'A'  # col with subject names
    __weekday_row = 3  # row with weekday names

    def get_deadlines(self, day: int):
        """get deadlines as (subject, deadline)"""

        # find day's index from zero day
        day_offset = day - self.__zero_day_id

        # find day's column
        column = self.__column_name(day_offset // 7 + day_offset)  # every week has one blank col

        weekday = self._wks.get_value(f'{column}{self.__weekday_row}')

        retval = []
        dls = zip(self.__get_col(self.__subject_col), self.__get_col(column))
        for subject, dl in dls:  # type: List[Cell]
            formatted_dl = Deadlines.__delete_links(dl[0].value_unformatted)
            if formatted_dl != '':
                retval.append((subject[0].value_unformatted, formatted_dl))
        return retval, weekday

    def __column_name(self, index):
        """column index -> SpreadSheets column name"""
        ret_val = ''
        index += self.__offset + 1
        while index > 0:
            index, ch = divmod(index - 1, 26)
            ret_val += chr(ch + ord('a'))
        return ret_val[::-1].capitalize()

    def __get_col(self, col):
        """get column for deadlines data"""
        return self._wks.get_values(
            start=col + self.__column_frame[0],
            end=col + self.__column_frame[1],
            returnas='cells',
        )

    @staticmethod
    def __delete_links(cell):
        """remove words (usually not formatted links) from text: hey *link* -> hey"""
        return re.sub(r'\*.*\*', '', cell).strip()


class Quotes(Server):
    """Server class for quotes"""
    _url = QUOTES_URL

    def get_random_quote(self):
        """return random quote"""
        values = self.__get_quotes()
        count = len(values)
        index = random.randint(0, count - 1)
        quote, author = values[index]
        # find quote's author
        while not author and index > 0:
            index = index - 1
            author = values[index][1]
        return quote, author

    def __get_quotes(self):
        """return all quotes"""
        return self._wks.get_all_values(
            include_tailing_empty_rows=False,
        )[1:]  # first row is cols names
