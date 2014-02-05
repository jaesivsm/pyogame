import logging

from pyogame.ships import Ships

logger = logging.getLogger(__name__)


class Fleet(object):

    def __init__(self):
        self._ships = {}
        self.clear = self._ships.clear

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

    def add(self, ships_id=0, ships=None, **kwargs):
        if ships is None:
            ships = Ships.load(ships_id=ships_id, **kwargs)
        if isinstance(ships, Ships) and ships.quantity:
            if not ships.ships_id in self._ships:
                self._ships[ships.ships_id] = ships.copy()
            else:
                self._ships[ships.ships_id].quantity += ships.quantity

    def remove(self, ships_id=0, ships=None, **kwargs):
        if ships is None:
            ships = self.__class__.load(ships_id=ships_id, **kwargs)
        if ships.quantity:
            self._ships[ships.ships_id].quantity -= ships.quantity
        if self._ships[ships.ships_id].quantity <= 0:
            del self._ships[ships.ships_id]

    def for_moving(self, quantity):
        fleet, tmp_quantity = Fleet(), quantity
        assert self.capacity >= quantity, 'Too many resources (%r) for fleet' \
                ' %r with capacity %r' % (quantity, self, self.capacity)
        cmp_func = lambda x,y: cmp(x.capacity, y.capacity)
        for ships in sorted(self, cmp=cmp_func, reverse=True):
            ships = ships.copy()
            if ships.capacity >= tmp_quantity:
                nb_ships = tmp_quantity / ships.single_ship_capacity
                if tmp_quantity % ships.single_ship_capacity:
                    nb_ships += 1
                ships.quantity = nb_ships
                fleet.add(ships=ships)
                return fleet
            fleet.add(ships=ships)
            tmp_quantity -= ships.capacity

    @classmethod
    def load(cls, *args):
        fleet = cls()
        for ships in args:
            fleet.add(**ships)
        return fleet

    def dump(self):
        return [ships.dump() for ships in self._ships.values()]

    def __len__(self):
        return sum([ships.quantity for ships in self])

    def __repr__(self):
        return repr(','.join([repr(ships) for ships in self]))


class FlyingFleet(Fleet):

    def __init__(self, from_pl, to_pl, arrival_time=None, return_time=None):
        super(FlyingFleet, self).__init__()
        self.from_pl = from_pl
        self.to_pl = to_pl
        self.arrival_time = arrival_time
        self.return_time = return_time

    def __repr__(self):
        return r'<Fleet (%r->%r)>' % (self.from_pl, self.to_pl)
