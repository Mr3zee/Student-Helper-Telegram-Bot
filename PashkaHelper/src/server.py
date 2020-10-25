import pygsheets

from static import consts
from static.config import timetable_url, service_file_path
import src.subject as sub

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(name)s, %(asctime)s - %(levelname)s : %(message)s')


class Server:
    """
    Server class is responsible for talking with different API's and parsing their data
    APIs:
    Google Sheet API - for parsing tables with data such as timetables deadlines and more
    """

    # Server is singleton
    __instance = None

    # --- params for parsing timetable ---
    # timetable rectangle
    __tt_top_left = 'B1'
    __tt_bottom_right = 'O49'

    # wight of timetable
    __tt_number_of_cols = 14

    # attendance cols
    __tt_attendance = {
        consts.ATTENDANCE_OFFLINE: [0, 6],
        consts.ATTENDANCE_ONLINE: [7, 13],
        consts.ATTENDANCE_BOTH: [0, 13],
    }

    # weekdays in timetable
    __tt__weekdays_map = {
        consts.MONDAY: 'пн',
        consts.TUESDAY: 'вт',
        consts.WEDNESDAY: 'ср',
        consts.THURSDAY: 'чт',
        consts.FRIDAY: 'пт',
        consts.SATURDAY: 'сб',
    }

    # parity in timetable
    __tt_week_parity_map = {
        'ч': consts.WEEK_EVEN,
        'н': consts.WEEK_ODD,
        'ч/нч': consts.WEEK_BOTH,
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

    def get_weekday_timetable(self, weekday, valid_subject_names, attendance, week_parity) -> tuple:
        """returns weekday as dict {attendance: list of subjects}"""

        # get all values
        values = self.__get_values_from_table()
        # get the filter for user's subjects
        subject_filter = Server.__subject_compare(valid_subject_names)

        return Server.__make_weekday_table(
            values=values, weekday=weekday,
            attendance=attendance, week_parity=week_parity,
            subject_filter=subject_filter,
        )

    def get_subject_timetable(self, subject, subtype, attendance) -> dict:
        """get timetable for specified subject"""

        # get all values
        values = self.__get_values_from_table()
        # get the filter for the subject
        subject_filter = Server.__subject_compare(subject_set=sub.SUBJECTS[subject].get_all_timetable_names(subtype))
        # dict {weekday: timetable}
        retval = {}
        for weekday in Server.__tt__weekdays_map.keys():
            retval[weekday] = Server.__make_weekday_table(
                values=values, weekday=weekday,
                attendance=attendance, week_parity=consts.WEEK_BOTH,
                subject_filter=subject_filter,
            )
        return retval

    @staticmethod
    def __make_weekday_table(values, weekday, attendance, subject_filter, week_parity=consts.WEEK_BOTH) -> tuple:
        """
        returns tuple of timetables
        ((online, None) or (offline, None)) xor (online, offline)
        """

        # get weekday frame
        start_row, end_row = Server.__find_weekday_frame(values, weekday)
        if attendance == consts.ATTENDANCE_BOTH:
            online_dict = Server.__parse_and_make(
                values=values,
                start_row=start_row, end_row=end_row,
                attendance=consts.ATTENDANCE_ONLINE, week_parity=week_parity,
                subject_filter=subject_filter,
            )
            offline_dict = Server.__parse_and_make(
                values=values,
                start_row=start_row, end_row=end_row,
                attendance=consts.ATTENDANCE_OFFLINE, week_parity=week_parity,
                subject_filter=subject_filter,
            )
            return online_dict, offline_dict
        else:
            ret_dict = Server.__parse_and_make(
                values=values,
                start_row=start_row, end_row=end_row,
                attendance=attendance, week_parity=week_parity,
                subject_filter=subject_filter,
            )
            return ret_dict, None

    def __get_values_from_table(self):
        """gets timetable from google sheets"""
        return self.__wks.get_values(self.__tt_top_left, self.__tt_bottom_right)

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
        table_weekday = Server.__tt__weekdays_map[weekday]
        found_start = False
        start_row = None
        end_row = None
        # [start_row, end_row)
        for row in range(len(table)):
            # first row of next weekday or the ending of the table
            if found_start and (table[row][0] in Server.__tt__weekdays_map.values() or row == len(table) - 1):
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
        table = Server.__parse_table(values, start_row, end_row, attendance)
        return Server.__make_subject_dict(table, week_parity, subject_filter)

    @staticmethod
    def __parse_table(table, start_row, end_row, attendance):
        """takes not empty rows from weekday's frame"""
        [start_col, end_col] = Server.__tt_attendance[attendance]
        # cols: [id, time, parity, subject, teacher, place]
        retval = []
        for row in range(start_row, end_row):
            # check if subject's row is empty, as time col might be empty
            if table[row][start_col + 2] != '':
                retval.append(table[row][start_col + 1:end_col - Server.__tt_number_of_cols])
        return retval

    @staticmethod
    def __make_subject_dict(raw_subjects, week_parity=consts.WEEK_BOTH, subject_filter=None) -> list:
        """makes as dict out of each row"""
        if subject_filter is None:
            subject_filter = Server.__true_filter
        retval = []
        for row in raw_subjects:
            subject_parity = Server.__tt_week_parity_map[row[1]]
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
