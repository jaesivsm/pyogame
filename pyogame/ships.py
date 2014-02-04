import logging

logger = logging.getLogger(__name__)


class Ships(object):
    single_ship_capacity = 0
    are_transport = False
    xpath = None
    ships_id = None

    def __init__(self, ships_id=0, name=None, quantity=0):
        self.ships_id = ships_id
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
        return self.quantity


class PTs(Ships):
    single_ship_capacity = 5000
    are_transport = True
    xpath = "//ul[@id='civil']/li[1]/div/a"
    ships_id = 202


class GTs(Ships):
    single_ship_capacity = 25000
    are_transport = True
    xpath = "//ul[@id='civil']/li[2]/div/a"
    ships_id = 203


SHIPS_TYPES = {203 : GTs, 202: PTs}
