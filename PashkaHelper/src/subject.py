from typing import Dict

from telegram import Update, error
from telegram.ext import CallbackContext, CommandHandler

from util import util
from util.log import log_function
from src.text import get_text
from src.timetable import get_subject_timetable
import src.database as database
import src.keyboard as keyboard

from static import consts


class Subject:
    """
    Class made to easily manipulate subject data
    Parameters
     - name: subject name
     - command: command for CommandHandler
     - main_timetable_names: set of general names in timetable,
       ones for all subtypes and general name (without subtype)
     - subtypes: dict of name - set of timetable name for all subtypes
     - subtypes_have_eq_tt_names: if all subtypes has equal timetable names
    """

    def __init__(self, name: str, command: str, main_timetable_names: set = None, subtypes: Dict[str, set] = None,
                 subtypes_have_eq_tt_names: bool = True):
        if not subtypes:
            subtypes = dict()
        if not main_timetable_names:
            main_timetable_names = set()
        self.__name = name
        self.__all_timetable_names = main_timetable_names
        if not subtypes_have_eq_tt_names:
            for subtype_tt in subtypes.values():
                self.__all_timetable_names = self.__all_timetable_names.union(subtype_tt)
        self.__subtypes_have_eq_tt_names = subtypes_have_eq_tt_names
        self.__subtypes = subtypes
        self.__command = command

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.__name)

    def __str__(self):
        return self.__name

    def get_name(self):
        return self.__name

    def get_command(self):
        return self.__command

    def get_subtypes(self):
        return self.__subtypes

    def get_subject_full_name(self, subtype):
        """Returns subject's full name in format name_subtype if subtype is valid else None"""
        return f'{self.__name}_{subtype}' if subtype in self.__subtypes else None

    def get_all_subject_full_names(self):
        """Return list of all full subject names in format name_subtype"""
        return [self.get_subject_full_name(subtype) for subtype in self.__subtypes]

    def get_all_timetable_names(self, subtype):
        """Returns all timetable names for the subtype of the subject"""
        if not self.__subtypes_have_eq_tt_names and subtype in self.__subtypes:
            return self.__subtypes[subtype]
        return self.__all_timetable_names


# dict of all subjects
SUBJECTS = {
    consts.ALGO: Subject(
        name=consts.ALGO,
        command='al',
        main_timetable_names={'АиСД (лк)', 'АиСД (пр)'},
    ),
    consts.DISCRA: Subject(
        name=consts.DISCRA,
        command='dm',
        main_timetable_names={'Дискретка (лк)', 'Дискретка (пр)'},
    ),
    consts.DUFFUR: Subject(
        name=consts.DUFFUR,
        command='df',
        main_timetable_names={'Диффуры (лк)', 'Диффуры (пр)'},
    ),
    consts.MATAN: Subject(
        name=consts.MATAN,
        command='ma',
        main_timetable_names={'МатАн (лк)', 'МатАн (пр)'},
    ),
    consts.BJD: Subject(
        name=consts.BJD,
        command='bj',
    ),
    consts.OS: Subject(
        name=consts.OS,
        command='os',
        subtypes={
            'adv': {'ОС-adv (лк)', 'ОС-adv (пр)'},
            'lite': {'OC (лк)'},
        }, subtypes_have_eq_tt_names=False),
    consts.SP: Subject(
        name=consts.SP,
        command='sp',
        subtypes={
            'kotlin': {'Kotlin (лк)', 'Kotlin (пр)'},
            'ios': {'Android / iOS'},
            'android': {'Android / iOS'},
            'web': {'СП - Web (лк)', 'СП - Web (пр)'},
            'cpp': {'C++ (лк)', 'C++ (пр)'},
        }, subtypes_have_eq_tt_names=False),
    consts.HISTORY: Subject(
        name=consts.HISTORY,
        command='hs',
        main_timetable_names={'История'},
        subtypes={
            'international': set(),
            'science': set(),
            'eu_problems': set(),
            'culture': set(),
            'reforms': set(),
            'statehood': set(),
        }),
    consts.ENG: Subject(
        name=consts.ENG,
        command='en',
        main_timetable_names={'Английский'},
        subtypes={
            'c2_1': set(), 'c2_2': set(), 'c2_3': set(), 'c1_1': set(),
            'c1_2': set(), 'b2_1': set(), 'b2_2': set(), 'b2_3': set(),
            'b11_1': set(), 'b11_2': set(), 'b12_1': set(), 'b12_2': set(),
        }),
    consts.PE: Subject(
        name=consts.PE,
        command='pe',
    ),
}


def get_subject_info(subject, user_id, page, language_code, request: dict = None):
    """
    Returns subject info and attendance as tuple
     - subject: name of the subject without subtype
     - user_id: id to get user parameters from database
     - page: main or timetable
     - request: dict with 2 values - attendance and subtype.
       By default user parameters are taken from database, but if the request has values, bot uses them
    """
    if request is None:
        request = {}
    # default parameters
    subtype, attendance = database.get_user_attrs([subject, consts.ATTENDANCE], user_id=user_id).values()

    # substitutes with request parameters if exists
    attendance = util.if_none(request.get(consts.ATTENDANCE), attendance)
    subtype = util.if_none(request.get(consts.SUBTYPE), subtype)

    # select page to return
    if page == consts.TIMETABLE_PAGE:
        timetable = get_subject_timetable(subject, subtype, attendance, language_code)
        return get_text('subject_timetable_text', language_code).text({
            consts.TIMETABLE: timetable,
        }), attendance
    elif page == consts.MAIN_PAGE:
        return get_text(f'{subject}_subject_text', language_code).text({
            consts.SUBTYPE: subtype,
            consts.ATTENDANCE: (attendance if attendance != consts.ATTENDANCE_BOTH else consts.ALL),
        }), attendance
    else:
        raise ValueError(f'Invalid subject page type: {page}')


def subject_handler(subject: str) -> CommandHandler:
    """Returns subject handler"""
    @log_function
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        user_id = update.effective_user.id

        # get subject info, page is main by default
        main_info, attendance = get_subject_info(
            subject=subject,
            user_id=user_id,
            page=consts.MAIN_PAGE,
            language_code=language_code,
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=main_info,
            reply_markup=keyboard.subject_keyboard(
                subject=subject,
                attendance=attendance,
                page=consts.MAIN_PAGE,
                language_code=language_code,
            ),
        )

    return CommandHandler(command=SUBJECTS[subject].get_command(), callback=inner)


@log_function
def subject_callback(update: Update, context: CallbackContext, data: list, language_code):
    """
    Callback function for subject keyboard
     - data: list
        - data[0] = 'subject'
        - data[1] = subject (name)
        - data[2] = attendance
        - data[3] = page
        - data[4] = 'button'
    """
    user_id = update.effective_user.id
    subject, attendance, page = data[1:-1]

    # get page text (attendance is redundant cause we received it as parameter in callback)
    text, _ = get_subject_info(
        subject=subject,
        user_id=user_id,
        page=page,
        language_code=language_code,
        request={
            consts.ATTENDANCE: attendance,
        }
    )
    # we need the try catch block here, because the python-telegram-bot lib throws a BadRequest error
    # when the page's content had not changed in the edit_message_text func
    # (also could be thrown when one button was double pressed very quickly)
    try:
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard.subject_keyboard(
                subject=subject,
                attendance=attendance,
                page=page,
                language_code=language_code,
            )
        )
    except error.BadRequest:
        pass
