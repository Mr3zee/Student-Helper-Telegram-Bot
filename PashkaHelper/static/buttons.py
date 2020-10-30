# weekdays buttons
WEEKDAY_BUTTON = 'timetable_%(weekday)s_button'
TIMETABLE_BUTTON = 'timetable_%(attendance)s_%(week_parity)s_%(weekday)s_button'

# parameters buttons
NAME = 'name_button'
MAILING = 'mailing_parameters_button'
ATTENDANCE = 'attendance_button'
COURSES = 'courses_parameters_button'
PARAMETERS_RETURN = 'return_parameters_button'
EXIT_PARAMETERS = 'exit_parameters_button'

MAIN_SET = {NAME, MAILING, COURSES, ATTENDANCE, PARAMETERS_RETURN}

# attendance buttons
ATTENDANCE_ONLINE = 'online_attendance_button'
ATTENDANCE_OFFLINE = 'offline_attendance_button'
ATTENDANCE_BOTH = 'both_attendance_button'

ATTENDANCE_SET = {ATTENDANCE_BOTH, ATTENDANCE_OFFLINE, ATTENDANCE_ONLINE}

# everyday message buttons
ALLOW_MAILING = 'allowed_mailing_button'
FORBID_MAILING = 'forbidden_mailing_button'
ENABLE_MAILING_NOTIFICATIONS = 'enabled_notification_mailing_button'
DISABLE_MAILING_NOTIFICATIONS = 'disabled_notification_mailing_button'
TZINFO = 'tz_info_button'
MESSAGE_TIME = 'message_time_button'

MAILING_SET = {ALLOW_MAILING, FORBID_MAILING, ENABLE_MAILING_NOTIFICATIONS, DISABLE_MAILING_NOTIFICATIONS,
               MESSAGE_TIME, TZINFO}

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
OS_ALL = 'os_all_button'

OS_SET = {OS_ADV, OS_LITE, OS_ALL}

# sp buttons
SP_KOTLIN = 'sp_kotlin_button'
SP_IOS = 'sp_ios_button'
SP_ANDROID = 'sp_android_button'
SP_WEB = 'sp_web_button'
SP_CPP = 'sp_cpp_button'
SP_ALL = 'sp_all_button'

SP_SET = {SP_CPP, SP_IOS, SP_WEB, SP_KOTLIN, SP_ANDROID, SP_ALL}

# eng buttons
ENG_C2_1 = 'eng_c2_1_button'
ENG_C2_2 = 'eng_c2_2_button'
ENG_C2_3 = 'eng_c2_3_button'

ENG_C1_1 = 'eng_c1_1_button'
ENG_C1_2 = 'eng_c1_2_button'

ENG_B2_1 = 'eng_b2_1_button'
ENG_B2_2 = 'eng_b2_2_button'
ENG_B2_3 = 'eng_b2_3_button'

ENG_B11_1 = 'eng_b11_1_button'
ENG_B11_2 = 'eng_b11_2_button'
ENG_B12_1 = 'eng_b12_1_button'
ENG_B12_2 = 'eng_b12_2_button'

ENG_ALL = 'eng_all_button'
ENG_NEXT = 'eng_next_button'
ENG_PREV = 'eng_prev_button'

ENG_SET = {ENG_C2_1, ENG_C2_3, ENG_C1_1, ENG_C1_2, ENG_B2_1, ENG_B2_2, ENG_B2_3, ENG_C2_2, ENG_B11_1, ENG_B11_2,
           ENG_B12_1, ENG_B12_2, ENG_ALL, ENG_NEXT, ENG_PREV}

# history buttons
HISTORY_INTERNATIONAL = 'history_international_button'
HISTORY_SCIENCE = 'history_science_button'
HISTORY_EU_PROBLEMS = 'history_eu_problems_button'
HISTORY_CULTURE = 'history_culture_button'
HISTORY_REFORMS = 'history_reforms_button'
HISTORY_STATEHOOD = 'history_statehood_button'
HISTORY_ALL = 'history_all_button'

HISTORY_SET = {HISTORY_CULTURE, HISTORY_EU_PROBLEMS, HISTORY_INTERNATIONAL, HISTORY_REFORMS, HISTORY_SCIENCE,
               HISTORY_STATEHOOD, HISTORY_ALL}


def is_course_update(button):
    return button in HISTORY_SET or button in ENG_SET or button in OS_SET or button in SP_SET


# SUBJECTS change page
SUBJECT = 'subject_%(subject)s_%(attendance)s_%(page)s_button'

# HELP change page
HELP_MAIN = 'help_main_button'
HELP_ADDITIONAL = 'help_additional_button'

# other
CANCEL = 'cancel_button'
CANCEL_CALLBACK = 'cancel_%(data)s_button'

# admin ls button
ADMIN_LS = 'admin_ls_%(page_number)d_button'
NEXT_PAGE = 'admin_ls_next_button'
PREV_PAGE = 'admin_ls_prev_button'
UPDATE_PAGE = 'admin_ls_update_button'
