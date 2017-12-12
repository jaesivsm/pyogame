import logging
from pyogame.tools import Resources
from pyogame.fleet import Fleet
from pyogame.constructions import Constructions
from pyogame.tools.common import coords_to_key

logger = logging.getLogger(__name__)


def cheapest(buildings):
    return sorted(buildings, key=lambda x: x.cost, reverse=True)[0]


class Planet:

    def __init__(self, name, coords, position, **kwargs):
        self.name = name
        self.coords = coords
        self.position = position
        self.idle = kwargs.get('idle', False)
        self.capital = kwargs.get('capital', False)
        self.waiting_for = kwargs.get('waiting_for', {})

        self.fleet = kwargs.get('fleet', Fleet())
        self.resources = kwargs.get('resources', Resources())
        self.constructs = kwargs.get('constructs', Constructions())
        self.plans = kwargs.get('plans', Constructions())
        self.remove_old_plans()

    def add_construction_plan(self, new_plan, level=None):
        # checking type
        new_cls = self.constructs.registry.get(new_plan)
        if new_cls is None:
            logger.error("Can't make out what %r is", new_plan)
            return
        current = self.get_curr(new_plan)

        # checking level against current
        if level is None:
            level = current.level + 1
        new = new_cls(level)
        if new.level <= current.level:
            logger.error("%r already have %r can't construct %r",
                         self, current, new)
            return

        # checking level against existing plan
        for existing_plan in self.plans:
            if new.name == existing_plan and new.level <= existing_plan.level:
                logger.error("%r already have %r planned for construction, "
                        "can't construct %r", self, existing_plan, new)
                return

        self.plans.add(new)

    def get_curr(self, obj):
        return self.constructs.cond(
                name=obj if isinstance(obj, str) else obj.name).first

    def remove_old_plans(self):
        to_remove = [plan for plan in self.plans
                     if plan.level <= self.get_curr(plan).level]
        for plan in to_remove:
            self.plans.remove(plan)

    @property
    def key(self):
        return coords_to_key(self.coords)

    @property
    def is_fleet_empty(self):
        return not bool(self.fleet)

    @property
    def is_idle(self):
        return self.idle and not self.waiting_for

    @property
    def is_waiting(self):
        return bool(self.waiting_for)

    @property
    def is_metal_tank_full(self):
        return self.resources.metal >= self.get_curr('metal_tank').capacity

    @property
    def is_crystal_tank_full(self):
        return self.resources.crystal >= self.get_curr('crystal_tank').capacity

    @property
    def is_deuterium_tank_full(self):
        current_deut_cap = self.get_curr('deuterium_tank').capacity
        return self.resources.deuterium >= current_deut_cap

    def time_to_construct(self, cost):
        return ((float(cost.metal) + cost.crystal)
                / (2500. * (float(self.get_curr('robot_factory').level) + 1.)
                * pow(2., float(self.get_curr('nanite_factory').level))))

    def _get_next_out_of_plans(self):
        if not self.plans.data:
            return None
        return cheapest(self.requirements_for(plan) for plan in self.plans)

    def requirements_for(self, building):
        if building.requirements:
            eligible_reqs = [self.requirements_for(req)
                             for req in building.requirements
                             if req.level > self.get_curr(req).level]
            if eligible_reqs:
                return cheapest(eligible_reqs)
        if building.level > self.get_curr(building).level + 1:
            return self.requirements_for(
                    building.__class__(building.level - 1))
        return building

    @property
    def to_construct(self):
        # Handling construction list
        to_construct = self._get_next_out_of_plans()
        if to_construct:
            return self.requirements_for(to_construct)

        metal_mine = self.get_curr('metal_mine')
        metal_tank = self.get_curr('metal_tank')
        crystal_tank = self.get_curr('crystal_tank')
        deut_tank = self.get_curr('deuterium_tank')

        to_construct = metal_mine
        if self.get_curr('deuterium_synthetizer').level < metal_mine.level - 7:
            to_construct = self.get_curr('deuterium_synthetizer')
        if self.get_curr('crystal_mine').level < metal_mine.level - 3:
            to_construct = self.get_curr('crystal_mine')
        # more or less 5%
        if to_construct.cost.energy * .95 > self.resources.energy:
            to_construct = self.get_curr('solar_plant')
        if self.capital:
            if metal_tank.capacity < to_construct.cost.metal \
                    or self.is_metal_tank_full:
                to_construct = metal_tank
            elif crystal_tank.capacity < to_construct.cost.crystal \
                    or self.is_crystal_tank_full:
                to_construct = crystal_tank
            elif deut_tank.capacity < to_construct.cost.deuterium \
                    or self.is_deuterium_tank_full:
                to_construct = deut_tank
        else:
            def should_build_tank(res_type, ratio):
                mine = self.get_curr('%s_mine' % res_type)
                tank = self.get_curr('%s_tank' % res_type)
                return float(mine.level) / (1 + tank.level) > ratio
            if should_build_tank('metal', 7):
                to_construct = self.get_curr('metal_tank')
            elif should_build_tank('crystal', 9):
                to_construct = self.get_curr('crystal_tank')
        return self.requirements_for(to_construct)

    @classmethod
    def load(cls, **kwargs):
        for key, attr_cls in (('fleet', Fleet),
                              ('resources', Resources),
                              ('constructs', Constructions),
                              ('plans', Constructions)):
            kwargs[key] = attr_cls.load(**kwargs.get(key, {}))
        return cls(**kwargs)

    def dump(self):
        return {'name': self.name,
                'coords': self.coords,
                'idle': self.idle,
                'position': self.position,
                'waiting_for': self.waiting_for,
                'capital': self.capital,
                'resources': self.resources.dump(),
                'fleet': {'data': self.fleet.dump()},
                'constructs': {'data': self.constructs.dump()},
                'plans': {'data': self.plans.dump()}}

    def __repr__(self):
        return r"<Planet(%r, %r, %r)>" % (
                self.name, self.coords, self.position)

    def __str__(self):
        return '%s %r' % (self.name, self.coords)

    def __eq__(self, other):
        if isinstance(other, Planet) and other.coords == self.coords:
            return True
        return False
