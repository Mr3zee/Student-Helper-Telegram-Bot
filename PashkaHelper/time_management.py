import pytz
from datetime import datetime, date

zero_week = date(2020, 9, 3).isocalendar()[1]


def get_weekday():
    return timezone_converter(datetime.utcnow()).weekday()


def timezone_converter(input_dt, current_tz='UTC', target_tz='Europe/Moscow'):
    current_tz = pytz.timezone(current_tz)
    target_tz = pytz.timezone(target_tz)
    target_dt = current_tz.localize(input_dt).astimezone(target_tz)
    return target_tz.normalize(target_dt)


def get_week_parity():
    return 'odd' if (datetime.today().isocalendar()[1] - zero_week % 2 != 0) else 'even'
