import sqlite3
from config.config import database_schedules_file

connection = sqlite3.connect(database_schedules_file)
cursor = connection.cursor()
cursor.execute('DROP TABLE IF EXISTS Schedules')
cursor.execute('CREATE TABLE Schedules '
               '(Id INTEGER PRIMARY KEY, '
               'Chat_id INTEGER, '
               'Scheduled_time INTEGER,'
               'Job_id INTEGER)')

try:
    cursor.execute('SELECT * FROM Schedules')
    print('Table Schedules successfully created')
except ConnectionError:
    print('Failed to create table Schedules')
