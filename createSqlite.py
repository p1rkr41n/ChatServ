import sqlite3
def createSqlChat():
    connection = sqlite3.connect('./chat.sqlite')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS "Cookies" (
        "Cookie"	TEXT,
        "User"	TEXT,
        "Last_acc"	NUMERIC,
        PRIMARY KEY("Cookie")
    )''')
    cursor.execute( '''CREATE TABLE IF NOT EXISTS "Msgs" (
        "Sender"	TEXT,
        "Receiver"	TEXT,
        "Timestamp"	NUMERIC,
        "Read"	NUMERIC,
        PRIMARY KEY("Sender","Receiver","Timestamp")
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS "Users" (
        "User"	TEXT NOT NULL,
        "Passwd"	TEXT,
        "Status"	NUMERIC,
        PRIMARY KEY("User")
    )''')
    connection.commit()
    connection.close()
# createChat()