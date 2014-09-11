import os
import json
import logging
from datetime import datetime

from pyogame.tools.const import CONF_PATH
from pyogame.planet_collection import PlanetCollection
from pyogame.interface import Interface

CACHE_PATH_TEMPLATE = 'cache.json'
logger = logging.getLogger(__name__)


class Factory(object):
    _instances = {}
    _conf = {}

    def __init__(self, username=None, conf_path=CONF_PATH):
        if not username and not 'current_user' in self._conf:
            raise
        with open(conf_path) as conf_file:
            self._conf.update(json.load(conf_file))
        if username is not None:
            self._conf['current_user'] = username

    def get_instance(self, cls):
        key = '%s.%s' % (self.username, cls.__name__)
        if key in self._instances:
            return False, self._instances[key]
        self._instances[key] = cls(**self.conf)
        return True, self._instances[key]

    @property
    def username(self):
        return self._conf['current_user']

    @property
    def conf(self):
        return self._conf.get(self.username, {})

    @property
    def empire(self):
        new, empire = self.get_instance(PlanetCollection)
        if not new:
            return empire

        empire.capital_coords = self.conf.get('capital')
        empire.loaded = False
        logger.debug('Loading objects from %r', CACHE_PATH_TEMPLATE)
        try:
            cache = self.load().get(self.username, None)
            if not cache:
                return empire
            empire.load(**cache)
        except ValueError:
            logger.error('Cache has been corrupted, ignoring it')
            return empire
        empire.loaded = True
        return empire

    @property
    def interface(self):
        new, interface = self.get_instance(Interface)
        return interface

    def load(self):
        if not os.path.exists(CACHE_PATH_TEMPLATE):
            logger.debug('No cache file found at %r', CACHE_PATH_TEMPLATE)
            return {}
        with open(CACHE_PATH_TEMPLATE, 'r') as fp:
            return json.load(fp)

    def dump(self):
        logger.debug('Dumping objects to %r', CACHE_PATH_TEMPLATE)
        cache = self.load()
        cache[self.username] = self.empire.dump()
        handler = lambda o: o.isoformat() if isinstance(o, datetime) else None
        with open(CACHE_PATH_TEMPLATE, 'w') as fp:
            json.dump(cache, fp, indent=2,
                      separators=(',', ': '), default=handler)
