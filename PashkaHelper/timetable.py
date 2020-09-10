from PashkaHelper.message import get_text

days = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    3: 'thursday',
    4: 'friday',
    5: 'saturday',
    6: 'sunday',
}


def get_timetable(day: str, language_code):
    return get_text('timetable_day_text', language_code).format(get_text(day + '_name', language_code), 'в разработке')


def get_timetable_by_index(day: int, language_code):
    return get_timetable(days[day], language_code)
