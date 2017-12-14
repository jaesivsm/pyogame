import re
from pyogame.tools.const import Pages
from pyogame.tools.resources import Resources


class AbstractOgameObj:
    position = None
    page = None
    requirements = None

    @property
    def name(self):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.__class__.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    def copy(self):
        raise NotImplementedError()

    @property
    def cost(self):
        raise NotImplementedError()

    def dump(self):
        raise NotImplementedError()

    @classmethod
    def load(cls, **kwargs):
        raise NotImplementedError()


class AbstractConstruct(AbstractOgameObj):
    base_metal_cost = 0
    base_crystal_cost = 0
    base_deuterium_cost = 0
    energy_factor = 0
    power = None

    def __init__(self, level=0):
        self.level = level

    def _cost(self, res, level=None):
        level = level if level else self.level
        return getattr(self, 'base_%s_cost' % res) * pow(self.power, level - 1)

    @property
    def css_dom(self):
        raise NotImplementedError()

    @property
    def cost(self):
        return Resources(metal=self._cost('metal'),
                crystal=self._cost('crystal'),
                deuterium=self._cost('deuterium'),
                energy=self._energy(self.level + 1) - self._energy(self.level))

    def _energy(self, level):
        return self.energy_factor * (level - 1) * pow(1.1, level)

    def __repr__(self):
        return "<%s(%d)>" % (self.__class__.__name__, self.level)

    def __str__(self):
        return "%s (lvl %d)" % (self.name, self.level)

    def copy(self):
        return self.__class__(self.level)

    def dump(self):
        return {'level': self.level}

    @classmethod
    def load(cls, **kwargs):
        obj = cls()
        obj.level = kwargs.get(obj.name, 0)
        return obj


class AbstractMultiConstruct(AbstractOgameObj):
    metal_cost = 0
    crystal_cost = 0
    deuterium_cost = 0
    quantity = 0

    def __init__(self, quantity=0):
        self.quantity = quantity

    @property
    def cost(self):
        return Resources(metal=self.metal_cost * self.quantity,
                         crystal=self.crystal_cost * self.quantity,
                         deuterium=self.deuterium_cost * self.quantity)

    @property
    def xpath(self):
        raise NotImplementedError()

    def copy(self):
        return self.__class__(self.quantity)

    def __len__(self):
        return self.quantity

    def __repr__(self):
        return "<%s(%d)>" % (self.__class__.__name__, self.quantity)

    def __str__(self):
        return "%s (%d)" % (self.name, self.quantity)

    def dump(self):
        return {'quantity': self.quantity}

    @classmethod
    def load(cls, **kwargs):
        obj = cls()
        obj.quantity = kwargs.get(obj.name, 0)
        return obj


class ResourcesBuilding(AbstractConstruct):
    page = Pages.resources

    @property
    def css_dom(self):
        return "#button%d a.fastBuild" % self.position


class Tank(ResourcesBuilding):
    power = 2
    energy_factor = 0
    page = Pages.resources

    @property
    def capacity(self):  # fugly, couldn't find the true formula for that one
        return {0: 10, 1: 20, 2: 40, 3: 75, 4: 140, 5: 255, 6: 470, 7: 865,
                8: 1590, 9: 2920, 10: 5355, 11: 9820, 12: 18005, 13: 33005,
                14: 60510, 15: 110925, 16: 203350, 17: 372785, 18: 683385,
                19: 1252785, 20: 2296600}[self.level] * 1000


class StationBuilding(AbstractConstruct):
    page = Pages.station
    power = 2
    energy_factor = 0

    @property
    def css_dom(self):
        return "#button%d a.fastBuild" % self.position


class Technology(AbstractConstruct):
    page = Pages.research
    research_number = None
    power = 2

    @property
    def css_dom(self):
        return ".research%d a.fastBuild" % self.research_number


class Ships(AbstractMultiConstruct):
    single_ship_capacity = 0
    are_transport = False
    xpath = None
    ships_id = None

    @property
    def capacity(self):
        return self.quantity * self.single_ship_capacity

    def copy(self):
        return self.__class__(self.quantity)


class CivilShips(Ships):
    position = 0

    def xpath(self):
        return "//ul[@id='civil']/li[%d]/div/a" % self.position
