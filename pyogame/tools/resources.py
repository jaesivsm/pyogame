RES_TYPES = ['metal', 'crystal', 'deuterium', 'energy']
SPLIT = 3
UNITS = 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'
MULTIPLE = {(i + 1) * 3: u for i, u in enumerate(UNITS)}



def pretty_number(number, short=True):
    number = str(int(number))
    browse = zip(range(-SPLIT, -len(number) - SPLIT, -SPLIT),
                 range(0, -len(number) - SPLIT, -SPLIT))
    lst = [number[start:end if end else None] for start, end in browse][::-1]
    result = lst[0]
    unit = MULTIPLE.get((len(lst)-1) * SPLIT, '')
    if short or len(lst) <= 1:
        if len(lst) <= 1:
            return result + unit
        return str(int(result) + (1 if int(lst[1]) > 500 else 0)) + unit
    if lst[1] == '000':
        return result + unit
    if lst[1][1:3] == '00':
        return result + unit + lst[1][0]
    return result + unit + lst[1]


class Resources:

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

    def __eq__(self, other):
        return all(amount == other[res_type]
                   for res_type, amount in self.movable)

    def __gt__(self, other):
        return all(amount > other[res_type]
                   for res_type, amount in self.movable)

    def __ge__(self, other):
        return all(amount >= other[res_type]
                   for res_type, amount in self.movable)

    def __lt__(self, other):
        return all(amount < other[res_type]
                   for res_type, amount in self.movable)

    def __le__(self, other):
        return all(amount <= other[res_type]
                   for res_type, amount in self.movable)

    def __len__(self):
        return sum(dict(self.__iter__()).values())

    def __repr__(self):
        output = [str(self[r_t]) for r_t in RES_TYPES if self[r_t]]
        return r"<Resources(%s)>" % r','.join(output)

    def __str__(self):
        output = []
        for res_type in RES_TYPES:
            if self[res_type]:
                output.append("%s%s" % (res_type[0].upper(),
                                        pretty_number(self[res_type])))
        return ",".join(output)
