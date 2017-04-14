# from services.provider.biglion import Provider, Offer
import json
from urllib.parse import urlparse
import importlib
from spider.models import OfferUrl
# from progress.bar import Bar
import urllib.request
from offers.models import *
from datetime import datetime, timezone
from services.offer import *

from pymemcache.client.base import Client as MemClient

mem_client = MemClient(('localhost', 11211))


class Parser:
    def __init__(self, provide_name):
        self.provide_name = provide_name
        self.content_providers_list = {}

    @staticmethod
    def get_content_by_url(url, use_cache=False):
        if use_cache is True:
            cache = mem_client.get(url)
            if cache is not None:
                return cache.decode('utf8')
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as f:
            content = f.read()
            mem_client.set(url, content, 60 * 60)
            return content.decode('utf8')

    def get_content_provider(self, name, key=None):
        if key is None:
            key = name
        if key not in self.content_providers_list:
            mod = importlib.import_module('services.provider.' + name)
            if hasattr(mod, 'ContentProvider') is False:
                return False
            content_provider = getattr(mod, 'ContentProvider')()
            self.content_providers_list[key] = content_provider
        return self.content_providers_list[key]

    def get_offer_entity_by_url(self, url):
        content_provider = self.get_content_provider(self.provide_name)
        content = self.get_content_by_url(url, use_cache=True)

        offer_entity = content_provider.get_offer_structure(content, url)

        return offer_entity
