from collections import namedtuple

GalaxyRow = namedtuple("GalaxyRow",
        ['postition', 'inactive', 'vacation', 'noob', 'debris', 'recyclers'])


def coords_to_key(coords):
    if isinstance(coords, (list, tuple, set)):
        return ':'.join([str(coord) for coord in coords])
    return coords


class FilterFailed(Exception):
    pass


class Collection(object):

    def __init__(self, data_dict):
        self._data_dict = data_dict
        self._filters = {}

    def __iter__(self):
        for item in self._data_dict.values():
            try:
                for key in self._filters:
                    if getattr(item, key) == self._filters[key]:
                        continue
                    raise FilterFailed()
                yield item
            except FilterFailed:
                pass

    def cond(self, *args, **kwargs):
        coll = self.__class__()
        coll._data_dict = self._data_dict
        coll._filters.update(self._filters)
        for arg in args:
            if isinstance(arg, dict):
                coll._filters.update(arg)
        coll._filters.update(kwargs)
        return coll

    def copy(self):
        coll = self.__class__()
        coll._data_dict.update(self._data_dict)
        coll._filters.update(self._filters)
        return coll

    @property
    def first(self):
        try:
            return self.__iter__().next()
        except StopIteration:
            return None

    def __len__(self):
        return len(list(self.__iter__()))

    def __repr__(self):
        return repr(','.join([repr(item) for item in self]))
