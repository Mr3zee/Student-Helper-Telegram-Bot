from typing import Dict


class Subject:

    def __init__(self, main: str, main_timetable_names: set = None, subtypes: Dict[str, set] = None,
                 subtypes_have_eq_tt_names: bool = True):
        if not subtypes:
            subtypes = set()
        if not main_timetable_names:
            main_timetable_names = set()
        self.__name = main
        self.__all_timetable_names = main_timetable_names
        if not subtypes_have_eq_tt_names:
            for subtype_tt in subtypes.values():
                self.__all_timetable_names = self.__all_timetable_names.union(subtype_tt)
        self.__subtypes_have_eq_tt_names = subtypes_have_eq_tt_names
        self.__subtypes = subtypes

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
}
