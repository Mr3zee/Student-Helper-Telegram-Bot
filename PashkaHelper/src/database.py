from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

from src.subject import subjects
from src.time_management import to_utc_converter
from src.message import get_text
from src.app import app

import config

ATTR_NAMES = [
    'username',
    'attendance',
    'mailing_status',
    'mailing_time',
    'utcoffset',
    'os',
    'sp',
    'history',
    'eng'
]

DOMAINS = {
    'attendance': {'both', 'online', 'offline'},
    'mailing_status': {'allowed', 'forbidden'},
}

for key, value in subjects.items():
    domains = set(value.get_subtypes().keys())
    if domains:
        DOMAINS[key] = domains


if config.ENV == 'development':
    app.config['SQLALCHEMY_DATABASE_URI'] = config.local_db_uri
elif config.ENV == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = config.production_db_url
else:
    raise ValueError('app running mode does not specified')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    attendance = db.Column(db.String(20))
    mailing_status = db.Column(db.String(20))
    mailing_time = db.Column(db.String(10))
    utcoffset = db.Column(db.Integer)
    os = db.Column(db.String(20))
    sp = db.Column(db.String(20))
    history = db.Column(db.String(20))
    eng = db.Column(db.String(20))

    def __init__(self, user_id, username='unknown', attendance='both', mailing_status='allowed', mailing_time='7:30',
                 utcoffset=3, os=None, sp=None, history=None, eng=None):
        self.user_id = user_id
        self.username = username
        self.attendance = attendance
        self.mailing_status = mailing_status
        self.mailing_time = mailing_time
        self.utcoffset = utcoffset
        self.os = os
        self.sp = sp
        self.history = history
        self.eng = eng


def add_user(user_id):
    if db.session.query(Users).filter(Users.user_id == user_id).count() == 0:
        new_user = Users(user_id)
        db.session.add(new_user)
        db.session.commit()


def __get_user_row(user_id):
    return Users.query.filter_by(user_id=user_id).first()


def get_user(user_id, language_code):
    retval = {}
    values = get_user_attrs(user_id, ATTR_NAMES)
    for attr_name, attr_value in values.items():
        if (attr_name == 'username' and attr_value) \
                or (attr_name == 'mailing_time') \
                or (attr_name == 'utcoffset'):
            retval[attr_name] = attr_value
            continue
        elif not attr_value:
            attr_value = 'all'
        text = get_text(f'{f"{attr_name}_{attr_value}"}_user_data_text', language_code)
        if attr_name == 'eng' and attr_value != 'all':
            text = get_text('eng_std_user_data_text', language_code).format(text)
        retval[attr_name] = text
    return retval


def get_user_subject_names(user_id):
    user = __get_user_row(user_id)
    retval = set()
    for subject in subjects:
        retval = retval.union(subjects[subject].get_all_timetable_names((
            getattr(user, subject)
            if subject in ATTR_NAMES
            else subject
        )))
    return retval


def get_user_attrs(user_id, attrs_name: list):
    user = __get_user_row(user_id)
    retval = {}
    for attr in attrs_name:
        retval[attr] = (getattr(user, attr) if attr in ATTR_NAMES else None)
    return retval


def get_user_attr(user_id, attr_name):
    return get_user_attrs(user_id, [attr_name]).get(attr_name)


def set_user_attr(user_id, attr_name, new_value):
    user = __get_user_row(user_id)
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
    mailing_time, utcoffset = get_user_attrs(user_id, ['mailing_time', 'utcoffset']).values()
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
