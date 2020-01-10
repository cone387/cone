import redis
import random, json


class ProxyHelper(object):
    def __init__(self, key='proxy:http', host='47.94.99.0', online=False, **kwargs):
        """
            online = True, 则每次随机ip都从redis中取
            False 则连接一次redis, 取出当前所有代理,然后本地随机
        """
        self.redis_client = redis.Redis(host=host, **kwargs)
        self.key = key
        if online:
            self.random = self.random_online
        else:
            self.proxies = self.redis_client.lrange(key, 0, self.redis_client.llen(key)-1)
            self.random = self.random_offline


    def random_online(self):
        llen = self.redis_client.llen(self.key)
        number = random.choice(range(llen))
        proxy = self.redis_client.lrange(self.key, number, number)[0]
        return json.loads(proxy.decode().replace("'", '"'))

    def random_offline(self):
        proxy = random.choice(self.proxies)
        return json.loads(proxy.decode().replace("'", '"'))

    def order_one(self):
        return


if __name__ == '__main__':
    helper = ProxyHelper(key='proxy:valid', host='47.94.99.0', online=True)
    print(helper.random())