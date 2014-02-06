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

    def _filter(self, *args, **kwargs):
        coll = self.__class__()
        coll._data_dict = self._data_dict
        coll._filters.update(self._filters)
        for arg in args:
            if isinstance(arg, dict):
                coll._filters.update(arg)
        coll._filters.update(kwargs)
        return coll

    def __len__(self):
        return len(list(self.__iter__()))

    def __repr__(self):
        return repr(','.join([repr(item) for item in self]))
