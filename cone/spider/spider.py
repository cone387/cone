import time
from .pool import Pool
from .recorder import Recorder, BaseRecorder
from queue import Queue
from .downloader import BaseDownloader
import logging

logger = logging.getLogger(__name__)


class ConeSpider(object):
    """
        Spider包括下载器, 解析器。
    """
    info_delay = 20 # 设置20/s打印一次信息。可以重写info方法自定义信息的内容
    block = False   # 设置当没有下载任务时是否退出爬虫。
    queue = None    # 爬虫使用的队列，可以使用自定义队列。
    downloader = None
    downloader_num = 3
    recorders = []
    start_urls = []
    # _recorder = None
    # _downloader_pool = None
    def __init__(self):
        # init downloader and recorder
        self.start_time = time.time()
        self.init_downloader()
        self.init_recorder()
        logger.debug('spider init')

    
    def init_downloader(self):
        """
            初始化下载器, 使用多线程, 每一个下载器就是一个线程
        """
        if self.downloader is None:
            self.downloader = BaseDownloader
        if self.queue is None:
            self.queue = Queue()
        self.downloader.from_spider(self)
        self._downloader_pool = Pool(self.queue, self.downloader, self.downloader_num)
        logger.debug('downloader init')
    
    def init_recorder(self):
        self._recorder = None
        if len(self.recorders) != 0:
            self._recorder = Recorder()
            for recorder in self.recorders:
                recorder.from_spider(self)
                self._recorder.add_recorder(recorder())
        logger.debug('recorder init')

    def download(self, priority=100, **kwargs):
        self._downloader_pool.do(priority, **kwargs)

    def record(self, item, priority=100, record=None):
        self._recorder.do(priority, item=item, record=record)

    def parse(self, response):
        print(response.status_code)

    def before_start(self):
        for url in self.start_urls:
            self.download(url=url, callback=self.parse)
    
    def if_break(self):
        self._downloader_pool.check_thread()
        if not self._downloader_pool.isAlive():
            # while not self._downloader_pool.queue.empty():
            #     self._downloader_pool.queue.get(timeout=1)
            # self._downloader_pool.queue.unfinished_tasks = 0
            return True
        if (self._downloader_pool is None or (self._downloader_pool.queue.empty() and \
            not self._downloader_pool.queue.unfinished_tasks)) and \
            (self._recorder is None or not self._recorder.queue.unfinished_tasks) and not self.block:
                logger.info('spider finished, used time: %.1fs', time.time()-self.start_time)
                return True
        # print('dq empty', self._downloader_pool.queue.empty())
        # print('dq unfinished_tasks', self._downloader_pool.queue.unfinished_tasks)
        # print('rq', self._recorder.queue.unfinished_tasks)
        return False

    def info(self):
        now_time = time.time()
        d_speed_str = r_speed_str = ''
        d_left = r_left = ''
        if self._downloader_pool is not None:
            d_speed = '%02f'%(len(self._downloader_pool.dones) / (now_time - self._downloader_pool.start_time))
            d_speed_str = f'download speed <{d_speed}/s>'
            d_left = 'request left %d'%self._downloader_pool.queue.qsize()
        if self._recorder is not None:
            r_left = 'record left: %s'%self._recorder.queue.qsize()
            recorders = self._recorder.get_recorder_info()
            for name, info in recorders.items():
                speed = '%02f'%(info['success_num'] / (now_time - self._recorder.start_time))
                r_speed_str += f'{name} record speed <{speed}/s>'
        logger.info(f'{d_left} {r_left}')
        logger.info(f'{d_speed_str},{r_speed_str}')

    def loop(self, delay=20):
        while True:
            if self.if_break():
                break
            try:
                time.sleep(self.info_delay)
                self.info()       
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
                        self.info()
                except KeyboardInterrupt:
                    return
    
    """
        以下start, pause, stop便于控制爬虫的运行.
    """

    def start(self, info=True):
        logger.debug("spider start")
        if self._recorder is not None:
            self._recorder.start()
        self._downloader_pool.start()
        self.before_start()
        self.loop()
        self.stop()

    def pause(self):
        if self._downloader_pool is not None:
            self._downloader_pool.pause()
        if self._recorder is not None:
            self._recorder.pause()
        logger.debug("spider pause")
    
    def resume(self):
        if self._downloader_pool is not None:
            self._downloader_pool.resume()
        if self._recorder is not None:
            self._recorder.resume()
        logger.debug("spider resume")
    
    def stop(self):
        if getattr(self, '_downloader_pool', None):
            self._downloader_pool.stop()
            self.downloader = None
            self._downloader_pool = None

        if getattr(self, '_recorder', None):
            self._recorder.stop()
            self._recorder = None
        logger.debug("spider stop")
    