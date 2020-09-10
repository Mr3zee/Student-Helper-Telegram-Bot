from PashkaHelper.message import get_text


def get_timetable(day, language_code):
    return get_text('timetable_day_text', language_code).format(get_text(day + '_name', language_code), 'в разработке')
