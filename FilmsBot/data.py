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


authorized = {}


def rm_from_auth(username):
    authorized.pop(username)


def user_authorized(username):
    return username in authorized


def add_to_auth(username, chat_id):
    authorized[username] = chat_id


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


def change_user(username, field, new_data):
    if new_data in users:
        return False
    users.remove(username)
    users.add(new_data)
    return True


def valid_rm_user(username, admin_chat_id):
    return username != users_chat_id[admin_chat_id]


def rm_user(username, admin_password, user_password):
    if admin_password == 'admin' and user_password == '1234':
        users.discard(username)
        if username in authorized:
            chat_id = authorized[username]
            if chat_id in users_chat_id:
                users_chat_id.pop(chat_id)
            authorized.pop(username)
        return True


def valid_change_user(username):
    return username not in authorized
