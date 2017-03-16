"""
frendi.ru
"""

import re
import pickle
import datetime
import urllib.request

from xml.dom import minidom
from urllib.parse import urlparse
from models.base import AbstractOffer, AbstractProvider
from pymemcache.client.base import Client as MemClient

import re
import lxml.etree as etree

from io import StringIO

mem_client = MemClient(('localhost', 11211))





class ContentDispatcher:

    def __init__(self, content):
        self.content = content

    def get_value_by_re(self, pattern):
        ms = re.search(pattern, self.content)
        if ms is None:
            return None
        st = ms.group(1).strip()
        if st == '':
            return None
        return st

    def get_title(self):
        ptrn = r'<h1 class="header" id="headerTitle">([\s\S]+?)</h1>'
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
        r = tree.xpath('//div[@class="multi_text_block multi_text_block1"]/div[@class="terms-load one_multi_text"]')
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


class Offer(AbstractOffer):
    pass


class Provider(AbstractProvider):

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
                cache = mem_client.set(url,  pickle.dumps(urls_str), 60*60)
                return urls_str

    def get_total_pages(self, content):
        """
        Возвращает количество страниц в разделе, найденные в контенте
        """
        matches = re.findall(r'<a href="/services/\?page=([\d]+)" data-id="[\d]+">[\d]+</a>', content)
        if matches is None:
            return None
        matches = map(int, matches)
        print(matches)
        return max(matches)

    def get_urls_from_content(self, content):
        """
        Возвращает массив ссылок на записи, найденных в контенте
        """
        pass

    def fill_offer_from_content(self, offer, content):
        """
        Заполняет данными объект оффера, на основе полученного контента
        """
        content_dispatcher = ContentDispatcher(content)
        offer.title = content_dispatcher.get_title()
        offer.likes_count = content_dispatcher.get_likes_count()
        offer.purchases_count = content_dispatcher.get_purchases_count()
        offer.rules = content_dispatcher.get_rules()

    def all(self):
        urls = self.get_urls()
        if urls is None:
            return None
        offers = []
        for url in urls:
            up = urlparse(url)
            if up.netloc != 'www.biglion.ru':
                continue
            if up.path == '':
                continue
            print(url)
            content = self.get_content_by_url(url)
            offer = Offer()
            offer.url = url
            offer.revision_at = datetime.datetime.now()
            self.fill_offer_from_content(offer, content)
            offers.append(offer)
        if len(offers) < 1:
            return None
        return offers
