import importlib
import urllib.request
from contracts import contract
from spider.models import *
from services.repository import *
import sys

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

    @staticmethod
    @contract
    def get_provider_urls(provider_name: str, base_url: str) -> 'list(str)':
        parser = Parser(provider_name)
        content_provider = parser.get_content_provider(provider_name)
        content = parser.get_content_by_url(base_url)
        return content_provider.get_entry_urls(content)

    @contract
    def get_offers_urls(self, url: str) -> 'list(str)':
        content_provider = self.get_content_provider(self.provide_name)
        content = self.get_content_by_url(url, use_cache=True)
        return content_provider.get_offers_urls(content)

    @contract
    def get_pages_count(self, url: str) -> int:
        content_provider = self.get_content_provider(self.provide_name)
        content = self.get_content_by_url(url, use_cache=True)
        return content_provider.get_pages_count(content)

    @staticmethod
    def pull_offers():
        base_urls = OfferUrl.objects.all()
        for base_url in base_urls:
            urls = Parser.get_provider_urls(
                base_url.offer_provider.provider,
                base_url.url
            )
            for entry_url in urls:
                entry_url = base_url.url + entry_url
                provider = Parser(base_url.offer_provider.provider)
                offers_urls = provider.get_offers_urls(entry_url)
                if len(offers_urls) < 1:
                    continue
                for offer_url in offers_urls:
                    try:
                        offer_url = base_url.url + offer_url
                        print(offer_url)
                        offer_content = provider.get_content_by_url(offer_url)
                        content_provider = provider.get_content_provider(base_url.offer_provider.provider)
                        offer_entity = content_provider.get_offer_structure(offer_content, offer_url)
                        sql_repository = SqlOfferRepository()
                        sql_repository.add(offer_entity)
                    except Exception as e:
                        print('ERROR:', e.__str__(), sys.exc_info())

