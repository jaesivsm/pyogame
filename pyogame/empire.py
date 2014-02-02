import logging

from pyogame.fleet import Fleet
from pyogame.const import Resources, RES_TYPES

logger = logging.getLogger(__name__)


class PlanetCollection(object):

    def __init__(self):
        self.planets = {}
        self.filters = {}

    def __iter__(self):
        class FilterFailed(Exception):
            pass
        for planet in self.planets.values():
            try:
                for key in self.filters:
                    if isinstance(key, (list, tuple)):
                        call = getattr(planet, key[0])
                        if call(*key[1:]) == self.filters[key]:
                            continue
                    elif getattr(planet, key) == self.filters[key]:
                        continue
                    raise FilterFailed()
                yield planet
            except FilterFailed:
                pass

    def add(self, planet):
        self.planets[planet.position] = planet

    def _filter(self, *args, **kwargs):
        pl_col = PlanetCollection()
        pl_col.planets = self.planets
        pl_col.filters.update(self.filters)
        for arg in args:
            if isinstance(arg, dict):
                pl_col.filters.update(arg)
        pl_col.filters.update(kwargs)
        return pl_col

    @property
    def capital(self):
        return list(self._filter(is_capital=True))[0]

    @property
    def colonies(self):
        return self._filter(is_capital=False)

    @property
    def idles(self):
        return self._filter(is_idle=True)

    def has_flag(self, flag):
        return self._filter({('has_flag', flag): True})

    def has_no_flag(self, flag):
        return self._filter({('has_flag', flag): False})

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
                resources[res_type] += planet.resources[res_type]
        return resources

    @property
    def cheapest(self):
        "return the planet with the cheapest construction of the given type"
        cheapest = None
        for planet in self:
            if not cheapest:
                cheapest = planet
            elif planet.to_construct.cost < cheapest.to_construct.cost:
                cheapest = planet
        return cheapest

    def _flags(self):
        return {planet.position: planet.flags for planet in self}

    def __len__(self):
        return len(self.planets)

    def __repr__(self):
        return repr(','.join([repr(planet) for planet in self]))


empire = PlanetCollection()
