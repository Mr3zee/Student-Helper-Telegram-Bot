from src.text import get_text
from static import consts
from src.server import Server

subject_template = '%(time)s | %(subject)s | %(teacher)s | %(place)s'
subject_template_parity = '%(time)s | %(parity)s | %(subject)s | %(teacher)s | %(place)s'

SERVER = Server.get_instance()


def get_subject_timetable(subject, subtype, attendance, language_code):
    """get a timetable for specified subject"""
    timetable = SERVER.get_subject_timetable(subject, subtype, attendance)

    # no timetable for this subject
    if not timetable:
        return get_text('no_subject_timetable_header_text', language_code=language_code).text()

    template = get_text('subject_timetable_header_text', language_code=language_code).text()

    # timetable is dict of weekday: ([online, None] or [offline, None]) xor [online, offline]
    for weekday, (sub1, sub2) in timetable.items():
        # get header
        weekday_name = get_text(f'{weekday}_timetable_text', language_code=language_code).text()
        # get timetable
        subject_timetable = __put_together(sub1, sub2, attendance, subject_template_parity, language_code)
        if not subject_timetable:
            continue
        day_template = get_text('subject_day_template_text', language_code=language_code).text({
            consts.TIMETABLE: subject_timetable,
            consts.WEEKDAY: weekday_name,
        })
        template += day_template

    return template


def get_weekday_timetable(weekday: str, subject_names, attendance, week_parity, language_code) -> str:
    """
    makes timetable for specified day
    (subject_names: all user's subjects or subtypes)
    """

    # checks if it is sunday
    if weekday == consts.SUNDAY:
        return get_text('today_sunday_text', language_code=language_code).text()

    # get text templates
    template = get_text('weekday_text', language_code)
    weekday_text = get_text(f'{weekday}_timetable_text', language_code).text()

    # get timetables as lists
    # ((online, None) or (offline, None)) xor (online, offline)
    first_subject_list, second_subject_list = SERVER.get_weekday_timetable(
        weekday=weekday,
        valid_subject_names=subject_names,
        attendance=attendance,
        week_parity=week_parity
    )
    parity_text = get_text(f'{week_parity}_week_timetable_text', language_code=language_code).text()

    template.add_global_vars({
        consts.WEEKDAY: weekday_text,
        consts.WEEK_PARITY: parity_text,
    })

    # no subjects that day
    if not first_subject_list and not second_subject_list:
        happy_text = get_text('happy_timetable_text', language_code=language_code).text()
        return template.text({consts.TIMETABLE: happy_text})

    # make timetable
    weekday_timetable = __put_together(
        first_subject_list=first_subject_list,
        second_subject_list=second_subject_list,
        attendance=attendance,
        template=subject_template,
        language_code=language_code,
    )
    return template.text({consts.TIMETABLE: weekday_timetable})


def __put_together(first_subject_list, second_subject_list, attendance, template, language_code):
    """make header(s) and glue it to timetable(s)"""
    first = second = ''

    # if attendance is both then first is online
    if attendance == consts.ATTENDANCE_BOTH:
        attendance = consts.ATTENDANCE_ONLINE

    if first_subject_list:
        first = get_text(f'{attendance}_timetable_text', language_code).text() + '\n'
        first += __make_timetable(first_subject_list, template)

    # only True when attendance is both and in that case first is online and second is offline
    if second_subject_list:
        second = get_text('offline_timetable_text', language_code).text() + '\n'
        second += __make_timetable(second_subject_list, template)

    timetable = ''

    if first != '':
        timetable += first

    if second != '':
        timetable += ('\n\n' if first else '') + second

    return timetable


def __rm_blanks(subject_row):
    """in templates rms blank spaces: 'time | subject | | ' -> 'time | subject' """
    for a in range(len(subject_row) - 1, -1, -1):
        if not subject_row[a].isspace() and subject_row[a] != '|':
            return subject_row[:a + 1]


def __make_timetable(subjects_dict, template):
    """rm blank spaces, substitute args and glue everything"""
    return '\n'.join(list(map(lambda a: __rm_blanks(template % a), subjects_dict)))
