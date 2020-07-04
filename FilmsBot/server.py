import random
import pygsheets
import log


class Server:
    __users = {
        'Маша': '1234',
        'Саша': 'саша',
        'Петя': 'петя',
        'Вася': 'вася',
        'Роман': 'роман',
        'admin': 'admin'
    }
    __admins = {
        'admin': 'admin'
    }
    __films = ['Побег из Шоушенка', 'Крестный отец',
               'Крестный отец 2', 'Темный рыцарь',
               '12 разгневанных мужчин', 'Список Шиндлера',
               'Властелин колец: Возвращение Короля', 'Криминальное чтиво',
               'Хороший, плохой, злой', 'Властелин колец: Братство кольца',
               'Бойцовский клуб', 'Форрест Гамп',
               'Начало', 'Звёздные войны: Эпизод 5 – Империя наносит ответный удар',
               'Властелин колец: Две крепости', 'Матрица']

    def __init__(self):
        log.log('Starting Server...')

        self.__gc = pygsheets.authorize(service_file='service_account_credentials.json')
        self.__sh = self.__gc.open('FilmsSheet')
        self.__wkh = self.__sh.sheet1
        self.URL = self.__sh.url

        self.__authorized = {}
        self.__users_chat_id = {}
        random.seed()

        log.log_done()

    def get_users(self):
        return self.__users

    def get_authorized(self):
        return self.__authorized

    def get_admins(self):
        return self.__admins

    def logged_in(self, chat_id):
        return chat_id in self.__users_chat_id

    def get_username(self, chat_id):
        if chat_id in self.__users_chat_id:
            return self.__users_chat_id[chat_id]

    def random_film(self):
        index = random.randint(0, len(self.__films) - 1)
        return self.__films[index]

    def auth_user(self, data: dict, chat_id):
        if len(data) != 2:
            return False
        username = data['username']
        password = data['password']
        if username in self.__users and password == self.__users[username]:
            self.__authorized[username] = chat_id
            self.__users_chat_id[chat_id] = username
            return True

    def unauth_user(self, chat_id):
        self.__authorized.pop(self.__users_chat_id[chat_id])
        self.__users_chat_id.pop(chat_id)

    def user_authorized(self, username):
        return username in self.__authorized

    def add_films(self, films: list):
        pass

    def get_films(self, username):
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

    def auth_admin(self, data: list):
        if len(data) != 2:
            return False
        username = data[0]
        password = data[1]
        if username in self.__admins and password == self.__admins[username]:
            return True
        return False

    def add_user(self, data: list):
        if len(data) != 2:
            return False
        username = data[0]
        password = data[1]
        if username not in self.__users:
            self.__users[username] = password
            return True

    def change_user(self, data: dict, new_data):
        if len(data) != 2:
            return False
        username = data['username']
        field = data['field']
        if username not in self.__users:
            return False
        if field == 'username':
            if new_data in self.__users:
                return False
            password = self.__users[username]
            self.__users.pop(username)
            self.__users[new_data] = password
            self.__authorized.pop(username)
            self.__authorized[new_data] = password
            return True
        elif field == 'password':
            if self.__users[username] == new_data:
                return False
            self.__users[username] = new_data
            return True

    def valid_rm_user(self, username, admin_chat_id):
        return True

    def rm_user(self, data: list, username):
        if len(data) != 3:
            return False, None
        admin = data[0]
        admin_password = data[1]
        user_password = data[2]
        if admin_password == self.__admins[admin] and user_password == self.__users[username]:
            self.__users.pop(username)
            if username in self.__authorized:
                user_chat_id = self.__authorized[username]
                self.__users_chat_id.pop(user_chat_id)
                self.__authorized.pop(username)
                return True, user_chat_id
            return True, None

    def valid_disconnection(self, username):
        return username in self.__authorized and username not in self.__admins

    def disconnect_user(self, username):
        if self.valid_disconnection(username):
            chat_id = self.__authorized[username]
            self.__authorized.pop(username)
            self.__users_chat_id.pop(chat_id)
            return chat_id


SERVER = Server()
