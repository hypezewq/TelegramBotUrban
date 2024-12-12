import sqlite3


def initiate_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER NOT NULL,
                balance INTEGER NOT NULL DEFAULT 1000
            )
        ''')

    conn.commit()
    conn.close()


def get_all_products(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()

    conn.close()
    return products


def add_user(db_name, username, email, age, balance):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Users (username, email, age, balance)
        VALUES (?, ?, ?, ?)
    ''', (username, email, age, balance))

    conn.commit()
    conn.close()


def is_included(db_name, username):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT COUNT(*) FROM Users WHERE username = ?
    ''', (username,))
    count = cursor.fetchone()[0]

    conn.close()
    return count > 0
