from django.test import TestCase
from services.offer import OfferEntity
from services.parser import Parser


class OfferEntityTestCase(TestCase):

    def setUp(self):
        pass

    def validate_structure(self, offer_entity):
        pass

    def test_constructor(self):
        return
        offer_entity = OfferEntity()
        attributes = ['title','rules','description','items','tags','places',]
        for attr in attributes:
            self.assertTrue(hasattr(offer_entity, attr), 'OfferEntity not has attribute: ' + attr)
            self.assertTrue(getattr(offer_entity, attr) is not None, 'OfferEntity attribute is None: ' + attr)

    def test_constructor2(self):
        parser = Parser('kupibonus')
        offer_entity = parser.get_offer_entity_by_url('http://www.kupibonus.ru/actions/spa/den-razvlecheniy-v-akvap/')
        self.assertTrue(isinstance(offer_entity, OfferEntity), 'Result is not OfferEntity')
