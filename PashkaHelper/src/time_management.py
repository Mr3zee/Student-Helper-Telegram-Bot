import pytz
from datetime import datetime, date, timedelta

ZERO_WEEK = date(2020, 9, 3).isocalendar()[1]

SERVER_TZ = pytz.timezone('UTC')
MOSCOW_TZ = pytz.timezone('Europe/Moscow')


def get_weekday(utcoffset: timedelta):
    return (datetime.utcnow() + utcoffset).weekday()


def to_utc_converter(input_date: datetime, utcoffset: timedelta):
    return input_date - utcoffset


def get_week_parity():
    return 'even' if (datetime.today().isocalendar()[1] - ZERO_WEEK) % 2 != 0 else 'odd'
