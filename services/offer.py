from contracts import contract, new_contract

new_contract('OfferItemEntityContract', 'isinstance(OfferItemEntity)')
new_contract('TagEntityContract', 'isinstance(TagEntity)')
new_contract('PlaceEntityContract', 'isinstance(PlaceEntity)')


class OfferItemEntity:

    def __init__(self, title=None):
        self.title = title


class TagEntity:

    def __init__(self, title=None):
        self.title = title


class PlaceEntity:

    def __init__(self, title=None):
        self.title = title


class OfferEntity:

    @contract
    def __init__(self, title=None, rules=None, description=None, items=None, tags=None, places=[]):
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
        self.places = []
        for place in places:
            self.place_append(place)

    def place_append(self, place):
        if isinstance(place, PlaceEntity) is False:
            raise Exception('Object is not a PlaceEntity')
        self.places.append(place)
        return self
