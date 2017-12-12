import logging

from pyogame.abstract.collections import Collection
from pyogame.abstract.planner import PlannerMixin
from pyogame.fleet import Missions, Fleet
from pyogame.planet import Planet
from pyogame.tools import resources
from pyogame.technologies import Technologies
from pyogame.tools.common import cheapest
from pyogame.constructions import Laboratory

logger = logging.getLogger(__name__)


class PlanetCollection(Collection, PlannerMixin):

    def __init__(self, data, capital=None, **kwargs):
        self.capital_coords = capital
        self.missions = kwargs.get('missions', Missions())
        self.technologies = kwargs.get('technologies', Technologies())
        self.plans = kwargs.get('plans', Technologies())
        super().__init__(data)
        PlannerMixin.__init__(self, 'technologies', 'plans')
        self.is_researching = False

    def empire_next_plan(self, planet):
        if not self._planner_plans.data:
            return None
        return cheapest(filter(self.filter_out_if_researching,
                               (self.requirements_for(planet, plan)[1]
                                for plan in self._planner_plans)))

    def is_tech_type(self, obj):
        return isinstance(obj, tuple(self.technologies.registry.values()))

    def filter_out_if_researching(self, elem):
        return not self.is_researching or (
                self.is_researching and (self.is_tech_type(elem)
                                         or isinstance(elem, Laboratory)))

    def requirements_for(self, planet, construction, only_tech=True):

        def current_level(obj):
            current = self.technologies.cond(name=obj.name).first
            if current is None:
                current = self.capital.constructs.cond(name=obj.name).first
            return current.level

        if construction.requirements:
            eligible_reqs = [self.requirements_for(self.capital, req, False)[1]
                    for req in construction.requirements
                    if (only_tech and self.is_tech_type(req)
                        and req.level > current_level(req))
                        or (not only_tech
                            and req.level > current_level(req))]
            if eligible_reqs:
                return self.capital, cheapest(filter(
                    self.filter_out_if_researching, eligible_reqs))
        if only_tech and self.is_tech_type(construction) or not only_tech:
            if construction.level > current_level(construction) + 1:
                return self.requirements_for(self.capital,
                        construction.__class__(construction.level - 1),
                        only_tech=False)
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
        filter_meth = self.filter_out_if_researching
        for planet in self:
            if not construct_on_capital and planet.capital:
                continue
            if not cheapest_planet:
                cheapest_planet = planet
                continue
            new_const = planet.to_construct(filter_meth)
            cheapest_yet = cheapest_planet.to_construct(filter_meth)
            if new_const.cost.movable.total < cheapest_yet.cost.movable.total:
                cheapest_planet = planet
        if cheapest_planet is None:
            return None, None
        return self.requirements_for(cheapest_planet,
                cheapest_planet.to_construct(filter_meth))

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
