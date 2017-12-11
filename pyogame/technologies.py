from pyogame.tools.const import Pages
from pyogame.constructions import Constructions, Laboratory


class Technology(Constructions):
    page = Pages.research
    research_number = None
    power = 2

    @property
    def css_dom(self):
        return ".research%d a.fastBuild" % self.research_number


class Energy(Technology):
    research_number = 113
    base_metal_cost = 0
    base_crystal_cost = 800
    base_deuterium_cost = 400
    requirements = [Laboratory(1)]


class Weapons(Technology):
    research_number = 109
    base_metal_cost = 800
    base_crystal_cost = 200
    requirements = [Laboratory(4)]


class Shields(Technology):
    research_number = 110
    base_metal_cost = 200
    base_crystal_cost = 600
    requirements = [Laboratory(6), Energy(3)]


class Armour(Technology):
    research_number = 111
    base_metal_cost = 1000
    requirements = [Laboratory(2)]


class Laser(Technology):
    research_number = 120
    base_metal_cost = 200
    base_crystal_cost = 100
    requirements = [Laboratory(1), Energy(2)]


class Ions(Technology):
    research_number = 121
    base_metal_cost = 1000
    base_crystal_cost = 300
    base_deuterium_cost = 100
    requirements = [Laboratory(4), Energy(4), Laser(5)]


class Hyperspace(Technology):
    research_number = 114
    base_metal_cost = 0
    base_crystal_cost = 4000
    base_deuterium_cost = 2000
    requirements = [Laboratory(7), Energy(5), Shields(5)]


class Plasma(Technology):
    research_number = 122
    base_metal_cost = 2000
    base_crystal_cost = 4000
    base_deuterium_cost = 1000
    requirements = [Laboratory(10), Energy(8), Laser(10), Ions(5)]


class Espionnage(Technology):
    research_number = 106
    base_metal_cost = 200
    base_crystal_cost = 1000
    base_deuterium_cost = 200
    requirements = [Laboratory(3)]


class Computer(Technology):
    research_number = 108
    base_metal_cost = 0
    base_crystal_cost = 400
    base_deuterium_cost = 600
    requirements = [Laboratory(1)]


class CombustionDrive(Technology):
    research_number = 115
    base_metal_cost = 400
    base_deuterium_cost = 600
    requirements = [Laboratory(1), Energy(1)]


class ImpulseDrive(Technology):
    research_number = 117
    base_metal_cost = 2000
    base_crystal_cost = 4000
    base_deuterium_cost = 600
    requirements = [Laboratory(2), Energy(1)]


class HyperspaceDrive(Technology):
    research_number = 118
    base_metal_cost = 10000
    base_crystal_cost = 20000
    base_deuterium_cost = 6000
    requirements = [Laboratory(7), Hyperspace(3)]


class AstroPhysics(Technology):
    research_number = 124
    base_metal_cost = 4000
    base_crystal_cost = 8000
    base_deuterium_cost = 4000
    requirements = [Laboratory(3), ImpulseDrive(3), Espionnage(4)]


class InterGalacticNetwork(Technology):
    research_number = 123
    base_metal_cost = 240000
    base_crystal_cost = 400000
    base_deuterium_cost = 160000
    requirements = [Laboratory(10), Computer(8), Hyperspace(8)]


class Graviton(Technology):
    research_number = 199
    requirements = [Laboratory(12)]
