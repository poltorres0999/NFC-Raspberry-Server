import sqlite3


class DBHandler:

    def __init__(self, db_name):
        try:
            self.connection = sqlite3.connect(db_name, isolation_level=None)
            self.cursor = self.connection.cursor()
            print("Connected to database: {}".format(db_name))

        except sqlite3.Error as err:
            print("Unable to connect to db {}, error: {}".format(db_name, err))

    def check_rfid_tag(self, tag):
        tag = (tag,)
        self.cursor = self.connection.cursor()
        query = "SELECT * FROM tags WHERE Card=?"
        result = self.cursor.execute(query, tag).fetchone()
        self.cursor.close()
        return result

    def store_rfid_tag(self, tag):
        tag = (tag,)
        self.cursor = self.connection.cursor()
        query = "INSERT INTO tags VALUES (?)"
        result = self.cursor.execute(query, tag).fetchone()
        self.cursor.close()

    def delte_RFID_tag(self, tag):
        tag = (tag,)
        self.cursor = self.connection.cursor()
        query = "DELETE FROM tags WHERE Card=?"
        self.cursor.close()

    def check_table_exists(self, table_name):
        self.cursor = self.connection.cursor()
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.cursor.execute(query, (table_name,)).fetchone()
        self.cursor.close()
        return result

    def get_all_tags(self):
        self.cursor = self.connection.cursor()
        query = "SELECT * from tags"
        tags = self.cursor.execute(query).fetchall()
        self.cursor.close()
        return tags

    def get_all_master_keys(self):
        self.cursor = self.connection.cursor()
        query = "SELECT * from masterKey"
        m_keys = self.cursor.execute(query).fetchall()
        self.cursor.close()
        return m_keys

    def get_logs(self):
        self.cursor = self.connection.cursor()
        query = "SELECT * from log"
        logs = self.cursor.execute(query).fetchall()
        self.cursor.close()
        return logs

    def init_db(self):

        create_key = "CREATE TABLE IF NOT EXISTS tags (Card TEXT)"
        create_log = "CREATE TABLE IF NOT EXISTS log (ID INTEGER PRIMARY KEY, Card TEXT, Date TEXT,  authorized INTEGER DEFAULT 0)"
        create_master_key = "CREATE TABLE IF NOT EXISTS masterKey (Card TEXT)"

        if not self.check_table_exists("tags"):
            self.cursor = self.connection.cursor()
            tags = [("123789",), ("123789",), ("123789",)]
            self.cursor.execute(create_key)
            self.cursor.executemany('INSERT INTO tags VALUES (?)', tags)

        if not self.check_table_exists("log"):
            self.cursor = self.connection.cursor()
            logs = [("001", "123789", "2006-03-28", "1"),
                    ("002", "1456789", "2006-03-28", "0"),
                    ("003", "123459", "2006-03-28", "1")]
            self.cursor.execute(create_log)
            self.cursor.executemany('INSERT INTO log VALUES (?,?,?,?)', logs)

        if not self.check_table_exists("masterKey"):
            self.cursor = self.connection.cursor()
            master = ("123456M",)
            self.cursor.execute(create_master_key)
            self.cursor.execute('INSERT INTO masterKey VALUES (?)', master)

        self.connection.commit()
        self.cursor.close()







