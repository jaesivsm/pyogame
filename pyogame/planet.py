import logging
import dateutil.parser

from pyogame.tools import Resources
from pyogame.fleet import Fleet
from pyogame.constructions import MetalMine, CrystalMine, \
        DeuteriumSynthetizer, SolarPlant

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

        self.metal_mine = MetalMine(kwargs.get('metal_mine', 0))
        self.crystal_mine = CrystalMine(kwargs.get('crystal_mine', 0))
        self.deuterium_synthetize = DeuteriumSynthetizer(
                kwargs.get('deuterium_synthetize', 0))
        self.solar_plant = SolarPlant(kwargs.get('solar_plant', 0))

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
    def to_construct(self):
        if self.deuterium_synthetize.level < self.metal_mine.level - 4:
            if self.deuterium_synthetize.cost.energy > self.resources.energy:
                return self.solar_plant
            return self.deuterium_synthetize
        if self.crystal_mine.level < self.metal_mine.level - 2:
            if self.crystal_mine.cost.energy > self.resources.energy:
                return self.solar_plant
            return self.crystal_mine
        if self.metal_mine.cost.energy > self.resources.energy:
            return self.solar_plant
        return self.metal_mine

    @classmethod
    def load(cls, **kwargs):
        kwargs['fleet'] = Fleet.load(*kwargs.get('fleet', []))
        kwargs['waiting_for'] = kwargs.get('waiting_for', {})
        kwargs['resources'] = Resources.load(**kwargs.get('resources', {}))
        for value in kwargs['waiting_for'].values():
            if 'arrival' in value:
                value['arrival'] = dateutil.parser.parse(value['arrival'])
            if 'return' in value:
                value['return'] = dateutil.parser.parse(value['return'])
        return cls(**kwargs)

    def dump(self):
        return {'name': self.name,
                'coords': self.coords,
                'position': self.position,
                'waiting_for': self.waiting_for,
                'capital': self.capital,
                'fleet': self.fleet.dump(),
                'resources': self.resources.dump(),
                'metal_mine': self.metal_mine.level,
                'crystal_mine': self.crystal_mine.level,
                'deuterium_synthetize': self.deuterium_synthetize.level,
                'solar_plant': self.solar_plant.level}

    def __repr__(self):
        return r"<%s %s>" % (self.name, self.coords)

    def __eq__(self, other):
        if isinstance(other, Planet) and other.coords == self.coords:
            return True
        return False
