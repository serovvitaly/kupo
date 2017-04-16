"""
https://kupikupon.ru/
"""
import re
import time
from datetime import datetime, timezone
import lxml.etree as etree
from io import StringIO
from bs4 import BeautifulSoup
from services.offer import *
from contracts import contract
import json


class ContentDispatcher:
    def __init__(self, content, soup=False):
        self.content = content
        if soup is True:
            self.soup = BeautifulSoup(self.content, 'html.parser')

    def get_value_by_re(self, pattern, content=None):
        if content is None:
            content = self.content
        ms = re.search(pattern, content)
        if ms is None:
            return None
        st = ms.group(1).strip()
        if st == '':
            return None
        return st

    def get_values_by_re(self, pattern, content=None):
        if content is None:
            content = self.content
        ms = re.search(pattern, content)
        if ms is None:
            return None
        return ms.groups()


class MerchantContentDispatcher(ContentDispatcher):
    @property
    def name(self):
        return 'name'


class TagContentDispatcher(ContentDispatcher):
    @property
    def title(self):
        return ''


class PlaceContentDispatcher(ContentDispatcher):

    @property
    def address(self):
        address = self.soup.find(class_='adrtab a').contents
        if len(address) < 1:
            return None
        return address[0].strip()

    @property
    def metro(self):
        metro = self.soup.find(class_='adrtab m').contents
        if len(metro) < 1:
            return None
        return metro[0].strip()

    @property
    def phones(self):
        return [1,2]
        parts = re.findall(r'([\d+])', self.content['phones'].strip())
        phone = ''.join(parts)
        phones = [int(phone)]
        return phones

    @property
    def latitude(self):
        return 2.0

    @property
    def longitude(self):
        return 3.0


class OfferItemContentDispatcher(ContentDispatcher):
    @property
    def url(self):
        url = self.soup.form['action']
        return url.strip()

    @property
    def title(self):
        title = self.soup.find(class_='side-info').p.contents[0]
        return title.strip()

    @property
    def amount(self):
        ptrn = r'вместо ([\d]+)'
        amount = self.get_value_by_re(ptrn, self.title)
        if amount is None:
            return None
        return float(amount)

    @property
    def price(self):
        price = self.soup.find(class_='cost').contents
        if len(price) < 1:
            return None
        return float(price[0].strip())

    @property
    def discount(self):
        content = self.soup.find(class_='side-info').p.span.string
        discount = self.get_value_by_re(r'([\d]+)', content=content)
        return float(discount)


class OfferContentDispatcher(ContentDispatcher):
    @property
    def title(self):
        ptrn = r'<h1 itemprop="name">[\s]*<p>([\s\S]+?)<'
        return self.get_value_by_re(ptrn)

    @property
    def rules(self):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(self.content), parser)
        r = tree.xpath('//div[@class="deal_conditions_wrapper"]')
        if len(r) < 1:
            return None
        base_el = r[0]
        for rms in base_el.xpath('//script'):
            rms.getparent().remove(rms)
        content_list = []
        for child_el in base_el.getchildren():
            child_ctn = etree.tostring(child_el, pretty_print=True, method="html").decode('utf8')
            content_list.append(child_ctn)
        content = (''.join(content_list)).strip()
        return content

    @property
    def description(self):
        return ''
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(self.content), parser)
        r = tree.xpath('//div[@class="desc"]')
        if len(r) < 1:
            return None
        base_el = r[0]
        content_list = []
        for child_el in base_el.getchildren():
            child_ctn = etree.tostring(child_el, pretty_print=True, method="html").decode('utf8')
            content_list.append(child_ctn)
        content = (''.join(content_list)).strip()
        return content

    @property
    def items(self):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(self.content), parser)
        r = tree.xpath('//div[@class="active item"]')
        if len(r) < 1:
            return []
        items = []
        for item in r:
            content = etree.tostring(item)
            items.append(
                OfferItemContentDispatcher(content, soup=True)
            )
        return items

    @property
    def images(self):
        return []
        # parser = etree.HTMLParser()
        # tree = etree.parse(StringIO(self.content), parser)
        images = []
        base_image_matches = re.search(r'var image_big = "([^"]+)"', self.content)
        if base_image_matches is not None:
            images.append(base_image_matches.group(1))
        images_matches = re.search(r'var photos_big = \[([^\]]+)\];', self.content)
        if images_matches is not None:
            images += re.findall(r"'([^']+)',", images_matches.group(1).strip())
        return images

    @property
    def expiration_date(self):
        ptrn = r'<div class="goTimer countdown-timer time" data-ts="([\d]+)"></div>'
        value = self.get_value_by_re(ptrn)
        if value is None:
            return None
        ts = time.time()
        return datetime.fromtimestamp(ts + int(value), tz=timezone.utc)

    @property
    def tags(self):
        tags = []
        tags.append(TagContentDispatcher(content=''))
        return tags

    @property
    def places(self):
        deal_body = self.soup\
            .find(class_='deal-body-wide-map__addresses')\
            .find_all(class_='deal-body-map__address-item')
        places = []
        for tag in deal_body:
            places.append(PlaceContentDispatcher(str(tag), soup=True))
        return places


class ContentProvider:
    @staticmethod
    @contract
    def get_offer_structure(content: str, url: str) -> OfferEntity:
        offer = OfferContentDispatcher(content, soup=True)

        offer_merchant = MerchantContentDispatcher(content)
        merchant = MerchantEntity(
            name=offer_merchant.name
        )

        currency_entity = CurrencyEntity('RUB')

        items = []
        for item in offer.items:
            amount = None
            if item.amount is not None:
                amount = MoneyEntity(item.amount, currency_entity)
            print(item.url)
            print(item.title)
            print(item.amount)
            print(item.price)
            print(item.discount)
            items.append(OfferItemEntity(
                url=item.url,
                title=item.title,
                amount=amount,
                price=MoneyEntity(item.price, currency_entity),
                discount=item.discount
            ))

        places = []
        for place in offer.places:
            places.append(PlaceEntity(
                address=place.address,
                phones=place.phones,
                latitude=place.latitude,
                longitude=place.longitude
            ))

        tags = []
        for tag in offer.tags:
            tags.append(TagEntity(
                title=tag.title
            ))

        offer_entity = OfferEntity(
            url=url,
            title=offer.title,
            rules=offer.rules,
            description=offer.description,
            items=items,
            tags=tags,
            places=places,
            merchant=merchant
        )

        return offer_entity
