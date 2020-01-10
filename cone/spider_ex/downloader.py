
from .queue import get_dowonload_queue, get_record_queue
from .thread import BaseThread
from .response import Response
from .log import spider_logger as logger
from .request import Request, CrawlerRequest
import requests
import types
from requests.packages.urllib3 import exceptions
requests.packages.urllib3.disable_warnings(exceptions.InsecureRequestWarning)
from requests.exceptions import Timeout, ProxyError


class HttpDownloader(BaseThread):
    
    def __init__(self, dones=set(), name='downloader'):
        super().__init__(name)
        self.dones = dones
        self._request_total = 0
        self._request_error = 0
        self._queue = get_dowonload_queue()
        self._item_queue = get_record_queue()

    @property
    def request_total(self):
        return self._request_total

    @property
    def request_error(self):
        return self._request_error

    @classmethod
    def from_spider(cls, spider):
        pass

    def get(self, url=None, **request):
        try:
            return requests.get(url, verify=False, **request)
        except Timeout:
            response = Response(status_code=Response.TIMEOUT, url=url, error_msg='请求超时')
        except ProxyError:
            response = Response(status_code=Response.PROXY_ERROR, url=url, error_msg='代理错误')
        except Exception as e:
            response = Response(status_code=Response.ERROR, url=url, error_msg=str(e))
        logger.error(f'[%s] %s', response.error_msg, url)
        return response

    def post(self, url=None, timeout=60, **request):
        try:
            return requests.post(url, timeout=timeout, verify=False, **request)
        except Timeout:
            response = Response(status_code=Response.TIMEOUT, url=url, error_msg='请求超时')
        except ProxyError:
            response = Response(status_code=Response.PROXY_ERROR, url=url, error_msg='代理错误')
        except Exception as e:
            response = Response(status_code=Response.ERROR, url=url, error_msg=str(e))
        logger.error(f'[%s] %s', response.error_msg, url)
        return response

    def execute(self, request):
        if request.do_filter:
            if request.fingerprint in self.dones:
                return
            self.dones.add(request.fingerprint)
        if request.method.lower() == 'get':
            response = self.get(**request)
        else:
            response = self.post(**request)
        response.meta = request.meta
        if request.encoding is not None:
            response.encoding = request.encoding
        # response.fingerprint = request.fingerprint
        result = None
        logger.debug("Request<%s>%s", response.status_code, response.url)
        self._request_total += 1
        if response.status_code >=200 and response.status_code < 300:
            if request.callback:
                # try:
                result = request.callback(response)
                # except Exception as e:
                #     logger.info("callback error, %s", str(e))
        elif request.done_times < request.try_times:
            request.done_times += 1
            request.do_filter = False
            self._queue.put(request)
            return logger.info("Retry<%s> %s", request.done_times, request['url'])
        elif request.errorcall:
            try:
                result = request.errorcall(response)
            except Exception as e:
                logger.info("error call error: %s", str(e))
            self._request_error += 1
        else:
            self._request_error += 1
        if isinstance(result, types.GeneratorType):
            for item in result:
                if isinstance(item, Request):
                    self._queue.put(item)
                else:
                    self._item_queue.put(item)

    def run(self):
        while self._run_flag:
            self._pause_flag.wait()
            request = self._queue.get()
            self.execute(request)
            self._queue.task_done()
    

class CrawlerDownloader(HttpDownloader):

    @classmethod
    def from_spider(cls, spider):
        cls.spider = spider
        cls._rule_map = spider._rule_map

    def _under_rule(self, url, rule_map):   # 对于followed的匹配项, 必须全部匹配成功才算正确，对于unfollowed，只要有一个匹配就算成功
        for rule in rule_map['unfollowed']:
            if rule.search(url):
                return True
        for rule in rule_map['followed']:
            if not rule.search(url):
                return False
        return True

    def get_rule_callback(self, url):
        for _, rule_map in self._rule_map.items():
            if self._under_rule(url, rule_map):
                return rule_map['callback']
        return None

    def execute(self, request):
        url = request['url']
        callback = request.callback or self.get_rule_callback(url)
        if callback is None:
            return
        if request.depth > request.max_depth:
            return
        if request.do_filter:
            fingerprint = request.fingerprint
            if fingerprint in self.dones:
                # print(request['url'], 'done')
                return
            self.dones.add(fingerprint)
        request['headers'] = request.headers or self.headers
        if request.method == 'GET':
            response = self.get(**request)
        else:
            response = self.post(**request)
        response.meta = request.meta
        response.depth = request.depth
        response.fingerprint = request.fingerprint
        # response.doc = lambda: PyQuery(response.text)
        if request.encoding is not None:
            response.encoding = request.encoding
        result = None
        logger.debug("Request<%s,%s,%s>%s", request.method, response.status_code, response.depth, response.url)
        if response.status_code >=200 and response.status_code < 300:
            result = callback(response) if request.callback else callback(self.spider, response) 
        elif request.done_times < request.try_times:
            request.done_times += 1
            request.do_filter = False
            self._queue.put(request)
            return logger.info("Retry<%s> %s", request.done_times, request['url'])
        elif request.errorcall:
            result = request.errorcall(response)
        if isinstance(result, types.GeneratorType):
            for item in result:
                if isinstance(item, CrawlerRequest):
                    self._queue.put(item)
                else:
                    self._item_queue.put(item)


class DownloaderPool(object):
    def __init__(self, downloader, num):
        self._thread_list = []
        self.dones = set()
        self.init_pool(downloader, num)

    def init_pool(self, downloader:HttpDownloader, num):
        for i in range(num):
            thread: HttpDownloader = downloader(dones=self.dones, name='%s_%s' % (downloader.__class__.__name__, i))
            self._thread_list.append(thread)

    @property
    def request_total(self):
        return sum([thread.request_total for thread in self._thread_list])

    @property
    def request_error(self):
        return sum([thread.request_error for thread in self._thread_list])
    
    def start(self):
        for thread in self._thread_list:
            thread.start()

    def resume(self):
        for thread in self._thread_list:
            thread.resume()

    def pause(self):
        for thread in self._thread_list:
            thread.pause()

    def stop(self):
        for thread in self._thread_list:
            thread.stop()
