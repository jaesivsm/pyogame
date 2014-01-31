import logging

logger = logging.getLogger(__name__)


class Ships(object):
    single_ship_capacity = 0
    are_transport = False
    xpath = None
    ship_id = None

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
    'Petit transporteur'
    single_ship_capacity = 5000
    are_transport = True
    xpath = "//ul[@id='civil']/li[1]/div/a"
    ship_id = "ship_202"


class GTs(Ships):
    'Grand transporteur'
    single_ship_capacity = 25000
    are_transport = True
    xpath = "//ul[@id='civil']/li[2]/div/a"
    ship_id = "ship_203"


SHIPS_TYPES = {'grand transporteur': GTs,
        'petit transporteur': PTs,
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
            ships_type = SHIPS_TYPES.get(ships_name.lower(), Ships)
            ships = ships_type(ships_name, quantity)
        if isinstance(ships, Ships) and ships.quantity:
            if not ships.name.lower() in self._ships:
                self._ships[ships.name.lower()] = ships.copy()
            else:
                self._ships[ships.name.lower()].quantity += ships.quantity

    def for_moving(self, quantity):
        fleet, tmp_quantity = Fleet(), quantity
        assert self.capacity >= quantity, 'Too many resources (%r) " \
                "for fleet %r' % (quantity, self)
        cmp_func = lambda x,y: cmp(x.capacity, y.capacity)
        for ships in sorted(self, cmp=cmp_func, reverse=True):
            if ships.capacity >= tmp_quantity:
                nb_ships = tmp_quantity / ships.single_ship_capacity
                if tmp_quantity % ships.single_ship_capacity:
                    nb_ships += 1
                fleet.add(ships.name, nb_ships)
                return fleet
            fleet.add(ships=ships)
            tmp_quantity -= ships.capacity

    def __len__(self):
        return sum([ships.quantity for ships in self])

    def __repr__(self):
        return repr(','.join([repr(ships) for ships in self]))
