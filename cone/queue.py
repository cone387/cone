import redis


class RedisQueue:
    def __init__(self, key, **redis_kwargs):
        # pool = redis.ConnectionPool(**redis_kwargs)
        # self.__db = redis.Redis(connection_pool=pool)
        self.__db = redis.Redis(**redis_kwargs)
        print('成功连接到redis')
        self.key = f'{key}'
        self.unfinished_tasks = 0

    def qsize(self):
        return self.__db.llen(self.key)

    def empty(self):
        return self.__db.llen(self.key) == 0

    def put(self, *item):
        self.__db.rpush(self.key, *item)
        self.unfinished_tasks += 1
    
    def get(self, timeout=None):
        item = self.__db.blpop(self.key, timeout=timeout)
        # return item.decode('utf-8')
        return item[1].decode('utf-8') if item else item

    def task_done(self):
        self.unfinished_tasks -= 1