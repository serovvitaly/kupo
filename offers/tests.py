from django.test import TestCase
from services.repository import *
from services.parser import Parser


class OfferEntityTestCase(TestCase):

    def setUp(self):
        pass

    def test_get_cats(self):
        urls = Parser.get_provider_urls('kupikupon', 'https://kupikupon.ru')
        self.assertIsInstance(urls, list)

    def test_constructor(self):
        html_repository = HtmlOfferRepository('kupikupon')
        offer_entity = html_repository.get_by_url('https://kupikupon.ru/deals/cafe-begemot-271652')
        print(offer_entity.title)
        #offer_entity = html_repository.get_by_url('https://kupikupon.ru/deals/more-on-269730')
        #offer_entity = html_repository.get_by_url('https://kupikupon.ru/deals/manikyur-i-pedikyur-267923')
        #sql_repository = SqlOfferRepository()
        #sql_repository.add(offer_entity)
