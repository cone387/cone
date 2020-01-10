import pymongo


class Mongodb():
    db = None
    client = None
    collection = None
    def __init__(self, connect_str=None, host=None, port=None, db=None, collection=None, primary_key=None):
        assert db and collection, 'db or collection can not be None'
        if connect_str:
            self.client = pymongo.MongoClient(connect_str)
        else:
            self.client = pymongo.MongoClient(host=host, port=port) 
        self.db = self.client[db]
        self.collection = self.db[collection]
        if primary_key:
            self.collection.ensure_index(primary_key, unique=True)
        print("connect to mongodb")    
            
    def close(self):
        if self.client:
            self.client.close()
        print("mongodb disconnect")