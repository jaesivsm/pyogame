import logging

from pyogame.abstract.collections import Collection
from pyogame.abstract.planner import PlannerMixin
from pyogame.fleet import Missions, Fleet
from pyogame.planet import Planet
from pyogame.tools import resources
from pyogame.technologies import Technologies
from pyogame.tools.common import cheapest

logger = logging.getLogger(__name__)


class PlanetCollection(Collection, PlannerMixin):

    def __init__(self, data, capital=None, **kwargs):
        self.capital_coords = capital
        self.missions = kwargs.get('missions', Missions())
        self.technologies = kwargs.get('technologies', Technologies())
        self.plans = kwargs.get('plans', Technologies())
        super().__init__(data)
        PlannerMixin.__init__(self, 'technologies', 'plans')
        self.is_researching_tech = False

    def planner_next_plan(self, planet):
        if not self._planner_plans.data:
            return None
        return cheapest(self.requirements_for(planet, plan)[1]
                        for plan in self._planner_plans)

    def requirements_for(self, planet, construction):

        def is_tech_type(obj):
            return isinstance(obj, tuple(self.technologies.registry.values()))

        def current_tech_level(obj):
            return self.technologies.cond(name=obj.name).first.level

        if construction.requirements:
            eligible_reqs = [self.requirements_for(self.capital, req)[1]
                    for req in construction.requirements
                    if is_tech_type(req)
                        and req.level > current_tech_level(req)]
            if eligible_reqs:
                return self.capital, cheapest(eligible_reqs)
        if is_tech_type(construction):
            if construction.level > current_tech_level(construction) + 1:
                return self.requirements_for(self.capital,
                        construction.__class__(construction.level - 1))
            return self.capital, construction
        return planet, construction

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
        cheapest_planet = None
        for planet in self:
            if not construct_on_capital and planet.capital:
                continue
            if not cheapest_planet:
                cheapest_planet = planet
            elif planet.to_construct.cost.movable.total \
                    < cheapest_planet.to_construct.cost.movable.total:
                cheapest_planet = planet
        if cheapest_planet is None:
            return None, None
        return self.requirements_for(cheapest_planet,
                cheapest_planet.to_construct)

    def load(self, data):
        for planet_dict in data.get('planets', {}):
            self.add(Planet.load(**planet_dict))
        self.missions = Missions.load(**data.get('missions', {}))
        self.technologies = Technologies.load(
                **data.get('technologies', {}))
        self.plans = Technologies.load(**data.get('plans', {}))

    def dump(self):
        return {'planets': [planet.dump() for planet in self],
                'technologies': {'data': self.technologies.dump()},
                'plans': {'data': self.plans.dump()},
                'missions': {'data': self.missions.dump()}}
