from abc import ABCMeta, abstractmethod
from services.offer import *
from contracts import contract
from services.parser import Parser
from offers.models import *
from django.db import transaction, connection


class OfferRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_by_url(self, url: str) -> OfferEntity:
        pass

    @abstractmethod
    def add(self, offer_entity: OfferEntity):
        pass


class SqlOfferRepository(OfferRepository):
    # @contract
    def add(self, offer_entity):

        with transaction.atomic():

            merchant = MerchantModel()
            merchant.name = offer_entity.merchant.name
            merchant.save()

            offer = Offer(merchant=merchant)
            offer.url = offer_entity.url
            offer.title = offer_entity.title
            offer.rules = offer_entity.rules
            offer.description = offer_entity.description
            offer.save()

            for item in offer_entity.items:
                amount = None
                if item.amount is not None:
                    amount = item.amount.value
                price = None
                if item.price is not None:
                    price = item.price.value
                offer_item = OfferItemModel(offer=offer)
                offer_item.title = item.title
                offer_item.url = item.url
                offer_item.discount = item.discount
                offer_item.price = price
                offer_item.amount = amount
                offer_item.save()

            for place_ent in offer_entity.places:
                place = Place()
                place.offer = offer
                place.merchant = merchant
                place.address = place_ent.address
                place.phones = ','.join(str(phone) for phone in place_ent.phones)
                place.latitude = place_ent.latitude
                place.longitude = place_ent.longitude
                place.save()

        return self

    @contract
    def get_by_url(self, url: str) -> OfferEntity:
        pass


class HtmlOfferRepository(OfferRepository):
    @contract
    def __init__(self, provider_name: str):
        self.set_provider_name(provider_name)

    @contract
    def set_provider_name(self, provider_name: str):
        self.parser = Parser(provider_name)

    @contract
    def add(self, offer_entity: OfferEntity):
        return self

    @contract
    def get_by_url(self, url: str) -> OfferEntity:
        return self.parser.get_offer_entity_by_url(url)


class MemcacheOfferRepository(OfferRepository):
    @contract
    def add(self, offer_entity: OfferEntity):
        pass

    @contract
    def get_by_url(self, url: str) -> OfferEntity:
        pass
