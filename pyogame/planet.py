import logging

from pyogame.const import Resources
from pyogame.fleet import Fleet
from pyogame.constructions import MetalMine, CrystalMine, \
        DeuteriumSynthetizer, SolarPlant

logger = logging.getLogger(__name__)


class Planet(object):
    is_capital = False

    def __init__(self, name, coords, position, idle=True):
        self.name = name
        self.coords = coords
        self.position = position
        self.idle = idle

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
