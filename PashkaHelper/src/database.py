import json

from telegram.utils.helpers import decode_conversations_from_json, encode_conversations_to_json

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

import src.subject as subject
from src.text import get_text
from src.app import app

from static import config, consts

# list of all columns
COLUMNS = [
    consts.USER_NICK,
    consts.CHAT_ID,
    consts.USERNAME,
    consts.ADMIN,
    consts.MUTED,
    consts.ATTENDANCE,
    consts.MAILING_STATUS,
    consts.NOTIFICATION_STATUS,
    consts.MAILING_TIME,
    consts.UTCOFFSET,
    consts.OS,
    consts.SP,
    consts.HISTORY,
    consts.ENG,
]

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
    Database to store all users and their parameters
     - user_id: user's telegram id
     - user_nick: user's telegram nick/tag
     - chat_id: current chat's id for user
     - admin: if user is an admin
     - muted: if user is not allowed to send reports
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
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_nick = db.Column(db.String(50), unique=True)
    chat_id = db.Column(db.Integer, unique=True)
    admin = db.Column(db.Boolean)
    muted = db.Column(db.Boolean)
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

    def __init__(self, user_id, user_nick, chat_id, admin=False, muted=False, username=consts.UNKNOWN,
                 attendance=consts.ATTENDANCE_BOTH, mailing_status=consts.MAILING_ALLOWED,
                 notification_status=consts.NOTIFICATION_ENABLED, mailing_time='7:30', utcoffset=3,
                 os=consts.ALL, sp=consts.ALL, history=consts.ALL, eng=consts.ALL):
        self.user_id = user_id
        self.user_nick = user_nick
        self.chat_id = chat_id
        self.admin = admin
        self.muted = muted
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
    if db.session.query(Users).filter(Users.user_id == user_id).count() == 0:
        new_user = Users(user_id=user_id, user_nick=user_nick, chat_id=chat_id)
        db.session.add(new_user)
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
        for user in db.session.query(Users).filter_by(mailing_status='allowed').all()
    }


def get_all_users():
    """get all users' ids and nicks"""
    return [(user.user_id, user.user_nick) for user in db.session.query(Users).all()]


def __get_user_row(user_id=None, user_nick=None, chat_id=None):
    """get user's row in the database by one of the parameters"""
    if user_id is None and user_nick is None and chat_id is None:
        raise ValueError('All fields cannot be None simultaneously')
    if user_id is not None:
        return db.session.query(Users).filter_by(user_id=user_id).first()
    elif user_nick is not None:
        return db.session.query(Users).filter_by(user_nick=user_nick).first()
    return db.session.query(Users).filter_by(chat_id=chat_id).first()


def get_user_parameters(user_id, language_code):
    """returns all user's parameters"""
    retval = {}
    values = get_user_attrs(COLUMNS, user_id)
    for attr_name, attr_value in values.items():
        # skip service parameters
        if attr_name in {consts.CHAT_ID, consts.USER_NICK, consts.MUTED, consts.ADMIN}:
            continue
        # attrs without modifications
        elif (attr_name == consts.USERNAME and attr_value) \
                or (attr_name == consts.MAILING_TIME):
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
    user = __get_user_row(user_id)
    retval = set()
    for sub in subject.SUBJECTS:
        retval = retval.union(subject.SUBJECTS[sub].get_all_timetable_names(
            getattr(user, sub)
            if sub in COLUMNS
            else sub
        ))
    return retval


def get_user_attrs(attrs_names: list, user_id: int = None, user_nick: str = None):
    """get all user attrs specified in attrs_names"""
    user = __get_user_row(user_id=user_id, user_nick=user_nick)
    retval = {}
    for attr in attrs_names:
        retval[attr] = (getattr(user, attr) if attr in COLUMNS else None)
    return retval


def get_user_attr(attr_name: str, user_id: int = None, user_nick: str = None):
    """get user attr by attr_name"""
    return get_user_attrs([attr_name], user_id=user_id, user_nick=user_nick).get(attr_name)


def gat_attr_column(name):
    """get attr value for all users"""
    return [getattr(user, name) for user in db.session.query(Users).all()]


def set_user_attrs(attrs: dict, user_id: int = None, user_nick: str = None, chat_id: int = None):
    """set user attrs passed to attrs dict"""
    user = __get_user_row(user_id=user_id, user_nick=user_nick, chat_id=chat_id)
    for attr_name, new_value in attrs.items():
        if attr_name not in COLUMNS:
            raise ValueError(f'Wrong attr name: {attr_name}')
        if attr_name in DOMAINS:
            if new_value in DOMAINS[attr_name]:
                setattr(user, attr_name, new_value)
            else:
                raise ValueError(f'forbidden value for {attr_name} attr: {new_value}')
        else:
            setattr(user, attr_name, new_value)

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
