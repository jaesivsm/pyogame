import logging

from pyogame.const import Resources

logger = logging.getLogger(__name__)


class Constructions(object):
    base_metal_cost = 0
    base_crystal_cost = 0
    base_deuterium_cost = 0
    power = 1.5
    energy_factor = 10
    cmp_factor = 1
    css_dom = None

    def __init__(self, level=0):
        self.level = level

    def _cost(self, res, level=None):
        level = level if level else self.level
        return getattr(self, 'base_%s_cost' % res) * pow(self.power, level)

    def _energy(self, level):
        return self.energy_factor * level * pow(1.1, level)

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
    css_dom = "css=#button1 a.fastBuild"


class CrystalMine(Constructions):
    base_metal_cost = 48
    base_crystal_cost = 24
    power = 1.6
    css_dom = "css=#button2 a.fastBuild"


class DeuteriumSynthetizer(Constructions):
    base_metal_cost = 225
    base_crystal_cost = 75
    energy_factor = 20
    css_dom = "css=#button3 a.fastBuild"


class SolarPlant(Constructions):
    base_metal_cost = 75
    base_crystal_cost = 30
    energy_factor = 20
    css_dom = "css=#button4 a.fastBuild"
