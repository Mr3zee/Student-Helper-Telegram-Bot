from src.text import get_text
from static import consts
from src.server import Server

from telegram import Update
from telegram.ext import CallbackContext

from src import keyboard, database, common_functions as cf, time_management as tm

SUBJECT_TEMPLATE = '%(time)s | %(subject)s | %(teacher)s | %(place)s'
SUBJECT_TEMPLATE_WITH_PARITY = '%(time)s | %(parity)s | %(subject)s | %(teacher)s | %(place)s'

SERVER = Server.get_instance()


def timetable_callback(update: Update, data: list, language_code):
    """handles timetable callbacks"""
    subject_names = database.get_user_subject_names(user_id=update.effective_user.id)
    attendance, week_parity, weekday = data[1:-1]

    cf.edit_message(
        update=update,
        text=get_weekday_timetable(
            weekday=weekday,
            subject_names=subject_names,
            attendance=attendance,
            week_parity=week_parity,
            language_code=language_code,
        ),
        reply_markup=keyboard.timetable_keyboard(
            weekday=weekday,
            attendance=attendance,
            week_parity=week_parity,
            language_code=language_code,
        )
    )


def timetable_args_error(context: CallbackContext, chat_id, error_type, language_code):
    """send argument error message"""
    cf.send_message(
        context=context,
        chat_id=chat_id,
        text=get_text('timetable_args_error_text', language_code).text({'error_type': error_type}),
    )


def timetable(update: Update, context: CallbackContext):
    """
    sends timetable main page if no argument specified
    otherwise sends timetable for specified day: 0 - 7 -> monday - sunday
    """
    language_code = update.effective_user.language_code
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    args = context.args

    week_parity = tm.get_week_parity()
    attendance = database.get_user_attr(consts.ATTENDANCE, user_id)

    if len(args) > 1:
        # too many args
        return timetable_args_error(context, chat_id, 'many', language_code)
    elif len(args) == 1:
        # check if arg is integer
        try:
            weekday = int(args[0])
        except ValueError:
            return timetable_args_error(context, chat_id, 'type', language_code)
        if weekday > 6 or weekday < 0:
            # wrong day index
            return timetable_args_error(context, chat_id, 'value', language_code)
        # get timetable for specified day
        weekday = tm.weekdays[weekday]
        text = get_weekday_timetable(
            weekday=weekday,
            subject_names=database.get_user_subject_names(user_id),
            attendance=attendance,
            week_parity=week_parity,
            language_code=language_code,
        )
    else:
        # timetable main page
        weekday = tm.get_today_weekday(database.get_user_attr(consts.UTCOFFSET, user_id=user_id))
        text = get_text('timetable_text', language_code).text()
    cf.send_message(
        context=context,
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard.timetable_keyboard(
            weekday=weekday,
            attendance=attendance,
            week_parity=week_parity,
            language_code=language_code,
        ),
    )


def today(update: Update, context: CallbackContext):
    """sends today timetable"""
    send_weekday_timetable(
        context=context,
        user_id=update.effective_user.id,
        chat_id=update.effective_chat.id,
        weekday=consts.TODAY,
        language_code=update.effective_user.language_code,
    )


def send_weekday_timetable(context: CallbackContext, user_id, chat_id, weekday, language_code, footer=None):
    """Sends timetable for specified day"""

    # get user parameters
    attendance, utcoffset, notification_status = database.get_user_attrs(
        attrs_names=[consts.ATTENDANCE, consts.UTCOFFSET, consts.NOTIFICATION_STATUS],
        user_id=user_id,
    ).values()

    disable_notification = notification_status == consts.NOTIFICATION_DISABLED

    if weekday == consts.TODAY:
        # get current day
        weekday = tm.get_today_weekday(utcoffset)

    week_parity = tm.get_week_parity()

    tt = get_weekday_timetable(
        weekday=weekday,
        subject_names=database.get_user_subject_names(user_id),
        attendance=attendance,
        week_parity=week_parity,
        language_code=language_code,
        footer=footer,
    )

    cf.send_message(
        context=context,
        chat_id=chat_id,
        text=tt,
        reply_markup=keyboard.timetable_keyboard(
            weekday=weekday,
            attendance=attendance,
            week_parity=week_parity,
            language_code=language_code
        ),
        disable_notification=disable_notification,
    )


def get_subject_timetable(subject, subtype, attendance, language_code):
    """get a timetable for specified subject"""

    # dict of {weekday: {'online': tt1, 'offline': tt2}}
    tt = SERVER.get_subject_timetable(subject, subtype, attendance)

    # no timetable for this subject
    if not tt:
        return get_text('no_subject_timetable_header_text', language_code=language_code).text()

    weekday_list = []
    for weekday, dct in tt.items():
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


def get_weekday_timetable(weekday: str, subject_names, attendance, week_parity, language_code, footer=None) -> str:
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
        consts.FOOTER: footer or '',
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
    def inner(attendance, table):
        header = get_text(f'{attendance}_timetable_text', language_code).text() + '\n'
        tt.append(header + __make_timetable(table, template))

    tt = []
    if online:
        inner(consts.ATTENDANCE_ONLINE, online)
    if offline:
        inner(consts.ATTENDANCE_OFFLINE, offline)

    return '\n\n'.join(tt)


def __rm_blanks(subject_row):
    """in templates rms blank spaces: 'time | subject | | ' -> 'time | subject' """
    for a in range(len(subject_row) - 1, -1, -1):
        if not subject_row[a].isspace() and subject_row[a] != '|':
            return subject_row[:a + 1]


def __make_timetable(subjects_dict, template):
    """rm blank spaces, substitute args and glue everything"""
    return '\n'.join(list(map(lambda a: __rm_blanks(template % a), subjects_dict)))
