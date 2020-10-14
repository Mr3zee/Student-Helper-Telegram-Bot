from typing import Dict

from telegram import Update, error
from telegram.ext import CallbackContext, CommandHandler

from util import util
from src.log import log_function
from src.text import get_text
from src.timetable import get_subject_timetable
import src.database as database
import src.keyboard as keyboard


class Subject:

    def __init__(self, main: str, main_timetable_names: set = None, subtypes: Dict[str, set] = None,
                 subtypes_have_eq_tt_names: bool = True, teachers: set = None):
        if not subtypes:
            subtypes = dict()
        if not main_timetable_names:
            main_timetable_names = set()
        self.__name = main
        self.__all_timetable_names = main_timetable_names
        if not subtypes_have_eq_tt_names:
            for subtype_tt in subtypes.values():
                self.__all_timetable_names = self.__all_timetable_names.union(subtype_tt)
        self.__subtypes_have_eq_tt_names = subtypes_have_eq_tt_names
        self.__subtypes = subtypes
        self.__teachers = teachers

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.__name)

    def __str__(self):
        return self.__name

    def get_name(self):
        return self.__name

    def get_subtypes(self):
        return self.__subtypes

    def get_subtype_full_name(self, subtype):
        return f'{self.__name}_{subtype}' if subtype in self.__subtypes else None

    def get_subtypes_full_names(self):
        return [self.get_subtype_full_name(subtype) for subtype in self.__subtypes]

    def get_all_timetable_names(self, subtype):
        if not self.__subtypes_have_eq_tt_names and subtype in self.__subtypes:
            return self.__subtypes[subtype]
        return self.__all_timetable_names


subjects = {
    'algo': Subject(
        main='algo',
        main_timetable_names={'АиСД (лк)', 'АиСД (пр)'},
    ),
    'discra': Subject(
        main='discra',
        main_timetable_names={'Дискретка (лк)', 'Дискретка (пр)'},
    ),
    'diffur': Subject(
        main='diffur',
        main_timetable_names={'Диффуры (лк)', 'Диффуры (пр)'},
    ),
    'matan': Subject(
        main='matan',
        main_timetable_names={'МатАн (лк)', 'МатАн (пр)'},
    ),
    'bjd': Subject(
        main='bjd',
    ),
    'os': Subject(
        main='os',
        subtypes={
            'adv': {'ОС-adv (лк)', 'ОС-adv (пр)'},
            'lite': {'OC (лк)'},
        }, subtypes_have_eq_tt_names=False),
    'sp': Subject(
        main='sp',
        subtypes={
            'kotlin': {'Kotlin (лк)', 'Kotlin (пр)'},
            'ios': {'Android / iOS'},
            'android': {'Android / iOS'},
            'web': {'СП - Web (лк)', 'СП - Web (пр)'},
            'cpp': {'C++ (лк)', 'C++ (пр)'},
        }, subtypes_have_eq_tt_names=False),
    'history': Subject(
        main='history',
        main_timetable_names={'История'},
        subtypes={
            'international': set(),
            'science': set(),
            'eu_problems': set(),
            'culture': set(),
            'reforms': set(),
            'statehood': set(),
        }),
    'eng': Subject(
        main='eng',
        main_timetable_names={'Английский'},
        subtypes={
            'c2_1': set(), 'c2_2': set(), 'c2_3': set(), 'c1_1': set(),
            'c1_2': set(), 'b2_1': set(), 'b2_2': set(), 'b2_3': set(),
            'b11_1': set(), 'b11_2': set(), 'b12_1': set(), 'b12_2': set(),
        }),
    'pe': Subject(
        main='pe',
    ),
}


def get_subject_info(sub_name, user_id, page, language_code, request: dict = None):
    if request is None:
        request = {}
    subtype, attendance = database.get_user_attrs([sub_name, 'attendance'], user_id=user_id).values()
    attendance = util.if_none(request.get('attendance'), attendance)
    subtype = util.if_none(request.get('subtype'), subtype)
    if page == 'timetable':
        timetable = get_subject_timetable(sub_name, subtype, attendance, language_code)
        return get_text('subject_timetable_text', language_code).text({
            'timetable': timetable,
        }), attendance
    elif page == 'main':
        return get_text(f'{sub_name}_subject_text', language_code).text({
            'course': subtype,
            'attendance': attendance,
        }), attendance
    else:
        raise ValueError(f'Invalid subject page type: {page}')


def subject_handler(sub_name):
    @log_function
    def inner(update: Update, context: CallbackContext):
        language_code = update.effective_user.language_code
        user_id = update.effective_user.id

        main_info, attendance = get_subject_info(
            sub_name=sub_name,
            user_id=user_id,
            page='main',
            language_code=language_code,
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=main_info,
            reply_markup=keyboard.subject_keyboard(
                sub_name=sub_name,
                attendance=attendance,
                page='main',
                language_code=language_code,
            ),
        )

    return CommandHandler(command=sub_name, callback=inner)


@log_function
def subject_callback(update: Update, context: CallbackContext, data: list, language_code):
    user_id = update.effective_user.id
    sub_name, attendance, page = data[1:-1]
    text, _ = get_subject_info(
        sub_name=sub_name,
        user_id=user_id,
        page=page,
        language_code=language_code,
        request={
            'attendance': attendance,
        }
    )
    try:
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard.subject_keyboard(
                sub_name=sub_name,
                attendance=attendance,
                page=page,
                language_code=language_code,
            )
        )
    except error.BadRequest:
        pass
