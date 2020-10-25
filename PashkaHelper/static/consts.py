# subject consts
ALGO = 'algo'
DISCRA = 'discra'
DUFFUR = 'diffur'
MATAN = 'matan'
PE = 'pe'
SP = 'sp'
OS = 'os'
BJD = 'bjd'
HISTORY = 'history'
ENG = 'eng'
SUBTYPE = 'subtype'

# pages consts
MAIN_PAGE = 'main'
TIMETABLE_PAGE = 'timetable'
ADDITIONAL_PAGE = 'additional'

# User attributes
USER_ID = 'user_id'
USER_NICK = 'user_nick'
USERNAME = 'username'
CHAT_ID = 'chat_id'
ADMIN = 'admin'
MUTED = 'muted'
UTCOFFSET = 'utcoffset'

# Persistence attributes
CONVERSATIONS = 'conversations'
JOBS = 'jobs'

# timetable consts
WEEKDAY = 'weekday'
MONDAY = 'monday'
TUESDAY = 'tuesday'
WEDNESDAY = 'wednesday'
THURSDAY = 'thursday'
FRIDAY = 'friday'
SATURDAY = 'saturday'
SUNDAY = 'sunday'
TODAY = 'today'

# handler types
COMMAND = 'command'
MESSAGE = 'message'

# ConversationHandlers' states
MAIN_STATE = 'main_state'
PARAMETERS_STATE = 'parameters_state'
ADMIN_STATE = 'admin_state'
REPORT_STATE = 'report_state'
REPORT_MESSAGE_STATE = 'report_message_state'
ADMIN_NOTIFY_STATE = 'admin_notify_state'
PARAMETERS_MAIN_STATE = 'parameters_main_state'
PARAMETERS_TIME_STATE = 'parameters_time_state'
PARAMETERS_TZINFO_STATE = 'parameters_tzinfo_state'
PARAMETERS_NAME_STATE = 'parameters_name_state'

# attendance consts
ATTENDANCE = 'attendance'
ATTENDANCE_BOTH = 'both'
ATTENDANCE_ONLINE = 'online'
ATTENDANCE_OFFLINE = 'offline'

# week parity consts
WEEK_PARITY = 'week_parity'
WEEK_ODD = 'odd'
WEEK_EVEN = 'even'
WEEK_BOTH = 'both'

# mailing consts
MAILING_TIME = 'mailing_time'
MAILING_STATUS = 'mailing_status'
MAILING_ALLOWED = 'allowed'
MAILING_FORBIDDEN = 'forbidden'
NOTIFICATION_STATUS = 'notification_status'
NOTIFICATION_ENABLED = 'enabled'
NOTIFICATION_DISABLED = 'disabled'

# Jobs consts
MAILING_JOB = 'mailing_job'
CALLBACK_JOB = 'callback'
INTERVAL_JOB = 'interval'
REPEAT_JOB = 'repeat'
CONTEXT_JOB = 'context'
DAYS_JOB = 'days'
NAME_JOB = 'name'
TZINFO_JOB = 'tzinfo'

JOB_DATA = [CALLBACK_JOB, INTERVAL_JOB, REPEAT_JOB, CONTEXT_JOB, DAYS_JOB, NAME_JOB, TZINFO_JOB]
JOB_STATE = ['_remove', '_enabled']


# other
DOC_COMMANDS = {'doc', 'help', 'parameters', 'today', 'timetable', 'report', 'admin'}
ALL = 'all'
DEV = 'dev'
PROD = 'prod'
UNKNOWN = 'unknown'
TIMETABLE = 'timetable'
SUBJECT = 'subject'
PAGE = 'page'
TEXT = 'text'
COURSES = 'courses'
ENTER_NAME = 'enter_name'
ENTER_TIME = 'enter_time'
ENTER_TZINFO = 'enter_tzinfo'
HELP = 'help'
