#from services.provider.biglion import Provider, Offer
from urllib.parse import urlparse
import importlib
from spider.models import OfferUrl
from progress.bar import Bar
import urllib.request
from offers.models import Offer, OfferItem, OfferMedia

from pymemcache.client.base import Client as MemClient
mem_client = MemClient(('localhost', 11211))


class Parser:

    def __init__(self):
        self.content_providers_list = {}


    def get_content_by_url(self, url, use_cache=False):
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


    def get_urls_all(self, section):
        base_url = 'http://www.biglion.ru/'+section+'/'
        content_provider = self.get_content_provider('biglion')
        first_page_content = self.get_content_by_url(base_url, use_cache=True)
        first_page_structure = content_provider.get_list_page_structure(first_page_content)
        if first_page_structure.total_pages is None:
            return
        urls = first_page_structure.urls_list
        for page in range(2, first_page_structure.total_pages + 1):
            page_url = base_url + '?page=' + str(page)
            #print(page_url)
            page_content = self.get_content_by_url(page_url, use_cache=True)
            page_structure = content_provider.get_list_page_structure(page_content)
            urls += page_structure.urls_list

        result_urls = []
        for url in urls:
            if url in result_urls:
                continue
            result_urls.append(url)
        return  result_urls


    def pull_urls(self):
        urls = []
        urls += self.get_urls_all('services')
        urls += self.get_urls_all('hotels')
        urls += self.get_urls_all('tours')
        urls += self.get_urls_all('services/goods')

        bar = Bar('Processing', max=len(urls))
        for url in urls:
            offer_url = OfferUrl()
            offer_url.url = url
            offer_url.offer_provider_id = 1
            offer_url.save()
            bar.next()
        bar.finish()


    def pull_offers(self):
        content_provider = self.get_content_provider('biglion')
        offers_urls_list = OfferUrl.objects.all()[0:281]
        bar = Bar('Processing', max=len(offers_urls_list))
        for offer_url in offers_urls_list:
            #print(offer_url.url)
            bar.next()
            content = self.get_content_by_url(offer_url.url, use_cache=True)
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

            for image_url in offer_structure.images:
                offer_media = OfferMedia()
                offer_media.url = image_url
                offer_media.offer = offer
                offer_media.save()

            #print(type(offer_structure.items))
            for item_odj in offer_structure.items:
                if item_odj.title is None:
                    continue
                offer_item = OfferItem()
                offer_item.title = item_odj.title
                offer_item.purchase_url = item_odj.purchase_url
                offer_item.discount_value = item_odj.discount_value
                offer_item.price_value = item_odj.price_value
                offer_item.offer = offer
                offer_item.save()

        bar.finish()

            #print(offer.pk)


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
