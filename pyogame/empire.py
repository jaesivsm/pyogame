import logging
from datetime import datetime

from pyogame.fleet import Fleet
from pyogame.planet import Planet
from pyogame.tools import flags, resources

logger = logging.getLogger(__name__)


class PlanetCollection(object):

    def __init__(self, capital_coords=None):
        self.capital_coords = capital_coords
        self.planets = {}
        self.filters = {}
        self.__cache = []

    def __iter__(self):
        class FilterFailed(Exception):
            pass
        self.__cache = []
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
                self.__cache.append(planet)
                yield planet
            except FilterFailed:
                pass

    def add(self, planet):
        self.planets[planet.position] = planet
        if self.capital_coords and self.capital_coords == planet.coords:
            planet.add_flag(flags.CAPITAL)

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
    def colonies(self):
        return self._filter(is_capital=False)

    @property
    def idles(self):
        return self._filter(is_idle=True)

    @property
    def with_fleet(self):
        return self._filter(is_fleet_empty=False)

    def has_flag(self, flag):
        return self._filter({('has_flag', flag): True})

    def has_no_flag(self, flag):
        return self._filter({('has_flag', flag): False})

    def del_flags(self, flag):
        for planet in self:
            if flag in planet._flags:
                del planet._flags[flag]

    @property
    def capital(self):
        return list(self._filter(is_capital=True))[0]

    @property
    def fleet(self):
        fleet = Fleet()
        for planet in self:
            for ships in planet.fleet:
                fleet.add(ships=ships)
        return fleet

    @property
    def resources(self):
        res = resources.Resources()
        for planet in self:
            for res_type, amount in planet.resources.movable:
                res[res_type] += amount
        return res

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

    def load(self, **kwargs):
        for planet_dict in kwargs['planets']:
            self.add(Planet.load(**planet_dict))

    def dump(self):
        return {'planets': [planet.dump() for planet in self]}

    def __len__(self):
        return len(self.__cache)

    def __repr__(self):
        return repr(','.join([repr(planet) for planet in self]))

empire = PlanetCollection()
