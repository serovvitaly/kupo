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
from urllib.parse import urlparse

BASE_URL = 'https://kupikupon.ru'


class ContentDispatcher:
    def __init__(self, content, soup=False):
        self.content = str(content)
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


class ImageContentDispatcher(ContentDispatcher):
    @property
    def src(self):
        src = self.get_value_by_re(r'src="([^"]+?)"')
        return str(src).strip()

    @property
    def alt(self):
        src = self.get_value_by_re(r'alt="([^"]+?)"')
        return str(src).strip()


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
        parts = self.soup.find(class_='adrtab t').contents
        if len(parts) < 1:
            return None
        phones = []
        parts = parts[0].split('\r\n')
        for part in parts:
            part = re.findall(r'([\d+])', part)
            phones.append(int(''.join(part)))
        return phones

    @property
    def work_times(self):
        work_times = self.soup.find(class_='adrtab c').contents
        if len(work_times) < 1:
            return None
        return work_times[0].strip()

    @property
    def latitude(self):
        return None

    @property
    def longitude(self):
        return None


class OfferItemContentDispatcher(ContentDispatcher):
    @property
    def url(self):
        url = self.soup.form['action']
        return url.strip()

    @property
    def title(self):
        contents = []
        for content in self.soup.find(class_='side-info').p.contents:
            contents.append(content.string)
        title = ''.join(contents).strip()
        return title

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
        parts = re.findall(r'([\d+])', price[0])
        if len(parts) < 1:
            return None
        price = ''.join(parts)
        return float(price)

    @property
    def discount(self):
        content = self.soup.find(class_='side-info').p.span.string
        discount = self.get_value_by_re(r'([\d]+)', content=content)
        return float(discount)


class OfferContentDispatcher(ContentDispatcher):
    @property
    def title(self):
        contents = []
        for content in self.soup.find(itemprop='name').p.contents:
            contents.append(content.string)
        title = ''.join(contents).strip()
        return title

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
        imgs = self.soup.find(class_='deal_logo_wrapper').find_all('img')
        if len(imgs) < 1:
            return []
        images = []
        for img in imgs:
            images.append(
                ImageContentDispatcher(img)
            )
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

    def get_entry_point_url(self):
        return ''

    @staticmethod
    @contract
    def get_entry_urls(content: str):
        ptrn = r'<a href="([^"]+?)" class="role-change_category" data-id="[\d]+" data-parent-id="[\d]+" ' \
               r'id="category_[\d]+"><span class="name">[^<]+?</span>[\s]*<span class="counter">[\d]+</span>[' \
               r'\s]*</a>'
        res = re.findall(ptrn, content)
        return res

    @staticmethod
    @contract
    def get_offers_urls(content: str) -> 'list(str)':
        res = re.findall(r'<a class="deal-link" href="([^"]+?)"', content)
        return res

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
            price = None
            if item.price is not None:
                price = MoneyEntity(item.price, currency_entity)
            items.append(OfferItemEntity(
                url=BASE_URL+item.url,
                title=item.title,
                amount=amount,
                price=price,
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

        images = []
        for image in offer.images:
            images.append(ImageEntity(
                url=BASE_URL+image.src
            ))

        tags = []
        for tag in offer.tags:
            tags.append(TagEntity(
                title=tag.title
            ))

        url_parts = urlparse(url)
        offer_url = BASE_URL + url_parts.path

        offer_entity = OfferEntity(
            url=offer_url,
            title=offer.title,
            rules=offer.rules,
            description=offer.description,
            items=items,
            images=images,
            tags=tags,
            places=places,
            merchant=merchant
        )

        return offer_entity
