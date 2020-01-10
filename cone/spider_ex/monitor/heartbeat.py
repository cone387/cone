import requests
import socket
import time
import os
from cone.spider_ex import logger

try:
    from cone.spider_ex import ConeSpider
except ImportError:
    class ConeSpider:
        pass

hostname = socket.gethostname()


def heartbeat(url=None, group=None, machine=hostname, interval=30, pid=os.getpid(), **kwargs):
    assert url is not None, '监控Url不能为空'

    def send_package(data):
        try:
            logger.info('[heartbeat]%s send success, %s', data, requests.post(url, data=data).status_code)
        except Exception as e:
            logger.info("[heartbeat]%s send error, %s", data, str(e))

    def schedule(method):
        method.last_time = time.time() - interval
        method.last_request_total = 0
        method.last_request_error = 0
        method.last_item_total = 0
        method.last_item_success = 0

        def method_wrapper(spider: ConeSpider, *args):
            now = time.time()
            if now - method.last_time >= interval:
                # print("request total", spider.download_pool.request_total - method.last_request_total)
                # print("request error", spider.download_pool.request_error - method.last_request_error)
                # print('item total', spider.item_total_num - method.last_item_total)
                # print('item success', spider.item_success_num - method.last_item_success)
                method.last_time = now
                send_package({
                    'group': group,
                    'machine': machine,
                    'request_total': spider.download_pool.request_total - method.last_request_total,
                    'request_error': spider.download_pool.request_error - method.last_request_error,
                    'item_total': spider.item_total_num - method.last_item_total,
                    'item_success': spider.item_success_num - method.last_item_success,
                    'pid': pid,
                    **kwargs
                })
                method.last_request_total = spider.download_pool.request_total
                method.last_request_error = spider.download_pool.request_error
                method.last_item_success = spider.item_success_num
                method.last_item_total = spider.item_total_num
            return method(spider, *args)
        return method_wrapper
    return schedule


def reset(url=None, group=None, machine=hostname):
    assert url and group, 'url或group不能为空'
    try:
        print('[reset]status, %s' % requests.post(url, data={
            'group': group,
            'machine': machine
        }).status_code)
    except Exception as e:
        print("[reset]error, %s" % str(e))

    def method_wrapper(method):
        return method
    return method_wrapper
