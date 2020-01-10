from . import parser
from .request import Request, CrawlerRequest
from .recorder import Recorder
from .log import spider_logger as logger
from .queue import set_download_queue, set_record_queue
from .downloader import DownloaderPool, HttpDownloader, CrawlerDownloader
from queue import Queue
from urllib.request import urljoin
import time


class ConeSpider(object):
    start_urls = []
    download_queue = None
    record_queue = None
    recorder = None
    downloader = None
    downloader_num = 1
    schedule_delay = 20
    block = False

    def __init__(self):
        self.init_queue()
        self.init_downloader()
        self.init_recorder()
        logger.info("spider init")
        
    def init_queue(self):
        if not self.download_queue:
            self.download_queue = Queue()
        set_download_queue(self.download_queue)
        if self.record_queue is None:
            self.record_queue = Queue()
        set_record_queue(self.record_queue)
        logger.info("queue init")

    def init_downloader(self):
        if not self.downloader:
            from .downloader import HttpDownloader
            self.downloader = HttpDownloader
        self.downloader.from_spider(self)
        self.download_pool = DownloaderPool(self.downloader, self.downloader_num)
        logger.info("downloader init")

    def init_recorder(self):

        if not self.recorder:
            self.recorder = Recorder
        self.recorder.from_spider(self)
        self.recorder = self.recorder()
        logger.info("recorder init")

    def start_requests(self):
        for url in self.start_urls:
            Request(url=url, callback=self.parse).start_request()

    def schedule(self):
        print("schedule")

    def should_break(self):
        if self.recorder:
            return self.download_queue.empty() \
                   and self.record_queue.empty() \
                   and self.download_queue.unfinished_tasks == 0 \
                   and self.record_queue.unfinished_tasks == 0
        return self.download_queue.empty() and self.download_queue.unfinished_tasks == 0

    def loop(self):
        while self.block or not self.should_break():
            self.schedule()
            try:
                time.sleep(self.schedule_delay)     
            except KeyboardInterrupt:
                try:
                    logger.info("PRESS CTRL + C TO STOP")
                    time.sleep(2)
                    self.pause()
                    logger.info("spider pause(PRESS CTRL + C CONTINE)")
                    try:
                        while True:
                            time.sleep(2)
                    except KeyboardInterrupt:
                        self.resume()
                except KeyboardInterrupt:
                    break

    def parse(self, response):
        pass

    def start(self):
        logger.info("spider start")
        if self.recorder:
            self.recorder.start()
        self.download_pool.start()
        self.start_requests()
        self.loop()
        self.stop()

    def pause(self):
        self.download_pool.pause()
    
    def resume(self):
        self.download_pool.resume()

    def stop(self):
        self.download_pool.stop()
        if self.recorder:
            self.recorder.stop()
            logger.info("spider stop, used time %.2f, send %s request", time.time()-self.recorder.start_time, len(self.download_pool.dones))

    @classmethod
    def item_count(cls, method):
        setattr(cls, 'item_total_num', 0)
        setattr(cls, 'item_success_num', 0)

        def method_wrapper(spider, *args):
            success = method(spider, *args)
            if success:
                cls.item_success_num += 1
            cls.item_total_num += 1
            return success
        return method_wrapper


class CrawlerSpider(ConeSpider):
    downloader = CrawlerDownloader

    def __new__(cls, *args, **kwargs):
        from .rule import _RULE_MAP
        cls._rule_map = _RULE_MAP
        return object.__new__(cls)

    def start_requests(self):
        for url in self.start_urls:
            CrawlerRequest(url=url, callback=self.parse).start_request()
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)