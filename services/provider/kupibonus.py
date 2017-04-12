"""
http://www.kupibonus.ru/
"""

import re
import pickle
import time
from datetime import datetime, timezone
import urllib.request
from xml.dom import minidom
from urllib.parse import urlparse
from models.base import AbstractOffer, AbstractProvider
import lxml.etree as etree
from io import StringIO
from bs4 import BeautifulSoup

from pymemcache.client.base import Client as MemClient

mem_client = MemClient(('localhost', 11211))


class TagContentDispatcher:

    def __init__(self, content):
        self.content = content
        self.title = ''


class PlaceContentDispatcher:

    def __init__(self, content):
        self.content = content
        self.title = ''


class OfferItemContentDispatcher:
    def get_value_by_re(self, pattern):
        ms = re.search(pattern, self.content)
        if ms is None:
            return None
        st = ms.group(1).strip()
        if st == '':
            return None
        return st

    def __init__(self, content):
        self.content = content
        self.title = self.get_title()

    def get_title(self):
        ptrn = r'<h1 itemprop="name">([\s\S]+?)</h1>'
        return self.get_value_by_re(ptrn)


class OfferContentDispatcher:
    def __init__(self, content):
        self.content = content
        self.title = self.get_title()
        self.rules = self.get_rules()
        self.description = self.get_description()
        self.items = self.get_items()
        self.tags = self.get_tags()
        self.places = self.get_places()

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

    def get_values_by_re(self, pattern):
        ms = re.search(pattern, self.content)
        if ms is None:
            return None
        return ms.groups()

    def get_title(self):
        ptrn = r'<h1 itemprop="name">([\s\S]+?)</h1>'
        return self.get_value_by_re(ptrn)

    def get_likes_count(self):
        ptrn = r'<div class="heart default unregistered biglionHeart" data-deal-id="[\d]+" data-like-qnt="([\d]+?)">'
        count = self.get_value_by_re(ptrn)
        if count is None:
            return None
        return int(count)

    def get_purchases_count(self):
        ptrn = r'<div style="background: none; background-position: [^"]+">([\d]+?)<span>'
        count = self.get_value_by_re(ptrn)
        if count is None:
            return None
        return int(count)

    def get_rules(self):
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

    def get_description(self):
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

    def get_coupon_expiration_date(self):
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

    def get_coupon_beginning_usage_date(self):
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

    def get_items(self):
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
            items_list.append(OfferItemContentDispatcher(content=item_content.__str__()))
        return items_list

    def get_images(self):
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

    def get_expiration_date(self):
        ptrn = r'<div class="goTimer countdown-timer time" data-ts="([\d]+)"></div>'
        value = self.get_value_by_re(ptrn)
        if value is None:
            return None
        ts = time.time()
        return datetime.fromtimestamp(ts + int(value), tz=timezone.utc)

    def get_tags(self):
        tags = []
        tags.append(TagContentDispatcher(content=''))
        return tags

    def get_places(self):
        places = []
        places.append(PlaceContentDispatcher(content=''))
        return places


class Offer(AbstractOffer):
    pass


class ContentProvider(AbstractProvider):
    def get_urls(self):
        """
        Парсит XML фид, и возвращает список найденных url
        """
        url = 'http://api.biglion.ru/api.php?method=get_torg_price&type=xml&ctype=all'
        cache = mem_client.get(url)
        if cache is not None:
            print('Loading from cache...')
            return pickle.loads(cache)
        print('Loading from net...')
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as f:
            print('Parsing...')
            xml_str = f.read().decode('utf-8')
            xmldoc = minidom.parseString(xml_str)
            urls_nodels_list = xmldoc.getElementsByTagName('url')
            print('Received', len(urls_nodels_list), 'items')
            urls_str = []
            for url_node in urls_nodels_list:
                urls_str.append(url_node.firstChild.nodeValue.strip())
            cache = mem_client.set(url, pickle.dumps(urls_str), 60 * 60)
            return urls_str

    def get_total_pages(self, content):
        """
        Возвращает количество страниц в разделе, найденные в контенте
        """
        mms = re.search(r'<div class="page_pavigation">([\s\S]+?)</div>', content)
        if mms is None:
            return None
        matches = re.findall(r'<a href="/[^"]+/\?page=([\d]+)" data-id="[\d]+">[\d]+</a>', mms.group(1))
        if matches is None:
            return None
        matches = map(int, matches)
        return max(matches)

    def get_urls_list(self, content):
        ptrn = 'href="(http://www.biglion.ru/deals/[^"]+)"'
        matches = re.findall(ptrn, content)
        return matches

    def get_urls_from_content(self, content):
        """
        Возвращает массив ссылок на записи, найденных в контенте
        """
        pass

    def fill_offer_from_content(self, offer, content):
        """
        Заполняет данными объект оффера, на основе полученного контента
        """
        content_dispatcher = OfferContentDispatcher(content)
        offer.title = content_dispatcher.get_title()
        offer.likes_count = content_dispatcher.get_likes_count()
        offer.purchases_count = content_dispatcher.get_purchases_count()
        offer.rules = content_dispatcher.get_rules()

    def get_list_page_structure(self, content):
        structure = type('offer_structure', (object,), {})()
        structure.total_pages = self.get_total_pages(content)
        structure.urls_list = self.get_urls_list(content)
        return structure

    def get_offer_structure(self, content):
        return OfferContentDispatcher(content)

    def all(self):
        urls = self.get_urls()
        if urls is None:
            return None
        offers = []
        for url in urls:
            up = urlparse(url)
            if up.netloc != '':
                continue
            if up.path == '':
                continue
            print(url)
            content = self.get_content_by_url(url)
            offer = Offer()
            offer.url = url
            offer.revision_at = datetime.now()
            self.fill_offer_from_content(offer, content)
            offers.append(offer)
        if len(offers) < 1:
            return None
        return offers
