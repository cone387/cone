from cone.spider import ConeSpider, BaseRecorder
from .items import DataSetItem, DataSetSql
from cone.sql import Sqliter
import os

class DataSetRecorder(BaseRecorder):
    model = DataSetItem
    server_db = ''
    this_db = ''
    this_db_descr = None
    def __init__(self):
        assert self.this_db_descr is not None, '数据库的描述不能为空'
        self.sql = DataSetSql(db=self.this_db, descr=self.this_db_descr)
        self.model.create_item(self.sql, self.model.table)
        server_sql = Sqliter(db=self.server_db)
        self.model.register(server_sql, self.sql)
        server_sql.close()
        assert self.model.is_registed, '模型未注册成功'
        super().__init__()
    
    def record(self, item):
        return self.model.save(self.sql, self.model.table, item)[0]

    def close(self):
        self.sql.close()


class DataSetSpider(ConeSpider):
    def init_recorder(self):
        for recorder in self.recorders:
            assert issubclass(recorder, DataSetRecorder), 'recorder must be subclass of %s'%DataSetRecorder.__name__
        super().init_recorder()
