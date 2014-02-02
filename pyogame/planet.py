import logging

from pyogame.const import Resources, IDLE, CAPITAL, WAITING_RES
from pyogame.fleet import Fleet
from pyogame.constructions import MetalMine, CrystalMine, \
        DeuteriumSynthetizer, SolarPlant

logger = logging.getLogger(__name__)


class Planet(object):

    def __init__(self, name, coords, position):
        self.name = name
        self.coords = coords
        self.position = position
        self._flags = {}

        self.fleet = Fleet()
        self.resources = Resources()

        self.metal_mine = MetalMine()
        self.crystal_mine = CrystalMine()
        self.deuterium_synthetize = DeuteriumSynthetizer()
        self.solar_plant = SolarPlant()

    def __repr__(self):
        return r"<%s %s>" % (self.name, self.coords)

    def __eq__(self, other):
        if isinstance(other, Planet) and other.coords == self.coords:
            return True
        return False

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

    def get_flag(self, flag, default=None):
        if self.has_flag(flag):
            return self._flags[flag]
        return default

    @property
    def is_fleet_empty(self):
        return not bool(self.fleet)

    @property
    def is_idle(self):
        return self.has_flag(IDLE) and not self.has_flag(WAITING_RES)

    @property
    def is_capital(self):
        return self.has_flag(CAPITAL)

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
