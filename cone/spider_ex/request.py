from .queue import get_dowonload_queue
from cone.tools import get_md5


class Request(dict):

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}

    def __init__(self, url=None, callback=None, method='GET', headers=None,
                 cookies=None, meta=None, priority=0, encoding=None, timeout=30,
                 do_filter=False, try_times=3, errorcall=None, **kwargs):
        self.priority = priority
        self.do_filter = do_filter
        self.errorcall = errorcall
        self.meta = meta
        self.method = method
        self.encoding = encoding
        self.callback = callback
        self.done_times = 1
        self['timeout'] = timeout
        self['url'] = url
        self['cookies'] = cookies
        self['headers'] = headers or self.headers
        self._fingerprint = None
        self.try_times = try_times
        self.update(kwargs)
    
    @property
    def fingerprint(self):
        if self._fingerprint is None:
            self._fingerprint = get_md5(self['url'])
        return self._fingerprint

    def start_request(self):
        queue = get_dowonload_queue()
        queue.put(self)

    def __lt__(self, other):
        # priority越小，处理优先级越高
        return self.priority < other.priority


class CrawlerRequest(Request):
    def __init__(self, depth=1, max_depth=2, **kwargs):
        self.depth = depth
        self.max_depth = max_depth
        super().__init__(**kwargs)

