import sqlite3


class SQLiteInsertError(Exception):
    def __init__(self, message):
        self.message = message
        super(SQLiteInsertError, self).__init__('{0}'.format(self.message))


class SQLInstance:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_all(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM Schedules').fetchall()

    def select_execution_times(self, starting_from=None):
        if starting_from:
            result = self.cursor.execute(
                'SELECT Scheduled_time FROM Schedules WHERE Scheduled_time > ?', (starting_from,)) \
                .fetchall()
            if len(result) > 0:
                return result
            else:
                return None
        else:
            result = self.cursor.execute('SELECT Scheduled_time FROM Schedules').fetchall()
            if len(result) > 0:
                return result
            else:
                return None

    def count_entries_for_id(self, chat_id):
        result = self.cursor.execute('SELECT Id FROM Schedules WHERE Chat_id=?', int(chat_id))
        return len(result.fetchall())

    def insert(self, chat_id, time, job_id):
        with self.connection:
            if self.cursor.execute('INSERT INTO Schedules (Chat_id, Scheduled_time, Job_id) values (?, ?, ?)',
                                   (int(chat_id), int(time), int(job_id))).rowcount < 0:
                raise SQLiteInsertError('Failed to insert data')
            return True

    def delete_old(self, time):
        with self.connection:
            result = self.cursor.execute('DELETE FROM Schedules WHERE Scheduled_time < ?', (time,))
            self.connection.commit()
        return result

    def execute(self, code):
        with self.connection:
            try:
                self.cursor.execute(code)
            except ConnectionError:
                pass

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()
