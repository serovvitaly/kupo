import re
import pickle
import datetime
import urllib.request

from xml.dom import minidom
from urllib.parse import urlparse
from models.base import AbstractOffer, AbstractProvider
from pymemcache.client.base import Client as MemClient
from services.provider.biglion.content_dispatcher import ContentDispatcher

mem_client = MemClient(('localhost', 11211))


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
