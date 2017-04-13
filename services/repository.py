from abc import ABCMeta, abstractmethod
from services.offer import *
from contracts import contract
from services.parser import Parser


class OfferRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_by_url(self, url: str) -> OfferEntity:
        pass

    @abstractmethod
    def add(self, offer_entity: OfferEntity):
        pass


class SqlOfferRepository(OfferRepository):
    @contract
    def add(self, offer_entity: OfferEntity):
        return self

    @contract
    def get_by_url(self, url: str) -> OfferEntity:
        pass


class HtmlOfferRepository(OfferRepository):
    @contract
    def add(self, offer_entity: OfferEntity):
        return self

    @contract
    def get_by_url(self, url: str) -> OfferEntity:
        parser = Parser('kupibonus')
        return parser.get_offer_entity_by_url(url)


class MemcacheOfferRepository(OfferRepository):
    @contract
    def add(self, offer_entity: OfferEntity):
        pass

    @contract
    def get_by_url(self, url: str) -> OfferEntity:
        pass
