from .thread import BaseThread
from .queue import get_record_queue

class Recorder(BaseThread):
    def __init__(self, name='recorder'):
        self.success_num = 0
        self.error_num = 0
        self.queue = get_record_queue()
        super().__init__(name=name)

    @classmethod
    def from_spider(cls, spider):
        pass

    def get_success_num(self):
        return self.success_num

    def get_faild_num(self):
        return self.error_num

    def record(self, item):
        return True

    def reset_num(self):
        self.error_num = 0
        self.success_num = 0

    def execute(self, item):
        if self.record(item):
            self.success_num += 1
        else:
            self.error_num += 1

    def run(self):
        while self._run_flag:
            self._pause_flag.wait()
            item = self.queue.get()
            self.execute(item)
            self.queue.task_done()

    def stop(self):
        super().stop()
        self.close()

    def close(self):
        pass


