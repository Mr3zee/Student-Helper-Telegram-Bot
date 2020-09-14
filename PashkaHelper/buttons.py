# weekdays buttons
MONDAY = 'monday_button'
TUESDAY = 'tuesday_button'
WEDNESDAY = 'wednesday_button'
THURSDAY = 'thursday_button'
FRIDAY = 'friday_button'
SATURDAY = 'saturday_button'

WEEKDAYS_SET = {MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY}

# parameters buttons
NAME = 'name_button'
EVERYDAY_MESSAGE = 'everyday_message_button'
ATTENDANCE = 'attendance_button'
COURSES = 'courses_button'
PARAMETERS_RETURN = 'return_par_button'
EXIT = 'exit_button'

MAIN_SET = {NAME, EVERYDAY_MESSAGE, COURSES, ATTENDANCE, PARAMETERS_RETURN}

# attendance buttons
ATTENDANCE_ONLINE = 'online_attendance_button'
ATTENDANCE_OFFLINE = 'offline_attendance_button'
ATTENDANCE_BOTH = 'both_attendance_button'

ATTENDANCE_SET = {ATTENDANCE_BOTH, ATTENDANCE_OFFLINE, ATTENDANCE_ONLINE}

# everyday message buttons
ALLOW_MESSAGE = 'allowed_message_button'
FORBID_MESSAGE = 'forbidden_message_button'
TZINFO = 'tz_info_button'
MESSAGE_TIME = 'message_time_button'

EVERYDAY_MESSAGE_SET = {ALLOW_MESSAGE, FORBID_MESSAGE, MESSAGE_TIME, TZINFO}

# courses buttons
OS_TYPE = 'os_type_button'
SP_TYPE = 'sp_type_button'
ENG_GROUP = 'eng_group_button'
HISTORY_GROUP = 'history_group_button'
COURSES_RETURN = 'return_courses_button'

COURSES_SET = {OS_TYPE, SP_TYPE, HISTORY_GROUP, ENG_GROUP, COURSES_RETURN}

# os buttons
OS_ADV = 'os_adv_button'
OS_LITE = 'os_lite_button'

OS_SET = {OS_ADV, OS_LITE}

# sp buttons
SP_KOTLIN = 'sp_kotlin_button'
SP_IOS = 'sp_ios_button'
SP_ANDROID = 'sp_android_button'
SP_WEB = 'sp_web_button'
SP_CPP = 'sp_cpp_button'

SP_SET = {SP_CPP, SP_IOS, SP_WEB, SP_KOTLIN, SP_ANDROID}

# eng buttons
ENG_C2_1 = 'eng_c21_button'
ENG_C2_2 = 'eng_c22_button'
ENG_C2_3 = 'eng_c23_button'

ENG_C1_1 = 'eng_c11_button'
ENG_C1_2 = 'eng_c12_button'

ENG_B2_1 = 'eng_b21_button'
ENG_B2_2 = 'eng_b22_button'
ENG_B2_3 = 'eng_b23_button'

ENG_B11_1 = 'eng_b111_button'
ENG_B11_2 = 'eng_b112_button'
ENG_B12_1 = 'eng_b121_button'
ENG_B12_2 = 'eng_b122_button'

ENG_NEXT = 'eng_next_button'
ENG_PREV = 'eng_prev_button'

ENG_SET = {ENG_C2_1, ENG_C2_3, ENG_C1_1, ENG_C1_2, ENG_B2_1, ENG_B2_2, ENG_B2_3, ENG_C2_2, ENG_B11_1, ENG_B11_2,
           ENG_B12_1, ENG_B12_2, ENG_NEXT, ENG_PREV}

# history buttons
HISTORY_INTERNATIONAL = 'history_international_button'
HISTORY_SCIENCE = 'history_science_button'
HISTORY_EU_PROBLEMS = 'history_eu_problems_button'
HISTORY_CULTURE = 'history_culture_button'
HISTORY_REFORMS = 'history_reforms_button'
HISTORY_STATEHOOD = 'history_statehood_button'

HISTORY_SET = {HISTORY_CULTURE, HISTORY_EU_PROBLEMS, HISTORY_INTERNATIONAL, HISTORY_REFORMS, HISTORY_SCIENCE,
               HISTORY_STATEHOOD}


def is_course_update(button):
    return button in HISTORY_SET or button in ENG_SET or button in OS_SET or button in SP_SET
