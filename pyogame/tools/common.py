from collections import namedtuple

GalaxyRow = namedtuple("GalaxyRow",
        ['coords', 'inactive', 'vacation', 'noob', 'debris', 'debris_content'])


def coords_to_key(coords):
    if isinstance(coords, (list, tuple, set)):
        return ':'.join([str(coord) for coord in coords])
    return coords


class FilterFailed(Exception):
    pass


class Collection:

    def __init__(self, data=None):
        self.data = data or {}
        self.clear = self.data.clear
        self.filters = {}

    def __iter__(self):
        for item in self.data.values():
            try:
                for key in self.filters:
                    if getattr(item, key) == self.filters[key]:
                        continue
                    raise FilterFailed()
                yield item
            except FilterFailed:
                pass

    def cond(self, *args, **kwargs):
        coll = self.__class__(self.data)
        coll.filters.update(self.filters)
        for arg in args:
            if isinstance(arg, dict):
                coll.filters.update(arg)
        coll.filters.update(kwargs)
        return coll

    def copy(self):
        coll = self.__class__()
        coll.data.update(self.data)
        coll.filters.update(self.filters)
        return coll

    @property
    def first(self):
        try:
            return next(self.__iter__())
        except StopIteration:
            return None

    def __len__(self):
        return len(list(self.__iter__()))

    def __repr__(self):
        return repr(','.join([repr(item) for item in self]))
