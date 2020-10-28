from static import consts


def to_not_attendance(attendance):
    """convert attendance to opposite"""
    if attendance == consts.ATTENDANCE_ONLINE:
        return consts.ATTENDANCE_OFFLINE
    elif attendance == consts.ATTENDANCE_OFFLINE:
        return consts.ATTENDANCE_ONLINE
    elif attendance == consts.ATTENDANCE_BOTH:
        return consts.ATTENDANCE_ONLINE
    else:
        raise ValueError(f'Invalid attendance type : {attendance}')


def to_not_help_page(page):
    """convert help page to opposite"""
    if page == consts.MAIN_PAGE:
        return consts.TIMETABLE_PAGE
    elif page == consts.TIMETABLE_PAGE:
        return consts.MAIN_PAGE
    else:
        raise ValueError(f'Invalid page type : {page}')


def to_not_week_parity(week_parity):
    """convert week parity to opposite"""
    if week_parity == consts.WEEK_ODD:
        return consts.WEEK_EVEN
    elif week_parity == consts.WEEK_EVEN:
        return consts.WEEK_ODD
    else:
        raise ValueError(f'Invalid week parity : {week_parity}')


def if_none(val, default):
    """returns val if val is not None else default"""
    return val if val is not None else default


def get_value(dct: dict, *keys):
    """access dict with given keys"""
    for key in keys:
        dct = dct.get(key, {})
    return dct
