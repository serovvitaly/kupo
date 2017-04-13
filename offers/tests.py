from django.test import TestCase
from services.offer import OfferEntity
from services.parser import Parser
from services.repository import *
from offers.models import *


class OfferEntityTestCase(TestCase):

    def setUp(self):
        pass

    def validate_structure(self, offer_entity):
        pass

    def test_constructor(self):
        html_repository = HtmlOfferRepository()
        sql_repository = SqlOfferRepository()
        offer_entity = html_repository.get_by_url('http://www.kupibonus.ru/actions/spa/den-razvlecheniy-v-akvap/')
        sql_repository.add(offer_entity)
