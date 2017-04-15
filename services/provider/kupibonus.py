"""
http://www.kupibonus.ru/
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
    def __init__(self, content):
        self.content = content

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
    def name(self):
        return self.content['name'].strip()

    @property
    def address(self):
        return self.content['address'].strip()

    @property
    def phones(self):
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
        ptrn = r'class="kb-deal certificate" href="([^"]+?)"'
        return str(self.get_value_by_re(ptrn)).strip()

    @property
    def title(self):
        ptrn = r'<div class="kb-name">([\s\S]+?)</div>'
        return str(self.get_value_by_re(ptrn)).strip()

    @property
    def amount(self):
        ptrn = r'<div class="kb-price"><span>([\s\d]+?)</span> [\w]+</div>'
        value = str(self.get_value_by_re(ptrn)).replace(' ', '')
        return float(value)

    @property
    def price(self):
        ptrn = r'<td><span class="kb-h">Стоимость:</span></td>[\s]*<td>[\s]*<span>([\s\d]+?)</span> [\w]+[\s]*</td>'
        value = str(self.get_value_by_re(ptrn)).replace(' ', '')
        return float(value)

    @property
    def discount(self):
        ptrn = r'<td><span class="kb-h">Скидка:</span></td><td> ([\d]+?)\%</td>'
        value = str(self.get_value_by_re(ptrn)).replace(' ', '')
        return float(value)


class OfferContentDispatcher(ContentDispatcher):
    @property
    def title(self):
        ptrn = r'<h1 itemprop="name">([\s\S]+?)</h1>'
        return self.get_value_by_re(ptrn)

    @property
    def likes_count(self):
        ptrn = r'<div class="heart default unregistered biglionHeart" data-deal-id="[\d]+" data-like-qnt="([\d]+?)">'
        count = self.get_value_by_re(ptrn)
        if count is None:
            return None
        return int(count)

    @property
    def purchases_count(self):
        ptrn = r'<div style="background: none; background-position: [^"]+">([\d]+?)<span>'
        count = self.get_value_by_re(ptrn)
        if count is None:
            return None
        return int(count)

    @property
    def rules(self):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(self.content), parser)
        r = tree.xpath('//div[@class="desc"]')
        if len(r) < 1:
            return None
        base_el = r[0]
        for rms in base_el.xpath('//script'):
            rms.getparent().remove(rms)
        for rms in base_el.xpath('//div[@class="terms_subheader"]'):
            rms.getparent().remove(rms)
        for rms in base_el.xpath('//div[@class="reviews_terms_view"]'):
            rms.getparent().remove(rms)
        for rms in base_el.xpath('//div[@class="forum-load hidden"]'):
            rms.getparent().remove(rms)
        for rms in base_el.xpath('//table[@style="border: none;width: 100%;"]'):
            rms.getparent().remove(rms)
        content_list = []
        for child_el in base_el.getchildren():
            child_ctn = etree.tostring(child_el, pretty_print=True, method="html").decode('utf8')
            content_list.append(child_ctn)
        content = (''.join(content_list)).strip()
        return content

    @property
    def description(self):
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
    def coupon_expiration_date(self):
        ptrn = r'<li>Купон действует <span style="font-weight: bold;">до&nbsp;([\d]+)\.([\d]+)\.([\d]+)</span></li>'
        values = self.get_values_by_re(ptrn)
        if values is None:
            return None
        return datetime(
            day=int(values[0]),
            month=int(values[1]),
            year=int(values[2]),
            tzinfo=timezone.utc
        )

    @property
    def coupon_beginning_usage_date(self):
        ptrn = r'<li class="important"><span>Купон можно использовать с ([\d]+)\.([\d]+)\.([\d]+). </span></li>'
        values = self.get_values_by_re(ptrn)
        if values is None:
            return None
        return datetime(
            day=int(values[0]),
            month=int(values[1]),
            year=int(values[2]),
            tzinfo=timezone.utc
        )

    @property
    def items(self):
        val = self.get_value_by_re(r'<div class="kb-pr-m fr">[\s]+<script type="text/javascript">([\s\S]+?)</script>')
        val = self.get_value_by_re(r'\'content\' : \'([\s\S]+?)<div id=\\"kb-arrow\\"', content=val)
        val = val.replace("\\n'+\n'", '\n')
        val = val.replace('\\"', '"')
        soup = BeautifulSoup(val, 'html.parser')
        items = soup.find_all(class_='kb-block-out')
        if len(items) < 1:
            return []
        items_list = []
        for item_content in items:
            item = OfferItemContentDispatcher(content=item_content.__str__())
            items_list.append(item)
        return items_list

    @property
    def images(self):
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
        ptrn = r"var places = ([\s\S]+?);"
        value = self.get_value_by_re(ptrn)
        value = value.replace("'", '"')
        values = json.loads(value)
        if isinstance(values, list) is False:
            return []
        places = []
        for data in values:
            places.append(PlaceContentDispatcher(content=data))
        return places


class ContentProvider:
    @staticmethod
    @contract
    def get_offer_structure(content: str, url: str) -> OfferEntity:
        offer = OfferContentDispatcher(content)
        offer_merchant = MerchantContentDispatcher(content)
        merchant = MerchantEntity(
            name=offer_merchant.name
        )

        currency_entity = CurrencyEntity('RUB')

        items = []
        for item in offer.items:
            items.append(OfferItemEntity(
                url=item.url,
                title=item.title,
                amount=MoneyEntity(item.amount, currency_entity),
                price=MoneyEntity(item.price, currency_entity),
                discount=item.discount
            ))

        places = []
        for place in offer.places:
            places.append(PlaceEntity(
                title=place.name,
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

