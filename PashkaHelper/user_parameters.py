from timetable import BOTH_ATTENDANCE


def get_user_course(user_id, sub_name):
    return sub_name, BOTH_ATTENDANCE


def get_user_status(user_id):
    return 'allow'


user = {
    'name': 'Сысоев Александр Александрович',
    'attendance': 'intramural',
    'morning_message': 'Да',
    'message_time': '7:30',
    'tzinfo': '+3',
    'eng': '2-ИТИПКТ-С2/1',
    'history': 'international',
    'sp': 'kotlin',
    'os': 'adv',
}


def set_course(user_id, subject, new_course):
    user[subject] = new_course
    pass


def set_attendance(user_id, attendance):
    user['attendance'] = attendance
    pass


def get_user(user_id):
    return user
