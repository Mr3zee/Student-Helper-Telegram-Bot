users = {'Маша', 'Саша', 'Петя', 'Вася', 'Роман'}
URL = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'


def get_users():
    return users


users_chat_id = {}


def logged_in(chat_id):
    return chat_id in users_chat_id


def get_username(chat_id):
    return users_chat_id[chat_id]


def rm_chat_id(chat_id):
    users_chat_id.pop(chat_id)


def add_user_chat_id(chat_id, name):
    users_chat_id[chat_id] = name


authorized = set()


def rm_from_auth(username):
    authorized.discard(username)


def user_authorized(username):
    return username in authorized


def add_to_auth(username):
    authorized.add(username)


def add_films(films: list):
    return None


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
    return URL


def auth_admin(data: list):
    if len(data) < 2:
        return False
    username = data[0]
    password = data[1]
    if username == 'admin' and password == 'admin':
        return True
    return False


def add_user(username, password):
    if username == 'user' and password == '1234' and username not in users:
        users.add(username)
        return True
