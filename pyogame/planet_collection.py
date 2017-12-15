import logging

from pyogame.abstract.collections import Collection
from pyogame.abstract.planner import PlannerMixin
from pyogame.fleet import Missions, Fleet
from pyogame.planet import Planet
from pyogame.tools import resources, common
from pyogame.technologies import Technologies

logger = logging.getLogger(__name__)


class PlanetCollection(Collection, PlannerMixin):

    def __init__(self, data, capital=None, **kwargs):
        self.capital_coords = capital
        self.missions = kwargs.get('missions', Missions())
        self.technologies = kwargs.get('technologies', Technologies())
        self.plans = kwargs.get('plans', Technologies(data={}))
        super().__init__(data)
        PlannerMixin.__init__(self, 'technologies', 'plans')
        self.is_researching = False

    def get_curr(self, obj):
        curr = self.technologies.cond(
                name=obj if isinstance(obj, str) else obj.name).first
        if curr is None:
            return self.capital.get_curr(obj)
        return curr

    def requirements_for(self, tech):
        unmatched_req = False
        for req in tech.requirements or []:
            if req.level > self.get_curr(req).level:
                unmatched_req = True
                yield from self.requirements_for(req)
        if unmatched_req:
            return
        elif tech.level > self.get_curr(tech).level + 1:
            yield from self.requirements_for(tech.__class__(tech.level - 1))
            return
        yield tech

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

    def cheapest(self, construct_on_capital=False):
        "return the planet with the cheapest construction of any type"
        choosen = None
        for planet in self:
            if planet.capital and not construct_on_capital:
                continue
            for cnstr in planet.to_construct:
                if not choosen:
                    choosen = (planet, cnstr)
                elif cnstr.cost.movable.total < choosen[1].cost.movable.total:
                    choosen = (planet, cnstr)
        if not choosen:
            return None, None
        planet, building = choosen
        return planet, common.cheapest(requirement for requirement in
                                       planet.requirements_for(building))

    def load(self, data):
        for planet_dict in data.get('planets', {}):
            self.add(Planet.load(**planet_dict))
        self.missions = Missions.load(**data.get('missions', {'data': {}}))
        self.technologies = Technologies.load(
                **data.get('technologies', {}))
        self.plans = Technologies.load(**data.get('plans', {}))
        self.is_researching = data.get('is_researching', False)

    def dump(self):
        return {'planets': [planet.dump() for planet in self],
                'is_researching': self.is_researching,
                'technologies': {'data': self.technologies.dump()},
                'plans': {'data': self.plans.dump()},
                'missions': {'data': self.missions.dump()}}
