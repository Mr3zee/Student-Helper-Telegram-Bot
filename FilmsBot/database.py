import sqlite3

__connection = None


def create_connection():
    global __connection
    if not __connection:
        __connection = sqlite3.connect('FilmsBotBase.db')
    return __connection


def init(force=False):
    connection = create_connection()
    cur = connection.cursor()

    if force:
        cur.execute('DROP TABLE IF EXISTS users')

    cur.execute('''
                
    ''')

    connection.commit()
