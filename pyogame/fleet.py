import logging
import datetime
import dateutil.parser
from uuid import uuid4

from pyogame.ships import Ships
from pyogame.tools.common import Collection

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
    def load(cls, **kwargs):
        ships_types = kwargs.pop('ships')
        fleet = cls(**kwargs)
        for ships in ships_types:
            fleet.add(**ships)
        return fleet

    def dump(self):
        return {'ships': [ships.dump() for ships in self._ships.values()]}

    def __len__(self):
        return sum([ships.quantity for ships in self])

    def __repr__(self):
        return repr(','.join([repr(ships) for ships in self]))


class FlyingFleet(Fleet):

    def __init__(self, src, dst, travel_id=None,
            arrival_time=None, return_time=None):
        super(FlyingFleet, self).__init__()
        self.src = src
        self.dst = dst
        self.travel_id = travel_id if travel_id is not None else str(uuid4())
        if arrival_time is not None \
                and not isinstance(arrival_time, datetime.datetime):
            arrival_time = dateutil.parser.parse(arrival_time)
        if return_time is not None \
                and not isinstance(return_time, datetime.datetime):
            return_time = dateutil.parser.parse(return_time)
        self.arrival_time = arrival_time
        self.return_time = return_time

    @property
    def is_arrived(self):
        return self.arrival_time < datetime.datetime.now()

    @property
    def is_returned(self):
        return self.return_time < datetime.datetime.now()

    def dump(self):
        dump = super(FlyingFleet, self).dump()
        dump.update({'travel_id': self.travel_id,
                'src': self.dst, 'arrival_time': self.arrival_time,
                'dst': self.src, 'return_time': self.return_time,
        })
        return dump

    def __repr__(self):
        return r'<Fleet %s (%r->%r)>' % (self.travel_id.split('-', 1)[0],
                self.src, self.dst)


class Missions(Collection):

    def __init__(self):
        self.missions = {}
        super(Missions, self).__init__(self.missions)

    def add(self, fleet=None, **kwargs):
        if fleet is None or not isinstance(fleet, Fleet):
            fleet = FlyingFleet(**kwargs)
        self.missions[fleet.travel_id] = fleet
        return fleet.travel_id

    def clean(self, awaited_travel=[]):
        to_dels = []
        for fleet in self.returned:
            if not fleet.travel_id in awaited_travel:
                to_dels.append(fleet)
        for fleet in to_dels:
            self.missions.pop(fleet.travel_id)

    @property
    def arrived(self):
        return self._filter(is_arrived=True)

    @property
    def returned(self):
        return self._filter(is_returned=True)

    @classmethod
    def load(cls, **kwargs):
        missions = cls()
        for mission in kwargs['missions']:
            missions.add(FlyingFleet.load(**mission))
        return missions

    def dump(self):
        return {'missions': [fleet.dump() for fleet in self]}
