# spider
一个简单的爬虫框架, 性能什么的可能不行，但应该蛮简单。

可以直接运行demo_spider查看效果


贴出部分demo代码

# 定义一个OriginSqlItem便于数据入库

```python
class DemoItem(OriginSqlItem):
    title = Field('nvarchar(100)')
    tag = Field('nvarchar(20)')
    url = Field('nchar(500)')
```

# 定义一个Recorder规定数据保存方式
```python
class DemoRecorder(BaseRecorder):
    table = 'demo_table'
    def __init__(self):
        super().__init__()
        self.sql = Sqliter(**SQL)
        DemoItem.create_item(self.sql, self.table, sqltype='sqlite')

    def record(self, item):
        return DemoItem.save(self.sql, self.table, item)
```

"""
    或者直接使用SqlRecorder入库
    class DemoRecorder(SqlRecorder):
        sql = Sqliter(**SQL)
        model = DemoItem
        table = 'demo'
"""

# 与Scrapy的部分操作类似
```python
class DemoSpider(ConeSpider):
    """
        如果遇到反爬可以自定义downloader
    """
    recorders = [DemoRecorder]
    base_url = 'http://www.chinanews.com/scroll-news/news%d.html'
    start_urls = ['http://www.chinanews.com/scroll-news/news1.html']

    def parse(self, response):
        pass
        """详见demo_spider"""
```

spider = DemoSpider()
spider.start()
即可运行爬虫,Ctrl + C 暂停，连按关闭爬虫
