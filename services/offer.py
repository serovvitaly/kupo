from contracts import contract, new_contract

new_contract('OfferItemEntityContract', 'isinstance(OfferItemEntity)')
new_contract('TagEntityContract', 'isinstance(TagEntity)')
new_contract('PlaceEntityContract', 'isinstance(PlaceEntity)')
new_contract('CurrencyEntityContract', 'isinstance(CurrencyEntity)')
new_contract('MoneyEntityContract', 'isinstance(MoneyEntity)')
new_contract('CurrencyCodeContract', lambda s: isinstance(s, str) and len(s) == 3)


class CurrencyEntity:
    @contract
    def __init__(self, code):
        """
        :type code: CurrencyCodeContract
        """
        self.code = code.upper()


class MoneyEntity:
    @contract
    def __init__(self, value, currency):
        """
        :type value: float
        :type currency: CurrencyEntityContract
        """
        self.value = value
        self.currency = currency


class MerchantEntity:
    @contract
    def __init__(self, name):
        """
        :type name: str
        """
        self.name = name


class OfferItemEntity:
    @contract
    def __init__(self, url, title, amount, price, discount):
        """
        :type url: str
        :type title: str
        :type amount: MoneyEntityContract
        :type price: MoneyEntityContract
        :type discount: float
        """
        self.url = url
        self.title = title
        self.amount = amount
        self.price = price
        self.discount = discount


class TagEntity:
    @contract
    def __init__(self, title=None):
        """
        :type title: str
        """
        self.title = title


class PlaceEntity:
    @contract
    def __init__(self, title=None):
        """
        :type title: str
        """
        self.title = title


class OfferEntity:
    @contract
    def __init__(self, title, rules, description, items, tags, places):
        """
        :type title: str
        :type rules: str
        :type description: str
        :type items: list[>0](OfferItemEntityContract)
        :type tags: list[>0](TagEntityContract)
        :type places: list[>0](PlaceEntityContract)
        """
        self.title = title
        self.rules = rules
        self.description = description
        self.items = items
        self.tags = tags
        self.places = places
