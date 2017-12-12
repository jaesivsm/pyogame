import logging

logger = logging.getLogger(__name__)

class FilterFailed(Exception):
    pass


class Collection:

    def __init__(self, data=None):
        self.data = data or {}
        self.filters = {}

    def clear(self):
        return self.data.clear()

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
        return "<%s(%s)>" % (self.__class__.__name__,
                ','.join([repr(item) for item in self]))

    def add(self, obj):
        raise NotImplementedError()

    def remove(self, obj):
        raise NotImplementedError()

    @classmethod
    def load(cls, data):
        raise NotImplementedError()

    def dump(self):
        raise NotImplementedError()


class AbstractOgameObjConstruct(Collection):

    @property
    def registry(self):
        raise NotImplementedError("collection need a registry of obj to list")

    @classmethod
    def load(cls, data):
        new_col = cls()
        for key, sub_elem_cls in new_col.registry.items():
            if key in data:
                new_col.add(sub_elem_cls(**data[key]))
        return new_col

    def dump(self):
        return {key: value.dump() for key, value in self.data.items()}


class ConstructCollection(AbstractOgameObjConstruct):

    def __init__(self, data=None):
        super().__init__(data)
        data = data or {}
        for key in self.registry:
            if key not in data:
                self.add(self.registry[key](0))

    @property
    def registry(self):
        raise NotImplementedError("collection need a registry of obj to list")

    @classmethod
    def load(cls, data):
        new_col = cls()
        for key, sub_elem_cls in new_col.registry.items():
            new_col.add(sub_elem_cls(
                    **(data[key] if key in data else {'level': 0})))
        return new_col

    def add(self, obj):
        if obj.name in self.data:
            self.data[obj.name].level = obj.level
        else:
            self.data[obj.name] = obj.copy()

    def remove(self, obj):
        return self.data.pop(obj.name, None)


class MultiConstructCollection(AbstractOgameObjConstruct):

    @property
    def registry(self):
        raise NotImplementedError("collection need a registry of obj to list")

    def add(self, obj):
        if obj.name in self.data:
            self.data[obj.name].quantity += obj.quantity
        else:
            self.data[obj.name] = obj.copy()

    def remove(self, obj):
        if not obj.quantity:
            self.data.pop(obj.name)
        elif obj.name in self.data:
            if self.data[obj.name].quantity > obj.quantity:
                self.data[obj.name].quantity -= obj.quantity
            elif self.data[obj.name].quantity == obj.quantity:
                self.data.pop(obj.name)
            else:
                logger.error("Can't remove more than %r from %r (trying %r)",
                             self.data[obj.name], self, obj)
                self.data.pop(obj.name)
