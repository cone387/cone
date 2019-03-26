from spider import ConeSpider
import jieba
import re
import time
import random
from collections import Counter
from urllib.request import quote
from urllib.parse import urljoin
from pyquery import PyQuery as pq
from logger import logger

class TestSpider(ConeSpider):
    start_urls = ["http://www.baidu.com/s?wd=衣服"]
    def parse_page(self, response):
        doc = pq(response.text)
        title = pq(response.content)("title").eq(0).text()
        text = doc.text()
        text = re.sub("<.*?>|</script>|/\*.*?\*/|[a-zA-Z]|\d|[\s\+\.&_,\$%\^\*#]", "", text)
        logger.debug(f"parse_page from {title}({response.url})")
        page = jieba.cut(text)
        page = [x for x in page if len(x)>1]
        c = Counter(page).most_common(10)
        logger.debug(f'parse key words: {c}')

    def parse(self, response):
        logger.debug("parse_query_url")
        doc = pq(response.content)
        for i in range(1, 10):
            # a = doc(f"#{i}")('a').eq(0)
            # href = a.attr("href")
            # title = a.text().strip()
            # if href is not None:
            #     logger.debug(f"get {title}")
            #     rdownloader.download({'url': href, 'callback': self.parse_page_url,
            #     })
            a = doc(f"#{i}")#.('a:first')#('a').eq(0)
            a = re.search('<a.*?</a>', a.html())
            if a:
            # href = a.attr("href")
            # title = a.text().strip()
                href = re.search('href="(.*?)"', a.group())
                title = re.search(">(.*?)<", a.group())
                if href is not None:
                    logger.debug(f"get {title.group(1)}")
                    self.download(
                        {'url': href.group(1), 
                        'callback': 
                        self.parse_page_url})

    def parse_page_url(self, response):
        doc = pq(response.content)
        links = doc("a")
        url_list = []
        for a in links.items():
            href = a.attr("href")
            title = a.text()  
            if not href:
                continue
            if href.startswith("/"):
                url_list.append((title, urljoin(response.url, href)))
            elif href == response.url:
                continue
            elif href.find(response.url) != -1:
                url_list.append((title, href))
        logger.debug(f"sample len is {len(url_list)}")
        url_list = random.sample(url_list, len(url_list) % 5)
        for title,  url in url_list:
            self.download({'url':url, 'callback': self.parse_page})

    # def run(self):
    #     logger.debug("parser runing...")
    #     query = BAIDU_ROOT_URL.format(wd=quote("衣服"))
    #     rdownloader.download({'url': query, 'callback': self.parse_query_url})
if __name__ == '__main__':
    TestSpider().start()