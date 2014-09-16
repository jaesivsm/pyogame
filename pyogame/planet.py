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

        self.construction_plans = []
        for construction in BUILDINGS.values() + STATIONS.values():
            setattr(self, construction.name,
                    construction.__class__(kwargs.get(construction.name, 0)))

        for planned_construct, lvl \
                in kwargs.get('construction_plans', {}).items():
            self.add_construction_plan(planned_construct, lvl)

    def add_construction_plan(self, new_plan, level):
        for planned_construct in self.construction_plans:
            if new_plan == planned_construct.name:
                planned_construct.level = level
                return
        for construction in BUILDINGS.values() + STATIONS.values():
            if new_plan == construction.name \
                    and getattr(self, construction.name).level < level:
                self.construction_plans.append(construction.__class__(level))
                return

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

    @property
    def is_metal_tank_full(self):
        return self.resources.metal >= self.metal_tank.capacity

    @property
    def is_crystal_tank_full(self):
        return self.resources.crystal >= self.crystal_tank.capacity

    @property
    def is_deuterium_tank_full(self):
        return self.resources.deuterium >= self.deuterium_tank.capacity

    def time_to_construct(self, cost):
        return ((float(cost.metal) + cost.crystal)
                / (2500. * (float(self.robot_factory.level) + 1.)
                * pow(2., float(self.nanite_factory.level))))

    @property
    def to_construct(self):
        # Handling construction list
        if self.construction_plans:
            to_construct = None
            for plan in self.construction_plans:
                construction = getattr(self, plan.name)
                if construction.level < plan.level and (not to_construct
                        or to_construct.cost.total > construction.cost.total):
                    to_construct = construction
            if to_construct is not None:
                return to_construct

        to_construct = self.metal_mine
        if self.deuterium_synthetizer.level < self.metal_mine.level - 7:
            to_construct = self.deuterium_synthetizer
        if self.crystal_mine.level < self.metal_mine.level - 3:
            to_construct = self.crystal_mine
        # more or less 5%
        if to_construct.cost.energy * .95 > self.resources.energy:
            to_construct = self.solar_plant
        #if self.time_to_construct(to_construct.cost) \
        #        / float(to_construct.level + 1) > 2:  # Fixed by experiment
        #    if self.robot_factory.level < 10:
        #        to_construct = self.robot_factory
        #    else:
        #        to_construct = self.nanite_factory
        if self.capital:
            if self.metal_tank.capacity < to_construct.cost.metal \
                    or self.is_metal_tank_full:
                to_construct = self.metal_tank
            elif self.crystal_tank.capacity < to_construct.cost.crystal \
                    or self.is_crystal_tank_full:
                to_construct = self.crystal_tank
            elif self.deuterium_tank.capacity < to_construct.cost.deuterium \
                    or self.is_deuterium_tank_full:
                to_construct = self.deuterium_tank
        else:
            def should_construct_tank(mine, tank, ratio):
                return float(mine.level) / (1 + tank.level) > ratio
            if should_construct_tank(self.metal_mine, self.metal_tank, 7):
                to_construct = self.metal_tank
            elif should_construct_tank(self.crystal_mine, self.crystal_tank, 9):
                to_construct = self.crystal_tank
        return to_construct

    @classmethod
    def load(cls, **kwargs):
        kwargs['fleet'] = Fleet.load(**kwargs.get('fleet', {}))
        kwargs['resources'] = Resources.load(**kwargs.get('resources', {}))
        return cls(**kwargs)

    def dump(self):
        dump = {'name': self.name,
                'coords': self.coords,
                'idle': self.idle,
                'position': self.position,
                'waiting_for': self.waiting_for,
                'capital': self.capital,
                'fleet': self.fleet.dump(),
                'resources': self.resources.dump(),
                'construction_plans': {
                    construction.name: construction.level
                    for construction in self.construction_plans},
        }

        for constru in BUILDINGS.values() + STATIONS.values():
            dump[constru.name] = getattr(self, constru.name).level
        return dump

    def __repr__(self):
        return r"<Planet(%r, %r, %r)>" % (
                self.name, self.coords, self.position)

    def __str__(self):
        return '%s %r' % (self.name, self.coords)

    def __eq__(self, other):
        if isinstance(other, Planet) and other.coords == self.coords:
            return True
        return False
