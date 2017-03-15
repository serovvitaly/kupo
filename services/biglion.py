from models.base import AbstractOffer, AbstractProvider
import re


class Offer(AbstractOffer):
    pass


class Provider(AbstractProvider):

    def get_total_pages(self, content):
        """
        Возвращает количество страниц в разделе, найденные в контенте
        """
        matches = re.findall(r'<a href="/services/\?page=([\d]+)" data-id="[\d]+">[\d]+</a>', content)
        if matches is None:
            return None

        print(max(matches))
        #return int(matches.group(1))

    def get_urls_from_content(self, content):
        """
        Возвращает массив ссылок на записи, найденных в контенте
        """
        pass

    def get_all_urls(self):
        first_page_url = 'http://www.biglion.ru/services/'
        first_page_content = self.get_content_by_url(first_page_url)
        total_pages = self.get_total_pages(first_page_content)
        print(total_pages)

    def all(self):

        items = self.get_all_urls()

        offers = []
        offers.append(Offer())
        offers.append(Offer())
        return offers
