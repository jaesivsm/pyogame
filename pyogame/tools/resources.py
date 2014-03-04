RES_TYPES = ['metal', 'crystal', 'deuterium', 'energy']


def pretty_number(number, split=3, short=True):
    number = str(int(number))
    browse = zip(xrange(-split, -len(number)-split, -split),
                 xrange(0, -len(number)-split, -split))
    lst = [number[start:end if end else None] for start, end in browse][::-1]
    if not short:
        return '.'.join(lst)
    multiple = {3: 'k', 6: 'M', 9: 'G', 12: 'T',
                15: 'P', 18: 'E', 21: 'Z', 24: 'Y'}
    if len(lst) == 2:
        return lst[0] + 'k'
    return '.'.join(lst[:2]) + multiple.get((len(lst)-2) * split, '')


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

    @classmethod
    def load(cls, **resources):
        return cls(**resources)

    def dump(self):
        return {'metal': self.metal, 'crystal': self.crystal,
                'deuterium': self.deuterium, 'energy': self.energy}

    def __iter__(self):
        for res_type, amount in vars(self).items():
            yield res_type, amount

    def __getitem__(self, key):
        if not key in RES_TYPES:
            raise TypeError('Resources attributes must be in %r' % RES_TYPES)
        return getattr(self, key, 0)

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

    def __len__(self):
        return sum(dict(self.__iter__()).values())

    def __repr__(self):
        output = []
        for res_type in RES_TYPES:
            if self[res_type]:
                output.append("%s%s" % (res_type[0].upper(),
                                        pretty_number(self[res_type])))
        return r"<Resources(%s)>" % r','.join(output)
