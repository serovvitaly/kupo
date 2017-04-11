
class PlaceEntity:

    def __init__(self):
        pass


class OfferEntity:

    def __init__(self, title=None, rules=None, description=None, items=None, tags=None, places=[]):
        self.title = title
        self.rules = rules
        self.description = description
        self.items = items
        self.tags = tags
        self.places = places
        for place in places:
            self.place_append(place)

    def place_append(self, place):
        if isinstance(place, PlaceEntity) is False:
            assert Exception('Foo')
        self.places.append(place)
        return self
