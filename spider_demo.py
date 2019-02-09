from cone.spider import ConeSpider, spider_logger as logger, BaseRecorder, SqlRecorder
from cone.spider.item import OriginSqlItem, Field
from cone.sql import Sqliter
from pyquery import PyQuery

"""
    以下就完成了对中国新闻网当日的滚动新闻的爬取入库.
"""


SQL = {
    # 'host': '47.94.99.0',
    'db': 'demo_db.db',
    # 'user': 'cone',
    # 'pwd': '3.1415926'
}


class DemoItem(OriginSqlItem):
    title = Field('nvarchar(100)')
    tag = Field('nvarchar(20)')
    url = Field('nchar(500)')


class DemoRecorder(BaseRecorder):
    table = 'demo_table'
    def __init__(self):
        super().__init__()
        self.sql = Sqliter(**SQL)
        DemoItem.create_item(self.sql, self.table, sqltype='sqlite')

    def record(self, item):
        return DemoItem.save(self.sql, self.table, item)

"""
    或者直接使用SqlRecorder
    class DemoRecorder(SqlRecorder):
        sql = Sqliter(**SQL)
        model = DemoItem
        table = 'demo'
"""


class DemoSpider(ConeSpider):
    """
        如果遇到反爬可以自定义downloader
    """
    recorders = [DemoRecorder]
    base_url = 'http://www.chinanews.com/scroll-news/news%d.html'
    start_urls = ['http://www.chinanews.com/scroll-news/news1.html']

    def parse(self, response):
        page = response.meta.get('page', 1)
        doc = PyQuery(response.content)
        lis = doc('.content_list li')
        lens = len(lis)
        logger.info(f'get {lens} news in page {page}')
        if not lis:
            logger.info("爬取完毕")
            return
        url = self.base_url % (page+1)
        self.download(url=url,
            timeout=1,
            callback=self.parse,
            meta={'page': page+1},
        )
        for li in lis.items():
            tag = li('.dd_lm a').text()
            title = li('.dd_bt').text()
            url = li('.dd_bt a').eq(0).attr('href')
            if tag and title and url:
                # logger.info(f'get news {tag}: {title} in page {page}')
                self.record(dict(
                    title=title.strip(),
                    tag=tag.strip(),
                    url=url
                ))



if __name__ == '__main__':
    spider = DemoSpider()
    spider.start()


