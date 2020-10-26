import json

from sqlalchemy import or_
from telegram.utils.helpers import decode_conversations_from_json, encode_conversations_to_json

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

import src.subject as subject
from src.text import get_text
from src.app import app

from static import config, consts

# list of all columns
PARAMETERS = {
    consts.USERNAME,
    consts.ATTENDANCE,
    consts.MAILING_STATUS,
    consts.NOTIFICATION_STATUS,
    consts.MAILING_TIME,
    consts.UTCOFFSET,
    consts.OS,
    consts.SP,
    consts.HISTORY,
    consts.ENG,
}

USER_INFO = {
    consts.CHAT_ID,
    consts.USER_NICK,
    consts.ADMIN,
    consts.MUTED,
}

# domains for attrs
DOMAINS = {
    consts.ATTENDANCE: {consts.ATTENDANCE_BOTH, consts.ATTENDANCE_ONLINE, consts.ATTENDANCE_OFFLINE},
    consts.MAILING_STATUS: {consts.MAILING_ALLOWED, consts.MAILING_FORBIDDEN},
}

# configuring domains for subjects
for key, value in subject.SUBJECTS.items():
    domains = set(value.get_subtypes().keys())
    if domains is not None:
        DOMAINS[key] = domains
        DOMAINS[key].add(consts.ALL)

# configuring database's uri
if config.ENV == consts.DEV:
    app.config['SQLALCHEMY_DATABASE_URI'] = config.local_db_uri
elif config.ENV == consts.PROD:
    app.config['SQLALCHEMY_DATABASE_URI'] = config.production_db_url
else:
    raise ValueError('app running mode does not specified')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Users(db.Model):
    """
    Database to store users' main info
     - user_id: user's telegram id
     - user_nick: user's telegram nick/tag
     - chat_id: current chat's id for user
     - admin: if user is an admin
     - muted: if user is not allowed to send reports
    """
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_nick = db.Column(db.String(50), unique=True)
    chat_id = db.Column(db.Integer, unique=True)
    admin = db.Column(db.Boolean)
    muted = db.Column(db.Boolean)

    def __init__(self, user_id, user_nick, chat_id, admin=False, muted=False):
        self.user_id = user_id
        self.user_nick = user_nick
        self.chat_id = chat_id
        self.admin = admin
        self.muted = muted


class UserParameters(db.Model):
    """
    Database to store users' parameters
     - user_id: user's telegram id
     - username: user's name for marking tasks in tables
     - attendance: user's attendance
     - mailing_status: if user wants to receive mailing
     - notification_status: if user wants to receive mailing silently
     - mailing_time: time in a day when user wants to receive mailing
     - utcoffset: user's timezone offset
     - os: os subtype
     - sp: sp subtype
     - history: history subtype
     - eng: english subtype
    """
    __tablename__ = 'user_parameters'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    attendance = db.Column(db.String(20))
    mailing_status = db.Column(db.String(20))
    notification_status = db.Column(db.String(20))
    mailing_time = db.Column(db.String(10))
    utcoffset = db.Column(db.Integer)
    os = db.Column(db.String(20))
    sp = db.Column(db.String(20))
    history = db.Column(db.String(20))
    eng = db.Column(db.String(20))

    def __init__(self, user_id, username=consts.UNKNOWN,
                 attendance=consts.ATTENDANCE_BOTH, mailing_status=consts.MAILING_ALLOWED,
                 notification_status=consts.NOTIFICATION_ENABLED, mailing_time='7:30', utcoffset=3,
                 os=consts.ALL, sp=consts.ALL, history=consts.ALL, eng=consts.ALL):
        self.user_id = user_id
        self.username = username
        self.attendance = attendance
        self.mailing_status = mailing_status
        self.notification_status = notification_status
        self.mailing_time = mailing_time
        self.utcoffset = utcoffset
        self.os = os
        self.sp = sp
        self.history = history
        self.eng = eng


def add_user(user_id, user_nick, chat_id) -> bool:
    """add new user to the database, returns True if user was added, else False"""
    if db.session.query(Users).filter(user_id == user_id).count() == 0:
        new_user = Users(user_id=user_id, user_nick=user_nick, chat_id=chat_id)
        new_parameters = UserParameters(user_id=user_id)
        db.session.add(new_user)
        db.session.add(new_parameters)
        db.session.commit()
        return True
    return False


def update_user_info(user_id, user_nick, chat_id):
    """updates user's info by id"""
    if db.session.query(Users).filter_by(user_id=user_id).count() != 0:
        set_user_attrs(user_id=user_id, attrs={consts.USER_NICK: user_nick, consts.CHAT_ID: chat_id})


def has_user(user_nick):
    """checks if there is specified user in the database"""
    return db.session.query(Users).filter_by(user_nick=user_nick).count() != 0


def get_all_admins_chat_ids():
    """Returns all admins' chats"""
    return [user.chat_id for user in db.session.query(Users).filter_by(admin=True).all()]


def get_jobs_info() -> dict:
    """load jobs from database"""
    return {
        user.user_id: [user.mailing_time, user.utcoffset, user.notification_status, user.chat_id]
        for user in db.session.query(UserParameters).filter_by(mailing_status='allowed').all()
    }


def get_all_users():
    """get all users' ids and nicks"""
    return [(user.user_id, user.user_nick) for user in db.session.query(Users).all()]


def check_unique_fields(user_id=None, user_nick=None, chat_id=None):
    if user_id is None and user_nick is None and chat_id is None:
        raise ValueError('All fields cannot be None simultaneously')


def __valid_attr(attr):
    return attr in PARAMETERS or attr in USER_INFO


def __get_user_parameters_row(user_id=None, user_nick=None, chat_id=None):
    """get user's row in the database by one of the parameters"""
    check_unique_fields(user_id, user_nick, chat_id)
    if user_id is None:
        user_id = db.session.query(Users).filter(
            Users.chat_id == chat_id or Users.user_nick == user_nick
        ).first().user_id
    return db.session.query(UserParameters).filter_by(user_id=user_id).first()


def __get_user_info_row(user_id=None, user_nick=None, chat_id=None):
    check_unique_fields(user_id, user_nick, chat_id)
    return db.session.query(Users).filter(
        or_(Users.user_id == user_id, Users.user_nick == user_nick, Users.chat_id == chat_id)
    ).first()


def get_user_parameters(user_id, language_code):
    """returns all user's parameters"""
    retval = {}
    values = get_user_attrs(PARAMETERS, user_id)
    for attr_name, attr_value in values.items():
        # attrs without modifications
        if (attr_name == consts.USERNAME and attr_value) or (attr_name == consts.MAILING_TIME):
            retval[attr_name] = attr_value
            continue
        # add sign to utcoffset
        elif attr_name == consts.UTCOFFSET:
            retval[attr_name] = (str(attr_value) if attr_value < 0 else f'+{attr_value}')
            continue
        # get readable values
        text = get_text(f'{attr_name}_{attr_value}_user_data_text', language_code).text()
        # attach group's number to general name
        if attr_name == consts.ENG and attr_value != consts.ALL:
            text = get_text('eng_std_user_data_text', language_code).text({consts.ENG: text})
        retval[attr_name] = text
    return retval


def get_user_subject_names(user_id):
    """
    get all user's subject
    returns set of subjects or subtypes if there are such
    """
    user = __get_user_parameters_row(user_id)
    retval = set()
    for sub in subject.SUBJECTS:
        retval = retval.union(subject.SUBJECTS[sub].get_all_timetable_names(
            getattr(user, sub)
            if sub in PARAMETERS
            else sub
        ))
    return retval


def get_user_attrs(attrs_names: set, user_id: int = None, user_nick: str = None) -> dict:
    """get all user attrs specified in attrs_names"""
    user = __get_user_info_row(user_id=user_id, user_nick=user_nick)
    user_parameters = __get_user_parameters_row(user_id=user.user_id)
    retval = {}
    for attr in attrs_names:
        if not __valid_attr(attr):
            retval[attr] = None
            continue
        retval[attr] = getattr((user_parameters if attr in PARAMETERS else user), attr)
    return retval


def get_user_attr(attr_name: str, user_id: int = None, user_nick: str = None):
    """get user attr by attr_name"""
    return get_user_attrs({attr_name}, user_id=user_id, user_nick=user_nick).get(attr_name)


def gat_attr_column(column) -> list:
    """get attr value for all users in parameters db"""
    if not __valid_attr(column):
        return []
    return [getattr(user, column) for user in db.session.query(
        UserParameters if column in PARAMETERS else Users
    ).all()]


def set_user_attrs(attrs: dict, user_id: int = None, user_nick: str = None, chat_id: int = None):
    """set user attrs passed to attrs dict"""
    user = __get_user_info_row(user_id=user_id, user_nick=user_nick, chat_id=chat_id)
    user_parameters = __get_user_parameters_row(user_id=user.user_id)
    for attr_name, new_value in attrs.items():
        if not __valid_attr(attr_name):
            raise ValueError(f'Wrong attr name: {attr_name}')
        if attr_name in USER_INFO:
            setattr(user, attr_name, new_value)
            continue
        if attr_name in DOMAINS:
            if new_value in DOMAINS[attr_name]:
                setattr(user_parameters, attr_name, new_value)
            else:
                raise ValueError(f'forbidden value for {attr_name} attr: {new_value}')
        else:
            setattr(user_parameters, attr_name, new_value)

    db.session.commit()


def valid_time(new_time: str):
    """validate mailing time"""
    try:
        datetime.strptime(new_time.strip(), '%H:%M')
        return True
    except ValueError:
        return False


def valid_utcoffset(new_tzinfo: str):
    """validate utcoffset format"""
    try:
        return abs(int(new_tzinfo)) < 13
    except ValueError:
        return False


class Persistence(db.Model):
    """Database for saving bot's states"""

    __tablename__ = 'persistence'
    name = db.Column(db.String(50), primary_key=True)
    data = db.Column(db.JSON)

    def __init__(self, name, data):
        self.name = name
        self.data = data


def get_persistence_row(name):
    """get specified persistence database row"""
    return db.session.query(Persistence).filter_by(name=name).first()


def get_conversations() -> dict:
    """load conversations from database"""
    conversations = get_persistence_row(name=consts.CONVERSATIONS).data
    if conversations is None:
        return {}
    return decode_conversations_from_json(json.dumps(conversations))


def update_conversations(conversations: dict):
    """save conversations to database"""
    db_conversations = get_persistence_row(name=consts.CONVERSATIONS)
    db_conversations.data = json.loads(encode_conversations_to_json(conversations))
    db.session.commit()
