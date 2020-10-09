def to_not_attendance(attendance):
    if attendance == 'online':
        return 'offline'
    elif attendance == 'offline':
        return 'online'
    elif attendance == 'both':
        return 'online'
    else:
        raise ValueError(f'Invalid attendance type : {attendance}')


def to_not_page(page):
    if page == 'main':
        return 'timetable'
    elif page == 'timetable':
        return 'main'
    else:
        raise ValueError(f'Invalid page type : {page}')


def to_not_week_parity(week_parity):
    if week_parity == 'odd':
        return 'even'
    elif week_parity == 'even':
        return 'odd'
    else:
        raise ValueError(f'Invalid week parity : {week_parity}')


def if_none(not_none, default):
    return not_none if not_none is not None else default