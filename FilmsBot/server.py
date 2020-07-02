import random
import pygsheets

random.seed()

users = {'Марина': '1234', 'Саша': 'саша', 'Петя': 'петя', 'Вася': 'вася', 'Роман': 'роман', 'admin': 'admin'}
admins = {'admin': 'admin'}
films = ['Побег из Шоушенка', 'Крестный отец',
         'Крестный отец 2', 'Темный рыцарь',
         '12 разгневанных мужчин', 'Список Шиндлера',
         'Властелин колец: Возвращение Короля', 'Криминальное чтиво',
         'Хороший, плохой, злой', 'Властелин колец: Братство кольца',
         'Бойцовский клуб', 'Форрест Гамп',
         'Начало', 'Звёздные войны: Эпизод 5 – Империя наносит ответный удар',
         'Властелин колец: Две крепости', 'Матрица']

users_chat_id = {}

authorized = {}

client_info = {
    'service_account_credentials_file': 'service_account_credentials.json',
    'URL': None,
    'sheet_name': 'FilmsSheet',
}


def start():
    if client_info['service_account_credentials_file']:
        client = pygsheets.authorize(service_account_file=client_info['service_account_credentials_file'])
        sheet = client.open(client_info['sheet_name'])
        client_info['URL'] = sheet.url
        sheet.sheet1.update_value('A1', 'Started')


def get_users():
    return users


def get_authorized():
    return authorized


def get_admins():
    return admins


def check_auth(chat_id):
    return chat_id in users_chat_id


def logged_in(chat_id):
    return chat_id in users_chat_id


def get_username(chat_id):
    if chat_id in users_chat_id:
        return users_chat_id[chat_id]


def random_film():
    index = random.randint(0, len(films) - 1)
    return films[index]


def get_films_for_random():
    return films


def auth_user(data: dict, chat_id):
    if len(data) != 2:
        return False
    username = data['username']
    password = data['password']
    if username in users and password == users[username]:
        authorized[username] = chat_id
        users_chat_id[chat_id] = username
        return True


def unauth_user(chat_id):
    authorized.pop(users_chat_id[chat_id])
    users_chat_id.pop(chat_id)


def user_authorized(username):
    return username in authorized


def add_films(films: list):
    pass


def get_films(username):
    return {
        'ticked': [
            'Крепкий орешек',
            'Крепкий орешек 2',
            'Крепкий орешек 3',
        ],
        'unticked': [
            'Крепкий орешек 4',
            'Крепкий орешек 5',
        ],
    }


def get_link():
    return client_info['URL']


def auth_admin(data: list):
    if len(data) != 2:
        return False
    username = data[0]
    password = data[1]
    if username in admins and password == admins[username]:
        return True
    return False


def add_user(data: list):
    if len(data) != 2:
        return False
    username = data[0]
    password = data[1]
    if username not in users:
        users[username] = password
        return True


def change_user(data: dict, new_data):
    if len(data) != 2:
        return False
    username = data['username']
    field = data['field']
    if username not in users:
        return False
    if field == 'username':
        if new_data in users:
            return False
        password = users[username]
        users.pop(username)
        users[new_data] = password
        authorized.pop(username)
        authorized[new_data] = password
        return True
    elif field == 'password':
        if users[username] == new_data:
            return False
        users[username] = new_data
        return True


def valid_rm_user(username, admin_chat_id):
    return True


def rm_user(data: list, username):
    if len(data) != 3:
        return False, None
    admin = data[0]
    admin_password = data[1]
    user_password = data[2]
    if admin_password == admins[admin] and user_password == users[username]:
        users.pop(username)
        if username in authorized:
            user_chat_id = authorized[username]
            users_chat_id.pop(user_chat_id)
            authorized.pop(username)
            return True, user_chat_id
        return True, None


def valid_disconnection(username):
    return username in authorized and username not in admins


def disconnect_user(username):
    if valid_disconnection(username):
        chat_id = authorized[username]
        authorized.pop(username)
        users_chat_id.pop(chat_id)
        return chat_id
