import time
from queue import Queue


class Pool(object):
    def __init__(self, queue, thread, num=3, dones=set()):
        self.start_time = time.time()
        self._threads = []
        self.queue = queue
        self.dones = dones
        self.errors = set()
        self.init_pool(thread, num)

    def init_pool(self, thread, num):
        for i in range(num):
            d = thread(self.queue, self.dones, self.errors, name=f"{thread.__name__.lower()}_{i}")
            self._threads.append(d)

    def do(self, priority=100, **kwargs):
        self.queue.put((priority, kwargs))
    

    def get_threads(self):
        return self._threads

    def check_thread(self):
        for i in self._threads:
            if not i.isAlive():
                i.queue.unfinished_tasks -= 1

    def isAlive(self):
        for i in self._threads:
            if i.isAlive():
                return True
        return False

    def start(self):
        for thread in self._threads:
            thread.start()

    def pause(self):
        for thread in self._threads:
            thread.pause()

    def resume(self):
        for thread in self._threads:
            thread.resume()

    def stop(self):
        for thread in self._threads:
            thread.stop()
        self.after_stop()

    def after_stop(self):
        pass