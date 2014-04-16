import os
import json
import logging
from datetime import datetime

from pyogame.tools.const import CONF_PATH
from pyogame.planet_collection import PlanetCollection
from pyogame.interface import Interface

CACHE_PATH_TEMPLATE = '%s.empire.cache'
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
    def cache_path(self):
        return CACHE_PATH_TEMPLATE % self.username

    @property
    def empire(self):
        new, empire = self.get_instance(PlanetCollection)
        if not new:
            return empire

        empire.capital_coords = self.conf.get('capital')
        empire.loaded = False
        if not os.path.exists(self.cache_path):
            logger.debug('No cache file found at %r' % self.cache_path)
            return empire
        logger.debug('Loading objects from %r' % self.cache_path)
        try:
            with open(self.cache_path, 'r') as fp:
                empire.load(**json.load(fp))
        except ValueError:
            logger.error('Cache has been corrupted, ignoring it')
            os.remove(self.cache_path)
            return empire
        empire.loaded = True
        return empire

    @property
    def interface(self):
        new, interface = self.get_instance(Interface)
        return interface

    def dump(self):
        handler = lambda o: o.isoformat() if isinstance(o, datetime) else None
        with open(self.cache_path, 'w') as fp:
            json.dump(self.empire.dump(), fp, default=handler)
