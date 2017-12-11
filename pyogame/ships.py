import logging
from pyogame.numerable_constructions import NumerableConstructions
from pyogame.constructions import Shipyard
from pyogame.technologies import (ImpulseDrive, CombustionDrive,
                                  Espionnage, Shields)

logger = logging.getLogger(__name__)


class Ships:
    single_ship_capacity = 0
    are_transport = False
    xpath = None
    ships_id = None

    def __init__(self, ships_id=0, name=None, quantity=0):
        self.ships_id = ships_id if self.ships_id is None else self.ships_id
        self.name = name
        self.quantity = int(quantity)

    @property
    def capacity(self):
        return self.quantity * self.single_ship_capacity

    def copy(self):
        return self.__class__(self.ships_id, self.name, self.quantity)

    @classmethod
    def load(cls, **kwargs):
        ships_cls = SHIPS_TYPES.get(kwargs.get('ships_id'), cls)
        return ships_cls(**kwargs)

    def dump(self):
        return {'ships_id': self.ships_id,
                'name': self.name, 'quantity': self.quantity}

    def __repr__(self):
        if self.name:
            return r"<%r(%d)>" % (self.name, self.quantity)
        return "<Unknown Ships(%d)>" % self.quantity

    def __len__(self):
        return self.quantity if self.quantity > 0 else 0


class CivilShips(Ships, NumerableConstructions):
    position = 0

    def xpath(self):
        return "//ul[@id='civil']/li[%d]/div/a" % self.position


class SmallCargo(CivilShips):
    single_ship_capacity = 5000
    metal_cost = 2000
    crystal_cost = 2000
    are_transport = True
    position = 1
    ships_id = 202
    requirements = [Shipyard(2), CombustionDrive(2)]


class LargeCargo(CivilShips):
    single_ship_capacity = 25000
    metal_cost = 6000
    crystal_cost = 6000
    are_transport = True
    position = 2
    ships_id = 203
    requirements = [Shipyard(4), CombustionDrive(6)]


class Probes(CivilShips):
    single_ship_capacity = 5
    crystal_cost = 1000
    position = 5
    ships_id = 210
    requirements = [Shipyard(3), CombustionDrive(3), Espionnage(2)]


class Colony(CivilShips):
    single_ship_capacity = 7500
    metal_cost = 10000
    crystal_cost = 20000
    deuterium_cost = 10000
    position = 3
    ships_id = 208
    requirements = [Shipyard(4), ImpulseDrive(3)]


class Recycler(CivilShips):
    metal_cost = 10000
    crystal_cost = 6000
    deuterium_cost = 2000
    single_ship_capacity = 20000
    position = 4
    ships_id = 209
    requirements = [Shipyard(4), CombustionDrive(6), Shields(2)]


SHIPS_TYPES = {ship.ships_id: ship() for ship in (
        SmallCargo, LargeCargo, Probes, Colony, Recycler)}
