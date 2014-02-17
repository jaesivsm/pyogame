import logging

from pyogame.tools import Resources
from pyogame.fleet import Fleet
from pyogame.constructions import BUILDINGS, STATIONS
from pyogame.tools.common import coords_to_key

logger = logging.getLogger(__name__)


class Planet(object):

    def __init__(self, name, coords, position, **kwargs):
        self.name = name
        self.coords = coords
        self.position = position
        self.idle = kwargs.get('idle', False)
        self.capital = kwargs.get('capital', False)
        self.waiting_for = kwargs.get('waiting_for', {})

        self.fleet = kwargs.get('fleet', Fleet())
        self.resources = kwargs.get('resources', Resources())
        self.station_updated = False
        self.building_updated = False
        self.fleet_updated = False

        for construction in BUILDINGS.values() + STATIONS.values():
            setattr(self, construction.name(),
                    construction(kwargs.get(construction.name(), 0)))

    @property
    def key(self):
        return coords_to_key(self.coords)

    @property
    def is_fleet_empty(self):
        return not bool(self.fleet)

    @property
    def is_idle(self):
        return self.idle and not self.waiting_for

    @property
    def is_waiting(self):
        return bool(self.waiting_for)

    def time_to_construct(self, cost):
        return ((float(cost.metal) + cost.crystal)
                / (2500. * (float(self.robot_factory.level) + 1.)
                * pow(2., float(self.nanite_factory.level))))

    @property
    def to_construct(self):
        to_construct = self.metal_mine
        if self.deuterium_synthetizer.level < self.metal_mine.level - 6:
            to_construct = self.deuterium_synthetizer
        if self.crystal_mine.level < self.metal_mine.level - 2:
            to_construct = self.crystal_mine
        if to_construct.cost.energy > self.resources.energy:
            to_construct = self.solar_plant
        if self.time_to_construct(to_construct.cost) \
                / float(to_construct.level + 1) > 1.25:  # Fixed by experiment
            if self.robot_factory.level < 10:
                return self.robot_factory
            return self.nanite_factory
        return to_construct

    @classmethod
    def load(cls, **kwargs):
        kwargs['fleet'] = Fleet.load(**kwargs.get('fleet', {}))
        kwargs['resources'] = Resources.load(**kwargs.get('resources', {}))
        return cls(**kwargs)

    def dump(self):
        dump = {'name': self.name,
                'coords': self.coords,
                'position': self.position,
                'waiting_for': self.waiting_for,
                'capital': self.capital,
                'fleet': self.fleet.dump(),
                'resources': self.resources.dump(),
        }

        for constru in BUILDINGS.values() + STATIONS.values():
            dump[constru.name()] = getattr(self, constru.name()).level
        return dump

    def __repr__(self):
        return r"<%s %s>" % (self.name, self.coords)

    def __eq__(self, other):
        if isinstance(other, Planet) and other.coords == self.coords:
            return True
        return False
