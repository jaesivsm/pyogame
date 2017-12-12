import logging

from pyogame.abstract.collections import Collection
from pyogame.fleet import Missions, Fleet
from pyogame.planet import Planet
from pyogame.tools import resources
from pyogame.technologies import Technologies

logger = logging.getLogger(__name__)


class PlanetCollection(Collection):

    def __init__(self, data, capital=None, **kwargs):
        self.capital_coords = capital
        self.missions = kwargs.get('missions', Missions())
        self.technologies = kwargs.get('technologies', Technologies())
        super().__init__(data)

    def add(self, obj):
        if obj.key in self.data:
            return self.data[obj.key]
        self.data[obj.key] = obj
        if self.capital_coords and self.capital_coords == obj.coords:
            obj.capital = True
        return obj

    def remove(self, obj):
        return self.data.pop(obj.key, None)

    @property
    def colonies(self):
        return self.cond(capital=False)

    @property
    def idles(self):
        return self.cond(is_idle=True)

    @property
    def with_fleet(self):
        return self.cond(is_fleet_empty=False)

    @property
    def waiting(self):
        return self.cond(is_waiting=True)

    @property
    def capital(self):
        return self.cond(capital=True).first

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
        for planet in self:
            waiting_for.update(planet.waiting_for)
        return waiting_for

    def cheapest(self, construct_on_capital=True):
        "return the planet with the cheapest construction of any type"
        cheapest = None
        for planet in self:
            if not construct_on_capital and planet.capital:
                continue
            if not cheapest:
                cheapest = planet
            elif planet.to_construct.cost.movable.total \
                    < cheapest.to_construct.cost.movable.total:
                cheapest = planet
        return cheapest

    def load(self, data):
        for planet_dict in data.get('planets', {}):
            self.add(Planet.load(**planet_dict))
        self.missions = Missions.load(**data.get('missions', {}))
        self.technologies = Technologies.load(
                **data.get('technologies', {}))

    def dump(self):
        return {'planets': [planet.dump() for planet in self],
                'technologies': {'data': self.technologies.dump()},
                'missions': {'data': self.missions.dump()}}
