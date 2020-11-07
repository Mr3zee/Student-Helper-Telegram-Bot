from datetime import datetime, date, timedelta

from static import consts

# week, from which week parity should be counting
ZERO_WEEK = date(2020, 9, 3).isocalendar()[1]

weekdays = {
    0: consts.MONDAY,
    1: consts.TUESDAY,
    2: consts.WEDNESDAY,
    3: consts.THURSDAY,
    4: consts.FRIDAY,
    5: consts.SATURDAY,
    6: consts.SUNDAY,
}


def get_today_weekday(utcoffset: int) -> str:
    """get current weekday"""
    return weekdays[(datetime.utcnow() + timedelta(hours=utcoffset)).weekday()]


def to_utc_converter(input_time: datetime, utcoffset: timedelta):
    """convert date with offset to utc"""
    return input_time - utcoffset


def get_week_parity():
    """return week parity according to ZERO_WEEK"""
    return consts.WEEK_EVEN if (datetime.today().isocalendar()[1] - ZERO_WEEK) % 2 != 0 else consts.WEEK_ODD


def today_id(utcoffset: timedelta):
    return get_today(utcoffset).toordinal()


def get_today(utcoffset):
    return datetime.utcnow() + utcoffset


def get_next_day(day: date, offset: int) -> date:
    return day + timedelta(days=offset)
