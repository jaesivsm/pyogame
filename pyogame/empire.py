import json
import logging
import dateutil.parser
from datetime import datetime

from pyogame.fleet import Fleet
from pyogame.const import Resources, RES_TYPES, FLEET_ARRIVAL

logger = logging.getLogger(__name__)


class PlanetCollection(object):

    def __init__(self):
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


    def loads_flags(self, cache):
        import ipdb
        ipdb.set_trace()
        for position, flags in json.loads(cache).items():
            for flag, value in flags.items():
                if flag == FLEET_ARRIVAL:
                    for uuid in value:
                        value[uuid] = dateutil.parser.parse(value[uuid])
                empire.planets[int(position)].add_flag(flag, value)

    def dumps_flags(self):
        handler = lambda o: o.isoformat() if isinstance(o, datetime) else None
        return json.dumps({planet.position: planet._flags for planet in self},
                default=handler)

    def __len__(self):
        return len(self.__cache)

    def __repr__(self):
        return repr(','.join([repr(planet) for planet in self]))

empire = PlanetCollection()
