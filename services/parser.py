#from services.provider.biglion import Provider, Offer
from urllib.parse import urlparse
import importlib
from spider.models import OfferUrl
from progress.bar import Bar
import urllib.request
from offers.models import Offer, OfferItem


class Parser:

    def __init__(self):
        self.content_providers_list = {}

    def get_content_by_url(self, url):
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as f:
            return f.read().decode('utf-8')

    def get_content_provider(self, name, key=None):
        if key is None:
            key = name
        if key not in self.content_providers_list:
            mod = importlib.import_module('services.provider.'+name)
            if hasattr(mod, 'ContentProvider') is False:
                return False
            content_provider = getattr(mod, 'ContentProvider')()
            self.content_providers_list[key] = content_provider
        return self.content_providers_list[key]

    def fill_offer_by_url(self, offer, url):
        #content_provider = Provider()
        #content = content_provider.get_content_by_url(url)
        #content_provider.fill_offer_from_content(offer, content)
        pass


    def pull_offers(self):
        content_provider = self.get_content_provider('biglion')
        offers_urls_list = OfferUrl.objects.all()
        for offer_url in offers_urls_list[0:100]:
            print(offer_url.url)
            content = self.get_content_by_url(offer_url.url)
            offer_structure = content_provider.get_offer_structure(content)
            if offer_structure.title is None:
                continue
            offer = Offer()
            offer.title = offer_structure.title
            offer.likes_count = offer_structure.likes_count
            offer.purchases_count = offer_structure.purchases_count
            offer.rules = offer_structure.rules
            offer.description = offer_structure.description
            offer.expiration_date = offer_structure.expiration_date
            offer.coupon_expiration_date = offer_structure.coupon_expiration_date
            offer.coupon_beginning_usage_date = offer_structure.coupon_beginning_usage_date
            offer.save()

            print(offer.pk)


    def execute(self):
        content_provider = self.get_content_provider('biglion')
        offers_urls_list = OfferUrl.objects.all()
        offset = 1
        for offer_url in offers_urls_list[offset:offset+1]:
            print(offer_url.url)
            content = self.get_content_by_url('http://www.biglion.ru/deals/seti-jakitorija-50/')
            offer_structure = content_provider.get_offer_structure(content)
            print(offer_structure.expiration_date)


        return

        content_provider = self.get_content_provider('biglion')
        """
        Получаем список URL для загрузки контента
        """
        urls_list = content_provider.get_urls()
        if (urls_list is None) or (len(urls_list) < 1):
            return
        """
        Обходим этот список, и получаем данные для каждой страницы
        """
        bar = Bar('Processing', max=len(urls_list))
        for url in urls_list:
            bar.next()
            up = urlparse(url)
            if up.netloc != 'www.biglion.ru':
                continue
            if up.path == '':
                continue
            offer_url = OfferUrl()
            offer_url.url = url
            offer_url.offer_provider_id = 1
            offer_url.save()
            #offer = Offer()
            #offer.url = url
            #self.fill_offer_by_url(offer, url)
            #print(offer.url)
            #print(offer.title)
        bar.finish()
