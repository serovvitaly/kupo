from services.provider.biglion.biglion import Provider, Offer
from urllib.parse import urlparse


class Parser:

    def __init__(self):
        pass

    def fill_offer_by_url(self, offer, url):
        content_provider = Provider()
        content = content_provider.get_content_by_url(url)
        content_provider.fill_offer_from_content(offer, content)


    def execute(self):
        content_provider = Provider()
        """
        Получаем список URL для загрузки контента
        """
        urls_list = content_provider.get_urls()
        if (urls_list is None) or (len(urls_list) < 1):
            return
        """
        Обходим этот список, и получаем данные для каждой страницы
        """
        for url in urls_list[0:2]:
            up = urlparse(url)
            if up.netloc != 'www.biglion.ru':
                continue
            if up.path == '':
                continue
            offer = Offer()
            offer.url = url
            self.fill_offer_by_url(offer, url)
            print(offer.url)
            print(offer.title)
