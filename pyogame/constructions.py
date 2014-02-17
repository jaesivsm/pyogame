import re
import logging

from pyogame.tools.resources import Resources

logger = logging.getLogger(__name__)


class Constructions(object):
    base_metal_cost = 0
    base_crystal_cost = 0
    base_deuterium_cost = 0
    power = 1.5
    energy_factor = 10
    cmp_factor = 1
    position = 0

    def __init__(self, level=0):
        self.level = level

    def _cost(self, res, level=None):
        level = level if level else self.level
        return getattr(self, 'base_%s_cost' % res) * pow(self.power, level)

    def _energy(self, level):
        return self.energy_factor * level * pow(1.1, level)

    @property
    def css_dom(self):
        return "css=#button%d a.fastBuild" % self.position

    @classmethod
    def name(cls):
        return re.sub('([A-Z])', r'_\1', cls.__name__).lower().strip('_')

    @property
    def cost(self):
        return Resources(metal=self._cost('metal'),
                crystal=self._cost('crystal'),
                deuterium=self._cost('deuterium'),
                energy=self._energy(self.level+1) - self._energy(self.level))

    def __repr__(self):
        return "<%s(%d)>" % (self.__class__.__name__, self.level)


class MetalMine(Constructions):
    base_metal_cost = 60
    base_crystal_cost = 15
    position = 1


class CrystalMine(Constructions):
    base_metal_cost = 48
    base_crystal_cost = 24
    power = 1.6
    position = 2


class DeuteriumSynthetizer(Constructions):
    base_metal_cost = 225
    base_crystal_cost = 75
    energy_factor = 20
    position = 3


class SolarPlant(Constructions):
    base_metal_cost = 75
    base_crystal_cost = 30
    energy_factor = 20
    position = 4


class RobotFactory(Constructions):
    base_metal_cost = 400
    base_crystal_cost = 120
    base_deuterium_cost = 200
    power = 2
    energy_factor = 0
    position = 0


class NaniteFactory(Constructions):
    base_metal_cost = 1000000
    base_crystal_cost = 500000
    base_deuterium_cost = 100000
    power = 2
    energy_factor = 0
    position = 5


BUILDINGS = {
        0: MetalMine,
        1: CrystalMine,
        2: DeuteriumSynthetizer,
        3: SolarPlant,
}
STATIONS = {
        0: RobotFactory,
        5: NaniteFactory,
}
