import logging

from pyogame.fleet import Fleet
from pyogame.constructions import MetalMine, CrystalMine, \
        DeuteriumSynthetizer, SolarPlant

logger = logging.getLogger(__name__)


class Planet(object):
    is_capital = False

    def __init__(self, name, coords, position):
        self.name = name
        self.coords = coords
        if type(coords) is not list:
            self.coords = [int(coord) for coord in coords.split(':')]
        self.position = position
        self.fleet = Fleet()
        self.resources = {}

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
