import re
import logging

from pyogame.tools.resources import Resources

logger = logging.getLogger(__name__)


class Constructions(object):
    base_metal_cost = 0
    base_crystal_cost = 0
    base_deuterium_cost = 0
    power = 1.5
    energy_factor = 0
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

    @property
    def name(self):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.__class__.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    @property
    def cost(self):
        return Resources(metal=self._cost('metal'),
                crystal=self._cost('crystal'),
                deuterium=self._cost('deuterium'),
                energy=self._energy(self.level+1) - self._energy(self.level))

    def __repr__(self):
        return "<%s(%d)>" % (self.__class__.__name__, self.level)

    def __str__(self):
        return "%s (lvl %d)" % (self.name, self.level)


class MetalMine(Constructions):
    base_metal_cost = 60
    base_crystal_cost = 15
    position = 1
    energy_factor = 10


class CrystalMine(Constructions):
    base_metal_cost = 48
    base_crystal_cost = 24
    power = 1.6
    position = 2
    energy_factor = 10


class DeuteriumSynthetizer(Constructions):
    base_metal_cost = 225
    base_crystal_cost = 75
    energy_factor = 20
    position = 3


class SolarPlant(Constructions):
    base_metal_cost = 75
    base_crystal_cost = 30
    position = 4


class Tank(Constructions):
    base_metal_cost = 1000
    power = 2

    @property
    def capacity(self):  #FIXME fugly, couldn't find the true formula for that one
        return {0: 10, 1: 20, 2: 40, 3: 75, 4: 140, 5: 255, 6: 470, 7: 865,
                8: 1590, 9: 2920, 10: 5355, 11: 9820, 12: 18005, 13: 33005,
                14: 60510, 15: 110925, 16: 203350, 17: 372785, 18: 683385,
                19: 1252785, 20: 2296600}[self.level] * 1000


class MetalTank(Tank):
    position = 7


class CrystalTank(Tank):
    base_crystal_cost = 500
    position = 8
    power = 2


class DeuteriumTank(Tank):
    base_metal_cost = 1000
    base_crystal_cost = 1000
    position = 9


class RobotFactory(Constructions):
    base_metal_cost = 400
    base_crystal_cost = 120
    base_deuterium_cost = 200
    power = 2
    energy_factor = 0
    position = 1


class NaniteFactory(Constructions):
    base_metal_cost = 1000000
    base_crystal_cost = 500000
    base_deuterium_cost = 100000
    power = 2
    energy_factor = 0
    position = 5


BUILDINGS = {
        1: MetalMine(),
        2: CrystalMine(),
        3: DeuteriumSynthetizer(),
        4: SolarPlant(),
        7: MetalTank(),
        8: CrystalTank(),
        9: DeuteriumTank(),
}
STATIONS = {
        1: RobotFactory(),
        5: NaniteFactory(),
}
