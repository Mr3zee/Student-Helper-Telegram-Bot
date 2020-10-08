import json

from telegram.utils.helpers import decode_conversations_from_json, encode_conversations_to_json

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

import src.subject as subject
from src.time_management import to_utc_converter
from src.text import get_text
from src.app import app

from static import config

ATTR_NAMES = [
    'user_nik',
    'chat_id',
    'username',
    'admin',
    'muted',
    'attendance',
    'mailing_status',
    'notification_status',
    'mailing_time',
    'utcoffset',
    'os',
    'sp',
    'history',
    'eng',
]

DOMAINS = {
    'attendance': {'both', 'online', 'offline'},
    'mailing_status': {'allowed', 'forbidden'},
}

for key, value in subject.subjects.items():
    domains = set(value.get_subtypes().keys())
    if domains is not None:
        DOMAINS[key] = domains
        DOMAINS[key].add('all')

if config.ENV == 'dev':
    app.config['SQLALCHEMY_DATABASE_URI'] = config.local_db_uri
elif config.ENV == 'prod':
    app.config['SQLALCHEMY_DATABASE_URI'] = config.production_db_url
else:
    raise ValueError('app running mode does not specified')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_nik = db.Column(db.String(50), unique=True)
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

    def __init__(self, user_id, user_nik, chat_id, admin=False, muted=False, username='unknown', attendance='both',
                 mailing_status='allowed', notification_status='enabled', mailing_time='7:30',
                 utcoffset=3, os='all', sp='all', history='all', eng='all'):
        self.user_id = user_id
        self.user_nik = user_nik
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


def add_user(user_id, user_nik, chat_id):
    if db.session.query(Users).filter(Users.user_id == user_id).count() == 0:
        new_user = Users(user_id=user_id, user_nik=user_nik, chat_id=chat_id)
        db.session.add(new_user)
        db.session.commit()


def update_user_info(user_id, user_nik, chat_id):
    if db.session.query(Users).filter_by(user_id=user_id).count() != 0:
        set_user_attrs(user_id=user_id, attrs={'user_nik': user_nik, 'chat_id': chat_id})


def has_user(user_nik):
    return db.session.query(Users).filter_by(user_nik=user_nik).count() != 0


def get_all_admins_chat_ids():
    return [user.chat_id for user in db.session.query(Users).filter_by(admin=True).all()]


def get_all_users():
    return [(user.user_id, user.user_nik) for user in db.session.query(Users).all()]


def __get_user_row(user_id=None, user_nik=None, chat_id=None):
    if user_id is None and user_nik is None and chat_id is None:
        raise ValueError('All fields cannot be None simultaneously')
    if user_id is not None:
        return db.session.query(Users).filter_by(user_id=user_id).first()
    elif user_nik is not None:
        return db.session.query(Users).filter_by(user_nik=user_nik).first()
    return db.session.query(Users).filter_by(chat_id=chat_id).first()


def get_user(user_id, language_code):
    retval = {}
    values = get_user_attrs(ATTR_NAMES, user_id)
    for attr_name, attr_value in values.items():
        if (attr_name == 'chat_id') or (attr_name == 'user_nik'):
            continue
        elif (attr_name == 'username' and attr_value) \
                or (attr_name == 'mailing_time'):
            retval[attr_name] = attr_value
            continue
        elif attr_name == 'utcoffset':
            retval[attr_name] = (str(attr_value) if attr_value < 0 else f'+{attr_value}')
            continue
        text = get_text(f'{f"{attr_name}_{attr_value}"}_user_data_text', language_code).text()
        if attr_name == 'eng' and attr_value != 'all':
            text = get_text('eng_std_user_data_text', language_code).text({'eng': text})
        retval[attr_name] = text
    return retval


def get_user_subject_names(user_id):
    user = __get_user_row(user_id)
    retval = set()
    for sub in subject.subjects:
        retval = retval.union(subject.subjects[sub].get_all_timetable_names((
            getattr(user, sub)
            if sub in ATTR_NAMES
            else sub
        )))
    return retval


def get_user_attrs(attrs_name: list, user_id: int = None, user_nik: str = None):
    user = __get_user_row(user_id=user_id, user_nik=user_nik)
    retval = {}
    for attr in attrs_name:
        retval[attr] = (getattr(user, attr) if attr in ATTR_NAMES else None)
    return retval


def get_user_attr(attr_name: str, user_id: int = None, user_nik: str = None):
    return get_user_attrs([attr_name], user_id=user_id, user_nik=user_nik).get(attr_name)


def gat_all_attrs(name):
    return [getattr(user, name) for user in db.session.query(Users).all()]


def set_user_attrs(attrs: dict, user_id: int = None, user_nik: str = None, chat_id: int = None):
    user = __get_user_row(user_id=user_id, user_nik=user_nik, chat_id=chat_id)
    for attr_name, new_value in attrs.items():
        if attr_name not in ATTR_NAMES:
            raise ValueError(f'Wrong attr name: {attr_name}')
        if attr_name in DOMAINS:
            if new_value in DOMAINS[attr_name]:
                setattr(user, attr_name, new_value)
            else:
                raise ValueError(f'forbidden value for {attr_name} attr: {new_value}')
        else:
            setattr(user, attr_name, new_value)

    db.session.commit()


def get_user_mailing_time_with_offset(user_id):
    mailing_time, utcoffset = get_user_attrs(['mailing_time', 'utcoffset'], user_id=user_id).values()
    return to_utc_converter(
        input_date=datetime.strptime(mailing_time, '%H:%M'),
        utcoffset=timedelta(hours=utcoffset),
    ).time()


def valid_time(new_time: str):
    try:
        datetime.strptime(new_time.strip(), '%H:%M')
        return True
    except ValueError:
        return False


def valid_utcoffset(new_tzinfo: str):
    try:
        return abs(int(new_tzinfo)) < 13
    except ValueError:
        return False


class Persistence(db.Model):
    __tablename__ = 'persistence'
    name = db.Column(db.String(50), primary_key=True)
    data = db.Column(db.JSON)

    def __init__(self, name, data):
        self.name = name
        self.data = data


def get_db_conversations_row(name):
    return db.session.query(Persistence).filter_by(name=name).first()


def get_conversations() -> dict:
    conversations = get_db_conversations_row('conversations').data
    if conversations is None:
        return {}
    return decode_conversations_from_json(json.dumps(conversations))


def update_conversations(conversations: dict):
    db_conversations = get_db_conversations_row('conversations')
    db_conversations.data = json.loads(encode_conversations_to_json(conversations))
    db.session.commit()


def load_jobs() -> dict:
    jobs = get_db_conversations_row('jobs').data
    if jobs is None:
        return {}
    return jobs


def save_jobs(jobs: dict):
    db_jobs = get_db_conversations_row('jobs')
    db_jobs.data = json.loads(json.dumps(jobs, default=str))
    db.session.commit()
