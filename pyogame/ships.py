from pyogame.abstract.ogame_objs import CivilShips
from pyogame.constructions import Shipyard
from pyogame.technologies import (ImpulseDrive, CombustionDrive,
                                  Espionnage, Shields)



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


SHIPS_TYPES = {ship_cls().name: ship_cls
               for ship_cls in CivilShips.__subclasses__()}
