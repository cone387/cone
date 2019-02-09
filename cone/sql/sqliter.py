import sqlite3

class Sqliter(object):
    def __init__(self, db):
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self.cursor = self.conn.cursor()
        print(f"已连接到{db}")

    def close(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()
        print('已断开sqlite连接')