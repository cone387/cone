import re
from .downloader import CrawlerDownloader
from .request import Request
from urllib.request import urljoin


_SPIDER = None
_RULE_MAP = {}  # 'method': {'followed': [], 'unfollowed': [], 'callback': callback}


def ruled_spider(spider):
    spider._rule_map = _RULE_MAP
    spider.downloader = CrawlerDownloader
    print("rule map:", _RULE_MAP)

    from . import parser
    @parser.use_pyquery
    def extract_link(spider, response):
        try:
            link_list = response.doc()('a')
        except Exception as e:
            return
        for link_item in link_list.items():
            url = link_item.attr('href')
            if url:
                if not url.startswith('http'):
                    url = urljoin(response.url, url)
                yield Request(url=url)

    spider.extract_link = extract_link
    return spider


def under_rule(rule, followed=False):
    global _RULE_MAP
    def parse_rule(parse_method):
        _RULE_MAP.setdefault(parse_method.__name__, {'followed': [], 'unfollowed': [], 'callback': parse_method})
        if followed:
            _RULE_MAP[parse_method.__name__]['followed'].append(re.compile(rule))
        else:
            _RULE_MAP[parse_method.__name__]['unfollowed'].append(re.compile(rule))
        return parse_method
    return parse_rule
