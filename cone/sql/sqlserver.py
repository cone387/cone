import pyodbc
import sys

class SQLServer(object):
    cursor = None
    conn = None
    def __init__(self,host=None,db=None,user=None,pwd=None):
        self.host = host
        self.db = db
        self.user = user
        self.pwd = pwd
        self.login(host,db,user,pwd)
    
    def login(self,host,db,user,pwd):
        command = "DRIVER={};SERVER={};DATABASE={};UID={};PWD={}".format("SQL Server",host,db,user,pwd)
        # command = "DRIVER={};SERVER={};UID={};PWD={}".format("SQL Server",host,user,pwd)
        self.conn = pyodbc.connect(command)
        self.cursor = self.conn.cursor()
        print("已连接到SQLServer")

    def close(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()
        print("SQLServer连接已断开")
 
            
if __name__ == "__main__":
    sql = MySQLServer("47.98.222.66,50001","hds316158242_db","sa","Wc159357")
    # sql = MySQLServer("47.94.99.0,52387","Cone","cone","bzl3.1415926")
    