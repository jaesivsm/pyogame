__pages = {
        'fleet': {'fr': 'Flotte'},
        'resources': {'fr': 'Ressources'},
}
__buildings = {
        'metal_mine': {'fr': u'Mine de m\xe9tal'},
        'crystal_mine': {'fr': u'Mine de cristal'},
        'deuterium_synthetize': {'fr': u'Synth\xe9tiseur de deut\xe9rium'},
        'solar_plant': {'fr': u'Centrale \xe9lectrique solaire'},
}
RES_TYPES = ['deuterium', 'crystal', 'metal', 'energy']


class Resources(object):

    def __init__(self, metal=0, crystal=0, deuterium=0, energy=0):
        self.metal = metal
        self.crystal = crystal
        self.deuterium = deuterium
        self.energy = energy

    @property
    def total(self):
        return self.metal + self.crystal + self.deuterium

    def __iter__(self):
        for res_type in RES_TYPES:
            if self[res_type]:
                yield res_type, self[res_type]

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
        for res_type in RES_TYPES:
            if self[res_type] < other[res_type]:
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
BUILDINGS = Collection(__buildings)
