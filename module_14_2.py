import sqlite3

connection = sqlite3.connect("not_telegram.db")
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users(
id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
email TEXT NOT NULL,
age INTEGER,
balance INTEGER NOT NULL
)
''')

cursor.execute("DELETE FROM Users WHERE id = 6")
cursor.execute("SELECT COUNT(*) FROM Users")
total = cursor.fetchone()[0]
cursor.execute("SELECT SUM(balance) FROM Users")
total_balances = cursor.fetchone()[0]
print(total_balances / total)
connection.close()
