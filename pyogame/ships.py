import logging

logger = logging.getLogger(__name__)


class Ships(object):
    capacity = 0

    def __init__(self, quantity=0):
        self.quantity = int(quantity)
        self.name = self.__doc__

    def get_capacity(self):
        return self.quantity * self.capacity

    def __repr__(self):
        if self.name:
            return r"%d %s" % (self.quantity, self.name)
        return "Ships"


class PTs(Ships):
    u'Petit transporteur'
    capacity = 5000
    is_transporter = True


class GTs(Ships):
    u'Grand transporteur'
    capacity = 25000
    is_transporter = True


SHIP_NAMES = {u'Grand transporteur': GTs,
        u'Petit transporteur': PTs,
        u'Recycleur': Ships,
        u'Sonde d`espionnage': Ships,
        u'Vaisseau de colonisation': Ships,
        u'Bombardier': Ships,
        u'Chasseur lourd': Ships,
        u'Chasseur l\xe9ger': Ships,
        u'Croiseur': Ships,
        u'Destructeur': Ships,
        u'Traqueur': Ships,
        u'Vaisseau de bataille': Ships,
        u'\xc9toile de la mort': Ships,
}


class Fleet(object):

    def __init__(self):
        self.ships = []

    def add(self, ships_name, quantity):
        self.ships.append(SHIP_NAMES[ships_name](quantity))

    def transport(self, quantity):
        total_capcity = 0
        for ship in self.ships:
            if not ship.is_transporter:
                continue
            capacity = ship.get_capacity()
            total_capcity += capacity
            if capacity > quantity:
                ship_count = quantity / ship.capacity
                ship_count += 1 if quantity % ship.capacity else 0
                return [(ship.ogame_id, ship_count)]
        if total_capcity > quantity:
            ships, total_capcity = [], 0
            for ship in self.ships:
                if not ship.is_transporter:
                    continue
                total_capcity += ship.get_capacity()
                ships.append((ships.ogame_id, ship.quantity))
                if total_capcity > quantity:
                    return ships

    def get_ships_total(self):
        return sum([ships.quantity for ships in self.ships])

    def __repr__(self):
        return repr(','.join(
                [repr(ships) for ships in self.ships
                    if ships.quantity != 0 and ships.name is not None]
            ))


