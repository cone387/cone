import pymysql


class MySql(object):
    def __init__(self, host=None,db=None,user=None,pwd=None, port=0):
        self.host = host
        self.db = db
        self.user = user
        self.pwd = pwd
        self.login(host, db, user, pwd, port)
    
    def login(self, host,db, user, pwd, port):
        self.conn = pymysql.connect(host, user, pwd, port=port, charset='UTF8MB4')
        self.cursor = self.conn.cursor()
        cmd = f'create database if not exists {db}'
        self.cursor.execute(cmd)
        self.cursor.execute(f'use {db}')
        # self.conn.commit()
        print("已连接到MySql")

    def close(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()
        print("MySql连接已断开")



def test():
    mysql = MySql('47.94.99.0', 'cone', 'cone', '3.1415926')
    mysql.close()
        
if __name__ == '__main__':
    test()
 