from collections import OrderedDict


class MetaItem(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for k, v in list(attrs.items()):
            if isinstance(v, Field):
                fields[k] = v
            elif isinstance(v, Relation):
                attrs['relation'] = v
        attrs['fields'] = fields
        return type.__new__(cls, name, bases, attrs)

    @classmethod
    def __prepare__(metacls, cls, bases, **kwds):
        return OrderedDict()

    def save(self):
        pass


class Field(str):
    def __new__(cls, value, descr=None):
        obj = str.__new__(cls, value)
        obj.descr = descr
        return obj
        

class Relation(str):
    pass


class BaseItem(dict, metaclass=MetaItem):
    fields = {}
    relation = None

    def get(self, k, d=None):
        return self.fields.get(k, d)

    def __getitem__(self, k):
        return self.fields.__getitem__(k)

    def __setitem__(self, k, v):
        self.fields[k] = v

    def __delitem__(self, key):
        del self.fields[key]

    def __len__(self):
        return len(self.fields)

    def __repr__(self):
        return self.fields.__repr__()