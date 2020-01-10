import time
from .thread import BaseThread
from queue import Queue

class BaseRecorder(object):
    def __init__(self, name=None):
        self.success_num = 0
        self.error_num = 0
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name
    
    @classmethod
    def from_spider(cls, spider):
        pass

    def record(self, item):
        pass

    def close(self):
        pass


class SqlRecorder(BaseRecorder):
    sql = None
    model = None
    table = None
    def __init__(self, name=None):
        super().__init__()
        if SqlRecorder.table is None:
            SqlRecorder.table = self.model.__name__
        self.model.create_item(self.sql, self.table)

    def record(self, item):
        r = self.model.save(self.sql, self.table, item)
        if not r[0]:
            print(r[1])
        return r[0]

    def close(self):
        self.sql.close()



class Recorder(BaseThread):
    def __init__(self, queue=Queue(), name='recorder'):
        self.recorders = []
        super().__init__(queue, name=name)

    def add_recorder(self, recorder):
        self.recorders.append(recorder)

    def get_success_num(self):
        return self.recorders[0].success_num

    def get_faild_num(self):
        return self.recorders[0].error_num

    def reset_num(self):
        self.recorders[0].success_num = 0
        self.recorders[0].error_num = 0

    def get_recorder_info(self):
        info = {}
        for recorder in self.recorders:
            info[recorder.name] = dict(success_num=recorder.success_num, error_num=recorder.error_num)
        return info

    def execute(self, item='', record=None):
        if record:
            if record(item):
                self.recorders[0].success_num += 1
            else:
                self.recorders[0].error_num += 1
        else:
            for recorder in self.recorders:
                if recorder.record(item):
                    recorder.success_num += 1
                else:
                    recorder.error_num += 1

    def stop(self):
        for recorder in self.recorders:
            recorder.close()
        super().stop()


