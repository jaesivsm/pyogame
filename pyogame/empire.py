import logging

from pyogame.fleet import Fleet

logger = logging.getLogger(__name__)
__all__ = ('Empire')


class ClassProperty(property):

    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Empire(object):
    planets = {}
    capital = None

    class __metaclass__(type):  # Hack so the class is iterable
        def __iter__(self):
            return self.__iter__()

    @classmethod
    def add(cls, planet):
        cls.planets[planet.position] = planet
        if planet.is_capital:
            logger.warning('Capital is now %r' % planet)
            cls.capital = planet

    @classmethod
    def __iter__(cls):
        return iter(cls.planets.values())

    @ClassProperty
    @classmethod
    def colonies(cls):
        for planet in cls:
            if not planet.is_capital:
                yield planet

    @ClassProperty
    @classmethod
    def fleet(cls):
        fleet = Fleet()
        for planet in cls:
            for ships in planet.fleet:
                fleet.add(ships=ships)
        return fleet

    @ClassProperty
    @classmethod
    def resources(cls):
        resources = {'crystal': 0, 'metal': 0, 'deuterium': 0}
        for planet in cls:
            for key in resources:
                resources[key] += planet.resources[key]
        return resources
