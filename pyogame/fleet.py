import logging
import datetime
import dateutil.parser
from uuid import uuid4

from pyogame.ships import Ships
from pyogame.tools.resources import pretty_number
from pyogame.tools.common import coords_to_key
from pyogame.abstract.collections import Collection

logger = logging.getLogger(__name__)


class Fleet(Ships):

    @property
    def capacity(self):
        return sum([ships.capacity for ships in self])

    @property
    def transports(self):
        return self.cond(are_transport=True)

    def for_moving(self, resources):
        fleet, amount = Fleet(), resources.movable.total
        assert self, 'fleet is empty !'
        if self.capacity < amount:
            logger.error('Too many resources (%s) for fleet %r with capacity '
                         '%s', pretty_number(amount), self,
                               pretty_number(self.capacity))
            return self

        def cmp_func(x, y):
            return x.capacity > y.capacity

        for ships in sorted(self, cmp=cmp_func, reverse=True):
            if fleet.capacity > amount:
                break
            ships = ships.copy()
            total_ship = ships.quantity
            ships.quantity = amount / ships.single_ship_capacity
            if ships.quantity > total_ship:
                ships.quantity = total_ship

            quantity_eq_capacity = amount % ships.single_ship_capacity == 0
            is_ship_left = total_ship - ships.quantity > 0
            if quantity_eq_capacity and is_ship_left:
                ships.quantity += 1
            fleet.add(ships=ships)
        return fleet

    def of_type(self, *args):
        fleet = Fleet()
        for ships in self:
            if isinstance(ships, args):
                fleet.add(ships=ships)
        return fleet

    def __len__(self):
        return sum([ships.quantity for ships in self])


class FlyingFleet(Fleet):

    def __init__(self, data, src, dst, flight_type=None, travel_id=None,
            arrival_time=None, return_time=None):
        super().__init__(data)
        self.src = coords_to_key(src)
        self.dst = coords_to_key(dst)
        self.travel_id = travel_id if travel_id is not None else str(uuid4())
        if arrival_time is not None \
                and not isinstance(arrival_time, datetime.datetime):
            arrival_time = dateutil.parser.parse(arrival_time)
        if return_time is not None \
                and not isinstance(return_time, datetime.datetime):
            return_time = dateutil.parser.parse(return_time)
        self.flight_type = flight_type
        self.arrival_time = arrival_time
        self.return_time = return_time

    @property
    def is_arrived(self):
        return self.arrival_time < datetime.datetime.now()

    @property
    def is_returned(self):
        return self.return_time < datetime.datetime.now()

    def dump(self):
        dump = super().dump()
        dump.update({'travel_id': self.travel_id,
                'flight_type': self.flight_type,
                'src': self.src, 'arrival_time': self.arrival_time,
                'dst': self.dst, 'return_time': self.return_time,
        })
        return dump

    def __repr__(self):
        return r'<Fleet %s (%r->%r)>' % (self.travel_id.split('-', 1)[0],
                self.src, self.dst)


class Missions(Collection):

    def add(self, obj):
        self.data[obj.travel_id] = obj
        return obj.travel_id

    def remove(self, obj):
        return self.data.pop(obj.travel_id, None)

    def clean(self, awaited_travel=None):
        awaited_travel = awaited_travel or []
        to_dels = []
        for fleet in self.returned:
            if not fleet.travel_id in awaited_travel:
                to_dels.append(fleet)
        for fleet in to_dels:
            self.data.pop(fleet.travel_id)

    @property
    def arrived(self):
        return self.cond(is_arrived=True)

    @property
    def returned(self):
        return self.cond(is_returned=True)

    @classmethod
    def load(cls, data):
        missions = cls()
        for mission in data.values():
            missions.add(FlyingFleet(**mission))
        return missions

    def dump(self):
        return {fleet.travel_id: fleet.dump() for fleet in self}
