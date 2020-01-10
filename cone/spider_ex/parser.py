from pyquery import PyQuery
from lxml import etree
from .request import CrawlerRequest
from urllib.request import urljoin


def use_pyquery(parse_method):
    def wrapper(spider, response):
        response.doc = lambda: PyQuery(response.text)
        return parse_method(spider, response)
    return wrapper


def use_xpath(parse_method):
    def wrapper(spider, response):
        response.etree = lambda: etree.HTML(response.text)
        return parse_method(spider, response)
    return wrapper


def extract_link(parse_method):
    def wrapper(spider, response):
        response.doc = lambda: PyQuery(response.text)
        try:
            link_list = response.doc()('a')
        except Exception as e:
            return
        for link_item in link_list.items():
            url = link_item.attr('href')
            if url and not url.startswith('javascript'):
                if not url.startswith('http'):
                    url = urljoin(response.url, url)
                CrawlerRequest(url=url, depth=response.depth).start_request()
                # break
        return parse_method
    return wrapper