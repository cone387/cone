import threading
import time


class BaseThread(threading.Thread):
    def __init__(self, queue, name='', daemon=True):
        """
            name: 线程名
            daemon = True
        """
        super().__init__(name=name, daemon=True)    # damen=True 即主线程结束，子线程结束
        self.name = name
        self.queue = queue
        self.start_time = time.time()
        self._run_flag = True  # 控制线程运行或停止
        self._pause_flag = threading.Event()    # 控制线程暂停或恢复
        self._pause_flag.set()
        

    def do(self, priority=100, **kwargs):
        self.queue.put((priority, kwargs))

    def pause(self):
        self._pause_flag.clear()

    def resume(self):
        self._pause_flag.set()

    def stop(self):
        self._run_flag = False

    def execute(self, **kwargs):
        raise NotImplemented

    def run(self):
        """
            不停的从queue取值,
            定义的queu必须传入两个参数
            _, kwargs = queue.get()
        """
        while self._run_flag:
            self._pause_flag.wait()
            _, kwargs = self.queue.get()
            self.execute(**kwargs)
            self.queue.task_done()


