from pyogame.abstract.collections import ConstructCollection
from pyogame.abstract.ogame_objs import Technology
from pyogame.constructions import Laboratory


class Energy(Technology):
    position = 0
    research_number = 113
    base_metal_cost = 0
    base_crystal_cost = 800
    base_deuterium_cost = 400
    requirements = [Laboratory(1)]


class Weapons(Technology):
    position = 13
    research_number = 109
    base_metal_cost = 800
    base_crystal_cost = 200
    requirements = [Laboratory(4)]


class Shields(Technology):
    position = 14
    research_number = 110
    base_metal_cost = 200
    base_crystal_cost = 600
    requirements = [Laboratory(6), Energy(3)]


class Armour(Technology):
    position = 15
    research_number = 111
    base_metal_cost = 1000
    requirements = [Laboratory(2)]


class Laser(Technology):
    position = 1
    research_number = 120
    base_metal_cost = 200
    base_crystal_cost = 100
    requirements = [Laboratory(1), Energy(2)]


class Ions(Technology):
    position = 2
    research_number = 121
    base_metal_cost = 1000
    base_crystal_cost = 300
    base_deuterium_cost = 100
    requirements = [Laboratory(4), Energy(4), Laser(5)]


class Hyperspace(Technology):
    position = 3
    research_number = 114
    base_metal_cost = 0
    base_crystal_cost = 4000
    base_deuterium_cost = 2000
    requirements = [Laboratory(7), Energy(5), Shields(5)]


class Plasma(Technology):
    position = 4
    research_number = 122
    base_metal_cost = 2000
    base_crystal_cost = 4000
    base_deuterium_cost = 1000
    requirements = [Laboratory(10), Energy(8), Laser(10), Ions(5)]


class Espionnage(Technology):
    position = 8
    research_number = 106
    base_metal_cost = 200
    base_crystal_cost = 1000
    base_deuterium_cost = 200
    requirements = [Laboratory(3)]


class Computer(Technology):
    position = 9
    research_number = 108
    base_metal_cost = 0
    base_crystal_cost = 400
    base_deuterium_cost = 600
    requirements = [Laboratory(1)]


class CombustionDrive(Technology):
    position = 5
    research_number = 115
    base_metal_cost = 400
    base_deuterium_cost = 600
    requirements = [Laboratory(1), Energy(1)]


class ImpulseDrive(Technology):
    position = 6
    research_number = 117
    base_metal_cost = 2000
    base_crystal_cost = 4000
    base_deuterium_cost = 600
    requirements = [Laboratory(2), Energy(1)]


class HyperspaceDrive(Technology):
    position = 7
    research_number = 118
    base_metal_cost = 10000
    base_crystal_cost = 20000
    base_deuterium_cost = 6000
    requirements = [Laboratory(7), Hyperspace(3)]


class AstroPhysics(Technology):
    position = 10
    research_number = 124
    base_metal_cost = 4000
    base_crystal_cost = 8000
    base_deuterium_cost = 4000
    requirements = [Laboratory(3), ImpulseDrive(3), Espionnage(4)]


class InterGalacticNetwork(Technology):
    position = 11
    research_number = 123
    base_metal_cost = 240000
    base_crystal_cost = 400000
    base_deuterium_cost = 160000
    requirements = [Laboratory(10), Computer(8), Hyperspace(8)]


class Graviton(Technology):
    position = 12
    research_number = 199
    requirements = [Laboratory(12)]


_tech_reg = {tech_cls().name: tech_cls
             for tech_cls in Technology.__subclasses__()}

class Technologies(ConstructCollection):

    @property
    def registry(self):
        return _tech_reg
