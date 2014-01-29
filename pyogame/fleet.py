import logging

logger = logging.getLogger(__name__)


class Ships(object):
    single_ship_capacity = 0
    are_transport = False

    def __init__(self, name=None, quantity=0):
        self.name = name
        self.quantity = quantity

    @property
    def capacity(self):
        return self.quantity * self.single_ship_capacity

    def copy(self):
        return self.__class__(self.name, self.quantity)

    def __repr__(self):
        if self.name:
            return r"<%s(%d)>" % (self.name, self.quantity)
        return "<Unknown Ships(%d)>" % self.quantity

    def __len__(self):
        return self.quantity


class PTs(Ships):
    u'Petit transporteur'
    single_ship_capacity = 5000
    are_transport = True


class GTs(Ships):
    u'Grand transporteur'
    single_ship_capacity = 25000
    are_transport = True


SHIP_TYPES = {'Grand transporteur': GTs,
        'Petit transporteur': PTs,
        'Recycleur': Ships,
        'Sonde d`espionnage': Ships,
        'Vaisseau de colonisation': Ships,
        'Bombardier': Ships,
        'Chasseur lourd': Ships,
        'Chasseur l\xc3\xa9ger': Ships,
        'Croiseur': Ships,
        'Destructeur': Ships,
        'Traqueur': Ships,
        'Vaisseau de bataille': Ships,
        '\xc3\x89toile de la mort': Ships,
}


class Fleet(object):

    def __init__(self):
        self._ships = {}

    def __iter__(self):
        return iter(self._ships.values())

    @property
    def capacity(self):
        return sum([ships.capacity for ships in self])

    @property
    def transports(self):
        fleet = Fleet()
        for ships in self:
            if ships.are_transport:
                fleet.add(ships=ships)
        return fleet

    def add(self, ships_name='', quantity=0, ships=None):
        if ships_name and quantity:
            ships = SHIP_TYPES.get(ships_name, Ships)(ships_name, quantity)
        elif isinstance(ships, Ships):
            ships = ships.copy()  # avoid stacking
        if isinstance(ships, Ships) and ships.quantity:
            if not ships.name in self._ships:
                self._ships[ships.name] = ships
            else:
                self._ships[ships.name].quantity += ships.quantity

    def __len__(self):
        return sum([ships.quantity for ships in self])

    def __repr__(self):
        return repr(','.join([repr(ships) for ships in self]))
