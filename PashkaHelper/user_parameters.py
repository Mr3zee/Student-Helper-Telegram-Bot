from datetime import datetime

from timetable import BOTH_ATTENDANCE


def get_user_course(user_id, sub_name):
    return sub_name, BOTH_ATTENDANCE


user = {
    'name': 'Сысоев Александр Александрович',
    'attendance': 'intramural',
    'message_status': 'Да',
    'message_time': '7:30',
    'tzinfo': '+3',
    'eng': '2-ИТИПКТ-С2/1',
    'history': 'international',
    'sp': 'kotlin',
    'os': 'adv',
}


def set_user_course(user_id, subject, new_course):
    user[subject] = new_course


def set_user_attendance(user_id, attendance):
    user['attendance'] = attendance


def get_user(user_id):
    return user


def get_user_message_status(user_id):
    return 'forbidden' if user['message_status'] == 'Нет' else 'allowed'


def set_user_name(user_id, new_name):
    user['name'] = new_name


def set_user_message_status(user_id, status):
    user['message_status'] = ('Дa' if status == 'allowed' else 'Нет')


def valid_tzinfo(new_tzinfo: str):
    try:
        return abs(int(new_tzinfo)) < 13
    except ValueError:
        return False


def set_user_tzinfo(user_id, new_tzinfo):
    user['tzinfo'] = new_tzinfo


def valid_time(new_time: str):
    try:
        datetime.strptime(new_time.strip(), '%H:%M')
        return True
    except ValueError:
        return False


def set_user_message_time(user_id, new_time):
    user['message_time'] = new_time.strip()
