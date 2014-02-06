import logging

from pyogame.fleet import Fleet
from pyogame.planet import Planet
from pyogame.tools import resources, common

logger = logging.getLogger(__name__)


class PlanetCollection(common.Collection):

    def __init__(self, capital_coords=None):
        self.capital_coords = capital_coords
        self.planets = {}
        self.flying_fleets = {}
        super(PlanetCollection, self).__init__(self.planets)

    def add(self, planet):
        self.planets[planet.position] = planet
        if self.capital_coords and self.capital_coords == planet.coords:
            planet.capital = True

    @property
    def colonies(self):
        return self._filter(capital=False)

    @property
    def idles(self):
        return self._filter(is_idle=True)

    @property
    def with_fleet(self):
        return self._filter(is_fleet_empty=False)

    @property
    def waiting(self):
        return self._filter(is_waiting=True)

    @property
    def capital(self):
        return list(self._filter(capital=True))[0]

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
    def waiting_for(self):
        waiting_for = {}
        for planet in empire:
            waiting_for.update(planet.waiting_for)
        return waiting_for

    @property
    def cheapest(self):
        "return the planet with the cheapest construction of any type"
        cheapest = None
        for planet in self:
            if not cheapest:
                cheapest = planet
            elif planet.to_construct.cost < cheapest.to_construct.cost:
                cheapest = planet
        return cheapest

    def load(self, **kwargs):
        for planet_dict in kwargs.get('planets', {}):
            self.add(Planet.load(**planet_dict))
        self.flying_fleets = kwargs.get('flying_fleets', {})

    def dump(self):
        return {'planets': [planet.dump() for planet in self],
                'flying_fleets': self.flying_fleets}

empire = PlanetCollection()
