import logging
import dateutil.parser

from pyogame.tools import Resources, flags
from pyogame.fleet import Fleet
from pyogame.constructions import MetalMine, CrystalMine, \
        DeuteriumSynthetizer, SolarPlant

logger = logging.getLogger(__name__)


class Planet(object):

    def __init__(self, name, coords, position,
            fleet=None, resources=None, **kwargs):
        self.name = name
        self.coords = coords
        self.position = position
        self._flags = {}

        self.fleet = fleet if fleet is not None else Fleet()
        self.resources = resources if resources is not None else Resources()

        self.metal_mine = MetalMine(kwargs.get('metal_mine', 0))
        self.crystal_mine = CrystalMine(kwargs.get('crystal_mine', 0))
        self.deuterium_synthetize = DeuteriumSynthetizer(
                kwargs.get('deuterium_synthetize', 0))
        self.solar_plant = SolarPlant(kwargs.get('solar_plant', 0))

    def has_flag(self, flag):
        return flag in self._flags

    def add_flag(self, flag, value=True):
        if not self.has_flag(flag):
            self._flags[flag] = value
        if self.has_flag(flag) and type(value) is dict \
                and type(self._flags[flag]) is dict:
            self._flags[flag].update(value)

    def del_flag(self, flag):
        if self.has_flag(flag):
            del self._flags[flag]

    def del_flag_key(self, flag, key):
        if self.has_flag(flag) and key in self._flags[flag]:
            self._flags[flag].pop(key)
        if not self.get_flag(flag):
            self.del_flag(flag)

    def get_flag(self, flag, default=None):
        if self.has_flag(flag):
            return self._flags[flag]
        return default

    @property
    def is_fleet_empty(self):
        return not bool(self.fleet)

    @property
    def is_idle(self):
        return self.has_flag(flags.IDLE) \
                and not self.has_flag(flags.WAITING_RES)

    @property
    def is_capital(self):
        return self.has_flag(flags.CAPITAL)

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
        fleet = Fleet.load(*kwargs.pop('fleet'))
        resources = Resources.load(**kwargs.pop('resources'))
        pl_flags = kwargs.pop('flags')
        obj = cls(fleet=fleet, resources=resources, **kwargs)
        for flag, value in pl_flags.items():
            if flag == flags.FLEET_ARRIVAL:
                for uuid in value:
                    value[uuid] = dateutil.parser.parse(value[uuid])
            obj.add_flag(flag, value)
        return obj

    def dump(self):
        return {'name': self.name,
                'coords': self.coords,
                'position': self.position,
                'flags': self._flags,
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
