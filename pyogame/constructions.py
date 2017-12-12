from pyogame.abstract.collections import ConstructCollection
from pyogame.abstract.ogame_objs import (ResourcesBuilding,
        StationBuilding, Tank)


class MetalMine(ResourcesBuilding):
    base_metal_cost = 60
    base_crystal_cost = 15
    power = 1.5
    position = 1
    energy_factor = 10


class CrystalMine(ResourcesBuilding):
    base_metal_cost = 48
    base_crystal_cost = 24
    power = 1.6
    position = 2
    energy_factor = 10


class DeuteriumSynthetizer(ResourcesBuilding):
    base_metal_cost = 225
    base_crystal_cost = 75
    power = 1.5
    energy_factor = 20
    position = 3


class SolarPlant(ResourcesBuilding):
    base_metal_cost = 75
    base_crystal_cost = 30
    power = 1.5
    position = 4


class MetalTank(Tank):
    base_metal_cost = 1000
    position = 7


class CrystalTank(Tank):
    base_metal_cost = 1000
    base_crystal_cost = 500
    position = 8


class DeuteriumTank(Tank):
    base_metal_cost = 1000
    base_crystal_cost = 1000
    position = 9


class RobotFactory(StationBuilding):
    base_metal_cost = 400
    base_crystal_cost = 120
    base_deuterium_cost = 200
    position = 0


class Shipyard(StationBuilding):
    base_metal_cost = 200
    base_crystal_cost = 400
    base_deuterium_cost = 200
    position = 1
    requirements = [RobotFactory(2)]


class Laboratory(StationBuilding):
    base_metal_cost = 200
    base_crystal_cost = 400
    base_deuterium_cost = 200
    position = 2


class NaniteFactory(StationBuilding):
    base_metal_cost = 1000000
    base_crystal_cost = 500000
    base_deuterium_cost = 100000
    requirements = [RobotFactory(10)]
    position = 5


class Constructions(ConstructCollection):

    @property
    def registry(self):
        return {cls().name: cls for cls in (
                        ResourcesBuilding.__subclasses__()
                        + StationBuilding.__subclasses__()
                        + Tank.__subclasses__()
                ) if cls is not Tank}
