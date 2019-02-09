import requests
import time
import logging
from ..thread import BaseThread
from ..response import Response
from cone.tools import get_md5
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


logger = logging.getLogger(__name__)


#  download with requests

class BaseDownloader(BaseThread):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'}
    
    def __init__(self, queue, dones=set(), errors=set(), name='downloader'):
        self.dones = dones
        self.errors = errors
        super().__init__(queue, name=name)
        logger.debug("%s init"%self.__class__.__name__)
        
    @classmethod
    def from_spider(cls, spider):
        pass

    def download(self, url, **kwargs):
        """
            url: **,
            **kwargs,
        """
        try:
            return requests.get(url, headers=self.headers, verify=False, **kwargs)
        except Exception as e:
            logger.info(f'error: download<{self.name}> {url} {e}')
            return Response(status_code=400, url=url, error_msg=str(e))  
      
    def fingerprint(self, url):
        return get_md5(url)

    def execute(self, url, **kwargs):
        do_filter = kwargs.pop('do_filter', False)
        fingerprint = self.fingerprint(url)
        if do_filter and fingerprint in self.dones:
            return
        meta = kwargs.pop('meta', {})
        delay = kwargs.pop('timeout', 0)
        callback = kwargs.pop('callback', None)
        errorcall = kwargs.pop('errorcall', None)
        http302 = kwargs.pop('http302', None)
        res = self.download(url, **kwargs)
        status_code = res.status_code
        res.meta = meta
        if status_code == 200:
            logger.debug(f'download<{self.name}> {url} <{status_code}>')
            if callback:
                callback(res)
        elif status_code == 302 and http302:
            http302(res)
        else:
            if errorcall: 
                errorcall(res)
            self.errors.add(url)    
        time.sleep(delay)
        self.dones.add(fingerprint)
