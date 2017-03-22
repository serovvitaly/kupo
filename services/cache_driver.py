from pymongo import MongoClient
from pymemcache.client.base import Client as MemClient
import json


class CacheDriver():

    def __init__(self):
        self.init()

    def init(self):
        pass

    def get(self, key):
        pass

    def set(self, key, value):
        pass


class MongoCacheDriver(CacheDriver):

    def init(self):
        client = MongoClient('localhost', 27017)
        db = client['Tmp']
        self.collection = db.CacheStorage

    def get(self, key):
        cache = self.collection.find({'key': key})
        if cache.count() < 1:
            return None
        return cache[0].get('value')

    def set(self, key, value):
        self.collection.insert_one({
            'key': key,
            'value': json.loads(value),
        })


class MemcachedCacheDriver(CacheDriver):

    def init(self):
        self.expiration = None
        self.client = MemClient(('localhost', 11211))

    def get(self, key):
        cache = self.client.get(key)
        if cache is None:
            return None
        return json.loads(cache.decode('utf8'))

    def set(self, key, value):
        self.client.set(key,  value, self.expiration)
