from .item import BaseItem

class OrmItem(BaseItem):
    def save(self):
        pass


if __name__ == '__main__':
    item = OrmItem()
    item.save()