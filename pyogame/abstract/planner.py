import logging
from pyogame.tools.common import cheapest

logger = logging.getLogger(__name__)


class PlannerMixin:

    def __init__(self, collection_name, plans_name):
        self._planner_collection_name = collection_name
        self._planner_plans_name = plans_name
        self.planner_remove_old()

    @property
    def _planner_collection(self):
        return getattr(self, self._planner_collection_name)

    @property
    def _planner_registry(self):
        return getattr(self._planner_collection, 'registry')

    @property
    def _planner_plans(self):
        return getattr(self, self._planner_plans_name)

    def _planner_get_curr(self, obj):
        return self._planner_collection.cond(name=obj.name).first

    def planner_next_plan(self):
        if not self._planner_plans.data:
            return None
        return cheapest(self.requirements_for(plan)
                        for plan in self._planner_plans)

    def planner_add(self, plan_name, level=None):
        # checking type
        new_cls = self._planner_registry.get(plan_name)
        if new_cls is None:
            logger.error("Can't make out what %r is", plan_name)
            return
        current = self._planner_collection.cond(name=plan_name).first

        # checking level against current
        try:
            level = int(level)
        except TypeError:
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

        self._planner_plans.add(new)

    def planner_remove_old(self):
        to_remove = [plan for plan in self.plans
                     if plan.level <= self._planner_get_curr(plan).level]
        for plan in to_remove:
            self._planner_plans.remove(plan)
