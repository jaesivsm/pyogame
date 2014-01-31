import logging

from pyogame.fleet import Fleet

logger = logging.getLogger(__name__)


class Planet(object):
    is_capital = False

    def __init__(self, name, coords, position):
        self.name = name
        self.coords = coords
        if type(coords) is not list:
            self.coords = [int(coord) for coord in coords.split(':')]
        self.position = position
        self.fleet = Fleet()
        self.resources = {}
        self.buildings = {}
        logger.info('Got planet %r' % self)

    def __repr__(self):
        return r"<%s %s>" % (self.name, self.coords)

    def __eq__(self, other):
        if isinstance(other, Planet) and other.coords == self.coords:
            return True
        return False
