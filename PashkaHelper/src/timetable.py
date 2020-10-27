from src.text import get_text
from static import consts
from src.server import Server

SUBJECT_TEMPLATE = '%(time)s | %(subject)s | %(teacher)s | %(place)s'
SUBJECT_TEMPLATE_WITH_PARITY = '%(time)s | %(parity)s | %(subject)s | %(teacher)s | %(place)s'

SERVER = Server.get_instance()


def get_subject_timetable(subject, subtype, attendance, language_code):
    """get a timetable for specified subject"""

    # dict of {weekday: {'online': tt1, 'offline': tt2}}
    timetable = SERVER.get_subject_timetable(subject, subtype, attendance)

    # no timetable for this subject
    if not timetable:
        return get_text('no_subject_timetable_header_text', language_code=language_code).text()

    weekday_list = []
    for weekday, dct in timetable.items():
        # get subheader
        weekday_name = get_text(f'{weekday}_timetable_text', language_code=language_code).text()

        # make timetable
        subject_timetable = __put_together(template=SUBJECT_TEMPLATE_WITH_PARITY, language_code=language_code, **dct)
        if not subject_timetable:
            continue
        day_template = get_text('subject_day_template_text', language_code=language_code).text({
            consts.TIMETABLE: subject_timetable,
            consts.WEEKDAY: weekday_name,
        })
        weekday_list.append(day_template)

    header = get_text('subject_timetable_header_text', language_code=language_code).text()

    return header + '\n'.join(weekday_list)


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

    template.add_global_vars({
        consts.WEEKDAY: get_text(f'{weekday}_timetable_text', language_code).text(),
        consts.WEEK_PARITY: get_text(f'{week_parity}_week_timetable_text', language_code=language_code).text(),
    })

    # get timetables as dict
    subject_tt: dict = SERVER.get_weekday_timetable(
        weekday=weekday,
        valid_subject_names=subject_names,
        attendance=attendance,
        week_parity=week_parity
    )

    online_tt, offline_tt = subject_tt['online'], subject_tt['offline']

    # no subjects that day
    if not online_tt and not offline_tt:
        happy_text = get_text('happy_timetable_text', language_code=language_code).text()
        return template.text({consts.TIMETABLE: happy_text})

    # make full timetable
    weekday_timetable = __put_together(
        online=online_tt,
        offline=offline_tt,
        template=SUBJECT_TEMPLATE,
        language_code=language_code,
    )
    return template.text({consts.TIMETABLE: weekday_timetable})


def __put_together(online, offline, template, language_code):
    """make header(s) and glue it to timetable(s)"""
    timetable = []

    if online:
        header = get_text(f'online_timetable_text', language_code).text() + '\n'
        timetable.append(header + __make_timetable(online, template))

    # only True when attendance is both and in that case first is online and second is offline
    if offline:
        header = get_text('offline_timetable_text', language_code).text() + '\n'
        timetable.append(header + __make_timetable(offline, template))

    return '\n\n'.join(timetable)


def __rm_blanks(subject_row):
    """in templates rms blank spaces: 'time | subject | | ' -> 'time | subject' """
    for a in range(len(subject_row) - 1, -1, -1):
        if not subject_row[a].isspace() and subject_row[a] != '|':
            return subject_row[:a + 1]


def __make_timetable(subjects_dict, template):
    """rm blank spaces, substitute args and glue everything"""
    return '\n'.join(list(map(lambda a: __rm_blanks(template % a), subjects_dict)))
