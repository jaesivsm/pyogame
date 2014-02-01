import logging

logger = logging.getLogger(__name__)


class Constructions(object):
    base_metal_cost = 0
    base_crystal_cost = 0
    base_deuterium_cost = 0
    power = 1.5
    energy_factor = 10

    def __init__(self, level=0):
        self.level = level

    def cost(self, res, level=None):
        level = level if level else self.level
        return getattr(self, 'base_%s_cost' % res) * pow(self.power, level)

    @property
    def next_level_cost(self):
        return self.cost('metal'), self.cost('crystal'), self.cost('deuterium')

    def energy(self, level):
        return self.energy_factor * level * pow(1.1, level)

    @property
    def energy_needed(self):
        return self.energy(self.level+1) - self.energy(self.level)

    def __repr__(self):
        return "<%s(%d)>" % (self.__class__.__name__, self.level)


class MetalMine(Constructions):
    base_metal_cost = 60
    base_crystal_cost = 15


class CrystalMine(Constructions):
    base_metal_cost = 48
    base_crystal_cost = 24
    power = 1.6


class DeuteriumSynthetizer(Constructions):
    base_metal_cost = 225
    base_crystal_cost = 75
    energy_factor = 20


class SolarPlant(Constructions):
    base_metal_cost = 75
    base_crystal_cost = 30
    energy_factor = 20
