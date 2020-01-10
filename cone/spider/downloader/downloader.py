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
    delay = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'}
    def __init__(self, queue, dones=set(), errors=set(), name='downloader'):
        self.dones = dones
        self.errors = errors
        super().__init__(queue, name=name)
        logger.debug("%s init"%self.__class__.__name__)
        
    @classmethod
    def from_spider(cls, spider):
        pass

    def download(self, url=None, **kwargs):
        """
            url: **,
            **kwargs,
            700: connecttimeout
            800: 代理错误
            600: 未知错误
        """
        headers = kwargs.pop('headers', self.headers)
        try:
            return requests.get(url, headers=headers, timeout=60, verify=False, **kwargs)
        except requests.exceptions.ConnectTimeout:
            # logger.info('ConnectTimeout, redownload...')
            return Response(status_code=700, url=url) 
            # return self.download(url, **kwargs)
        except requests.exceptions.ProxyError:
            # logger.info('ProxyError, redownload...')
            # return self.download(url, **kwargs, page+=1)
            return Response(status_code=800, url=url) 
        except Exception as e:
            # download<{self.name}> 
            logger.info(f'error: download {url} {e}')
            return Response(status_code=600, url=url, error_msg=str(e))  
      
    def fingerprint(self, url):
        return get_md5(url)

    def execute(self, url=None, **kwargs):
        do_filter = kwargs.pop('do_filter', False)
        fingerprint = self.fingerprint(url)
        if do_filter and fingerprint in self.dones:
            return
        meta = kwargs.pop('meta', {})
        delay = kwargs.pop('timeout', self.delay)
        callback = kwargs.pop('callback', None)
        errorcall = kwargs.pop('errorcall', None)
        http302 = kwargs.pop('http302', None)
        res = self.download(url, **kwargs)
        status_code = res.status_code
        res.meta = meta
        if status_code == 200:
            logger.debug(f'download<{self.name}> {url} <{status_code}>')
            if callback:
                try:
                    callback(res)
                except Exception as e:
                    logger.error('callback error: %s', str(e))
        elif status_code == 302 and http302:
            http302(res)
        else:
            logger.info(f'error: download<{self.name}> {url} {status_code}')
            if errorcall:
                try:
                    errorcall(res)
                except Exception as e:
                    logger.error('errorcall error: %s', str(e))
            self.errors.add(fingerprint)    
        time.sleep(delay)
        self.dones.add(fingerprint)
