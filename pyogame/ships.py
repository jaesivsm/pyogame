import logging

logger = logging.getLogger(__name__)


class Ships(object):
    single_ship_capacity = 0
    are_transport = False
    xpath = None
    ship_id = None

    def __init__(self, name=None, quantity=0):
        self.name = name
        self.quantity = quantity

    @property
    def capacity(self):
        return self.quantity * self.single_ship_capacity

    def copy(self):
        return self.__class__(self.name, self.quantity)

    def __repr__(self):
        if self.name:
            return r"<%s(%d)>" % (self.name, self.quantity)
        return "<Unknown Ships(%d)>" % self.quantity

    def __len__(self):
        return self.quantity


class PTs(Ships):
    'Petit transporteur'
    single_ship_capacity = 5000
    are_transport = True
    xpath = "//ul[@id='civil']/li[1]/div/a"
    ship_id = "ship_202"


class GTs(Ships):
    'Grand transporteur'
    single_ship_capacity = 25000
    are_transport = True
    xpath = "//ul[@id='civil']/li[2]/div/a"
    ship_id = "ship_203"


SHIPS_TYPES = {'grand transporteur': GTs,
        'petit transporteur': PTs,
}
