from datetime import datetime, timedelta
from subject import subjects

from time_management import timezone_converter
from message import get_text

users = {}


def set_default_user_parameters(user_id):
    if user_id in users:
        return
    users[user_id] = {
        'name': 'unknown',
        'attendance': 'both',
        'message_status': 'allowed',
        'message_time': '7:30',
        'utcoffset': '+3',
        'os': None,
        'sp': None,
        'history': None,
        'eng': None,
    }


def get_user(user_id, language_code):
    data = users[user_id]
    retval = {}
    for key, value in data.items():
        if (key == 'name' and value != 'unknown') or (key == 'message_time') or (key == 'utcoffset'):
            retval[key] = value
            continue
        elif not value:
            value = 'all'
        text = get_text(f'{f"{key}_{value}"}_user_data_text', language_code)
        if key == 'eng' and value != 'all':
            text = get_text('eng_std_user_data_text', language_code).format(text)
        retval[key] = text
    return retval


def get_user_subtype(user_id, sub_name):
    return users[user_id].get(sub_name)


def get_user_subject_names(user_id):
    retval = set()
    for subject in subjects:
        retval = retval.union(subjects[subject].get_all_timetable_names(get_user_subtype(user_id, subject)))
    return retval


def set_user_subtype(user_id, subject, new_course):
    if new_course == 'all':
        new_course = None
    users[user_id][subject] = new_course


def get_user_attendance(user_id):
    return users[user_id]['attendance']


def set_user_attendance(user_id, attendance):
    users[user_id]['attendance'] = attendance


def get_user_message_status(user_id):
    return users[user_id]['message_status']


def set_user_message_status(user_id, status):
    users[user_id]['message_status'] = status


def get_username(user_id):
    return users[user_id]['name']


def set_username(user_id, new_name):
    users[user_id]['name'] = new_name


def get_user_utcoffset(user_id):
    return timedelta(hours=int(users[user_id]['utcoffset']))


def set_user_utcoffset(user_id, new_tzinfo):
    users[user_id]['utcoffset'] = new_tzinfo


def valid_utcoffset(new_tzinfo: str):
    try:
        return abs(int(new_tzinfo)) < 13
    except ValueError:
        return False


def get_user_mailing_time_with_offset(user_id):
    return timezone_converter(
        input_date=datetime.strptime(users[user_id]['message_time'], '%H:%M'),
        utcoffset=get_user_utcoffset(user_id)
    ).time()


def set_user_mailing_time(user_id, new_time):
    users[user_id]['message_time'] = new_time.strip()


def valid_time(new_time: str):
    try:
        datetime.strptime(new_time.strip(), '%H:%M')
        return True
    except ValueError:
        return False
