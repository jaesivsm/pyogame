import logging

from pyogame.ships import SHIPS_TYPES, Ships

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

    def add(self, ships_id=0, ships=None, *args, **kwargs):
        if ships is None:
            ships_type = SHIPS_TYPES.get(ships_id, Ships)
            ships = ships_type(ships_id, *args, **kwargs)
        if isinstance(ships, Ships) and ships.quantity:
            if not ships.ships_id in self._ships:
                self._ships[ships.ships_id] = ships.copy()
            else:
                self._ships[ships.ships_id].quantity += ships.quantity

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

    def __len__(self):
        return sum([ships.quantity for ships in self])

    def __repr__(self):
        return repr(','.join([repr(ships) for ships in self]))
