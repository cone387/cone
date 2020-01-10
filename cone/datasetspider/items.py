from cone.spider.item import OriginSqlItem, Field
from cone.sql import Sqliter
from cone.tools import get_md5
import json
import os


class RegisterErrorException(BaseException):
    """注册失败"""


class ServerSqlItem(OriginSqlItem): # 服务端数据库，用于记录当前有多少数据集可以使用
    table = 'datasets'
    db = 'server.db'
    db_id = Field('nchar(32) primary key') # 数据库路径的md5值
    db_descr = Field('nvarchar(100)')   # 数据库的描述
    db_file = Field('nvarchar(200)')    # 数据库所在路径


class DataSetSql(Sqliter):
    def __init__(self, descr=None, db=None):
        super().__init__(db=db)
        self.descr = descr
        self.db_file = os.path.abspath(db)
        
    @property
    def item(self):
        return {'db_file': self.db_file, 'db_descr': self.descr, 'db_id': get_md5(self.db)}
    

class DescrItem(OriginSqlItem):
    # 描述表的信息与字段信息
    table = 'description'
    table_name = Field('nvarchar(50)', descr="名字")
    table_descr = Field('nvarchar(100)', descr='你好')
    column_descr = Field('text', descr='猎民')

"""
    成为数据集的流程：
    每一个数据集的数据库里都得有一个description表,即DescrItem模型，
    字段有三个：数据集的表名，数据集表的描述，数据集字段的描述：格式为json{字段名：字段名说明}
"""

class DataSetItem(OriginSqlItem):
    descr_item = DescrItem
    table = None
    table_descr = ''
    is_registed = False

    @classmethod
    def register(cls, server_sql:Sqliter, this_sql: DataSetSql):
        descr_item = getattr(DataSetItem, 'descr_item', DescrItem)
        # 一下两个保存应该保证其操作的原子性，目前有待解决
        assert cls.table_descr, '表的描述不能为空'
        assert cls.table, '表名不能为空'
        descr_item.create_item(this_sql)
        r = descr_item.save(this_sql, descr_item.table, cls.generate_descr())
        if not r[0]:
            raise RegisterErrorException(r[1])
        r = ServerSqlItem.save(server_sql, ServerSqlItem.table, this_sql.item)
        if not r[0]:
            raise RegisterErrorException(r[1])
        cls.is_registed = True
        print("dataset: %s->%s 注册成功"%(cls.table, cls.table_descr))

    @classmethod
    def generate_descr(cls):
        column_descr = {k: v.descr for k, v in cls.__dict__.items() if isinstance(v, Field) and v.descr is not None}
        assert column_descr, '字段描述不能都为空'
        return {
            'table_descr': cls.table_descr,
            'table_name': cls.table,
            'column_descr': json.dumps(column_descr)
        }