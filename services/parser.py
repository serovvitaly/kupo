#from services.provider.biglion import Provider, Offer
import json
from urllib.parse import urlparse
import importlib
from spider.models import OfferUrl
#from progress.bar import Bar
import urllib.request
from offers.models import Offer, OfferItem, OfferMedia, OfferProperty, Place, Merchant
from datetime import datetime, timezone
from services.offer import OfferEntity, PlaceEntity, OfferItemEntity, TagEntity

from pymemcache.client.base import Client as MemClient
mem_client = MemClient(('localhost', 11211))


class Parser:

    def __init__(self, provide_name):
        self.provide_name = provide_name
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
        content_provider = self.get_content_provider(self.provide_name)
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
        print('Pull services...')
        urls += self.get_urls_all('services')
        print('Pull hotels...')
        urls += self.get_urls_all('hotels')
        print('Pull tours...')
        urls += self.get_urls_all('tours')
        print('Pull goods...')
        urls += self.get_urls_all('services/goods')

        #bar = Bar('Writing to database', max=len(urls))
        for url in urls:
            offer = Offer.objects.filter(url__exact=url).first()
            if offer is None:
                offer = Offer()
                offer.url = url
                offer.created_date = datetime.now(tz=timezone.utc)
            offer.save()
            #bar.next()
        #bar.finish()

    def get_offer_entity_by_url(self, url):
        content_provider = self.get_content_provider(self.provide_name)
        content = self.get_content_by_url(url, use_cache=True)
        offer_structure = content_provider.get_offer_structure(content)
        if offer_structure.title is None:
            return False

        items = []
        for item in offer_structure.items:
            items.append(OfferItemEntity(
                title=item.title
            ))

        tags = []
        for tag in offer_structure.tags:
            tags.append(TagEntity(
                title=tag.title
            ))

        places = []
        for place in offer_structure.places:
            places.append(PlaceEntity(
                title=place.title
            ))

        offer_entity = OfferEntity(
            title=offer_structure.title,
            rules=offer_structure.rules,
            description=offer_structure.description,
            items=items,
            tags=tags,
            places=places,
        )
        return offer_entity

    def pull_offer_by_url(self, url):
        content_provider = self.get_content_provider(self.provide_name)
        content = self.get_content_by_url(url, use_cache=True)
        offer_structure = content_provider.get_offer_structure(content)
        if offer_structure.title is None:
            return False



        merchant = Merchant()
        merchant.name = offer_structure.merchant.name
        merchant.save()

        offer = Offer.objects.filter(url__exact=url).first()

        if offer is None:
            offer = Offer()
            offer.created_date = datetime.now()

        offer.status = 'd'
        offer.merchant = merchant
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

        for tag in offer_structure.tags:
            offer_property = OfferProperty()
            offer_property.offer = offer
            offer_property.type = 'string'
            offer_property.name = 'tag'
            offer_property.value = tag
            offer_property.save()

        for place_obj in offer_structure.merchant.places:
            if place_obj.address is not None:
                pass
            if place_obj.metro is not None:
                pass
            if place_obj.phone_number is not None:
                pass
            place_obj_dict = place_obj.__dict__
            if len(place_obj_dict) < 1:
                continue
            place = Place()
            place.merchant = merchant
            place.data = json.dumps(place_obj_dict)
            place.save()


    def pull_offer_by_id(self, offer_id):
        offer = Offer.objects.get(pk=offer_id)
        if offer is None:
            return False
        return self.pull_offer_by_url(offer.url)



    def pull_offers(self):
        offers = Offer.objects.filter(status__exact='o').all()
        #bar = Bar('Processing', max=len(offers))
        for offer in offers:
            #bar.next()
            self.pull_offer_by_url(offer.url)
        #bar.finish()


    def execute(self):
        content_provider = self.get_content_provider(self.provide_name)
        offers_urls_list = OfferUrl.objects.all()
        offset = 1
        for offer_url in offers_urls_list[offset:offset+1]:
            print(offer_url.url)
            content = self.get_content_by_url('http://www.biglion.ru/deals/seti-jakitorija-50/')
            offer_structure = content_provider.get_offer_structure(content)
            print(offer_structure.expiration_date)


        return

        content_provider = self.get_content_provider(self.provide_name)
        """
        Получаем список URL для загрузки контента
        """
        urls_list = content_provider.get_urls()
        if (urls_list is None) or (len(urls_list) < 1):
            return
        """
        Обходим этот список, и получаем данные для каждой страницы
        """
        #bar = Bar('Processing', max=len(urls_list))
        for url in urls_list:
            #bar.next()
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
        #bar.finish()
