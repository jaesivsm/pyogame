__pages = {
        'fleet': {'fr': 'Flotte'},
        'resources': {'fr': 'Ressources'},
}
RES_TYPES = ['deuterium', 'crystal', 'metal', 'energy']
CACHE_PATH = 'planets.flags'

# Flags
IDLE = 'IDLE'
CAPITAL = 'CAPITAL'
WAITING_RES = 'WAITING_RES'
FLEET_ARRIVAL = 'FLEET_ARRIVAL'


class Resources(object):

    def __init__(self, metal=0, crystal=0, deuterium=0, energy=0):
        self.metal = int(metal)
        self.crystal = int(crystal)
        self.deuterium = int(deuterium)
        self.energy = int(energy)

    @property
    def total(self):
        return self.metal + self.crystal + self.deuterium

    @property
    def movable(self):
        res = Resources(self.metal, self.crystal, self.deuterium)
        del res.energy
        return res

    def __iter__(self):
        for res_type, amount in self.__dict__.items():
            yield res_type, amount

    def __getitem__(self, key):
        if not key in RES_TYPES:
            raise TypeError('Resources attributes must be in %r' % RES_TYPES)
        return getattr(self, key)

    def __setitem__(self, key, value):
        if not key in RES_TYPES:
            raise TypeError('Resources attributes must be in %r' % RES_TYPES)
        return setattr(self, key, value)

    def __cmp__(self, other):
        comp = {}
        for res_type, amount in self.movable:  #Only compares what can be moved
            if amount < other[res_type]:
                return -1
            comp[res_type] = self[res_type] > other[res_type]
        if comp.values().count(False) == 4:
            return 0
        return 1

    def __repr__(self):
        return r"<Resources(M%d,C%d,D%d)>" \
                % (self.metal, self.crystal, self.deuterium)


class Collection(object):

    def __init__(self, dictionnary, lang='fr'):
        self.lang = lang
        self.dictionnary = {}
        for key in dictionnary:
            self.dictionnary[key] = dictionnary[key][lang]
            self.dictionnary[dictionnary[key][lang]] = key

    def __getitem__(self, *args, **kwargs):
        return self.dictionnary.__getitem__(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.dictionnary.get(*args, **kwargs)


PAGES = Collection(__pages)
