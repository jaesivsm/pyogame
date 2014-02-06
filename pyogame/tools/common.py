class FilterFailed(Exception):
    pass


class Collection(object):

    def __init__(self, data_dict):
        self.__cache = []
        self._data_dict = data_dict
        self._filters = {}

    def __iter__(self):
        if self.__cache:
            for cache_elem in self.__cache:
                yield cache_elem
            raise StopIteration()
        for item in self._data_dict.values():
            try:
                for key in self._filters:
                    if getattr(item, key) == self._filters[key]:
                        continue
                    raise FilterFailed()
                self.__cache.append(item)
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
        if not self.__cache:
            list(self.__iter__())
        return len(self.__cache)

    def __repr__(self):
        return repr(','.join([repr(item) for item in self]))
