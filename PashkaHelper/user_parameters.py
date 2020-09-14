from datetime import datetime

users = {}


def set_default_user_parameters(user_id):
    if user_id in users:
        return
    users[user_id] = {
        'name': 'unknown',
        'attendance': 'both',
        'message_status': 'forbidden',
        'message_time': '7:30',
        'tzinfo': '+3',
        'os': None,
        'sp': None,
        'history': None,
        'eng': None,
    }


def get_user_course(user_id, sub_name):
    return get_user_subtype(user_id, sub_name), users[user_id]['attendance']


def get_user_subtype(user_id, sub_name):
    return users[user_id].get(sub_name)


def set_user_course(user_id, subject, new_course):
    users[user_id][subject] = new_course


def set_user_attendance(user_id, attendance):
    users[user_id]['attendance'] = attendance


def get_user(user_id):
    return users[user_id]


def get_user_message_status(user_id):
    return 'forbidden' if users[user_id]['message_status'] == 'Нет' else 'allowed'


def set_user_name(user_id, new_name):
    users[user_id]['name'] = new_name


def set_user_message_status(user_id, status):
    users[user_id]['message_status'] = ('Дa' if status == 'allowed' else 'Нет')


def valid_tzinfo(new_tzinfo: str):
    try:
        return abs(int(new_tzinfo)) < 13
    except ValueError:
        return False


def set_user_tzinfo(user_id, new_tzinfo):
    users[user_id]['tzinfo'] = new_tzinfo


def valid_time(new_time: str):
    try:
        datetime.strptime(new_time.strip(), '%H:%M')
        return True
    except ValueError:
        return False


def set_user_message_time(user_id, new_time):
    users[user_id]['message_time'] = new_time.strip()


def get_user_time(user_id):
    return datetime.strptime(users[user_id]['message_time'], '%H:%M').time()


def get_user_attendance(user_id):
    return users[user_id]['attendance']
