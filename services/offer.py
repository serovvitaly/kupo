from contracts import contract, new_contract

OfferItemEntityContract = new_contract('OfferItemEntityContract', 'isinstance(OfferItemEntity)')
TagEntityContract = new_contract('TagEntityContract', 'isinstance(TagEntity)')
PlaceEntityContract = new_contract('PlaceEntityContract', 'isinstance(PlaceEntity)')
CurrencyEntityContract = new_contract('CurrencyEntityContract', 'isinstance(CurrencyEntity)')
MoneyEntityContract = new_contract('MoneyEntityContract', 'isinstance(MoneyEntity)')
CurrencyCodeContract = new_contract('CurrencyCodeContract', lambda s: isinstance(s, str) and len(s) == 3)


class CurrencyEntity:
    @contract
    def __init__(self, code: CurrencyCodeContract):
        self.code = code.upper()


class MoneyEntity:
    @contract
    def __init__(self, value: float, currency: CurrencyEntityContract):
        self.value = value
        self.currency = currency


class MerchantEntity:
    @contract
    def __init__(self, name: str):
        self.name = name


class OfferItemEntity:
    @contract
    def __init__(self, url: str, title: str, amount: MoneyEntityContract, price: MoneyEntityContract, discount: float):
        self.url = url
        self.title = title
        self.amount = amount
        self.price = price
        self.discount = discount


class TagEntity:
    @contract
    def __init__(self, title: str):
        self.title = title


class PlaceEntity:
    @contract
    def __init__(self, title: str):
        self.title = title


class OfferEntity:
    @contract
    def __init__(self, url: str, title: str, rules: str, description: str, items, tags, places):
        """
        :type items: list[>0](OfferItemEntityContract)
        :type tags: list[>0](TagEntityContract)
        :type places: list[>0](PlaceEntityContract)
        """
        self.url = url.strip()
        self.title = title.strip()
        self.rules = rules.strip()
        self.description = description.strip()
        self.items = items
        self.tags = tags
        self.places = places
