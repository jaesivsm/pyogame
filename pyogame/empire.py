import logging

from pyogame.fleet import Fleet
from pyogame.const import Resources, RES_TYPES

logger = logging.getLogger(__name__)


class PlanetCollection(object):

    def __init__(self):
        self.planets = {}
        self.capital = None

    def __iter__(self):
        return iter(self.planets.values())

    def add(self, planet):
        self.planets[planet.position] = planet
        if planet.is_capital:
            logger.warning('Capital is now %r' % planet)
            self.capital = planet

    def _filter(self, **kwargs):
        pl_col = PlanetCollection()
        for planet in self:
            for key, value in kwargs.items():
                if getattr(planet, key) == value:
                    pl_col.add(planet)
        return pl_col

    @property
    def colonies(self):
        return self._filter(is_capital=False)

    @property
    def idles(self):
        return self._filter(idle=True)

    @property
    def fleet(self):
        fleet = Fleet()
        for planet in self:
            for ships in planet.fleet:
                fleet.add(ships=ships)
        return fleet

    @property
    def resources(self):
        resources = Resources()
        for planet in self:
            for res_type in RES_TYPES:
                if not res_type in resources:
                    resources[res_type] = 0
                resources[res_type] += planet.resources[res_type]
        return resources

    def cheapest(self, construct_type):
        "return the planet with the cheapest construction of the given type"
        cheapest = None
        for planet in self:
            construct = getattr(planet, construct_type)
            if not cheapest:
                cheapest = planet
            if construct.level < getattr(cheapest, construct_type).level:
                cheapest = planet
        return cheapest

    def __len__(self):
        return len(self.planets)

    def __repr__(self):
        return repr(','.join([repr(planet) for planet in self]))


empire = PlanetCollection()
