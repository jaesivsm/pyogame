import os
import json
import logging
from datetime import datetime

from pyogame.tools.const import CONF_PATH
from pyogame.planet_collection import PlanetCollection
from pyogame.interface import Interface

CACHE_PATH_TEMPLATE = 'cache.json'
logger = logging.getLogger(__name__)

_CONTEXTES = {}


def get_context(username, conf_path=CONF_PATH):
    if username not in _CONTEXTES:
        _CONTEXTES[username] = Context(username, conf_path)
    return _CONTEXTES[username]


class Context:

    def __init__(self, username=None, conf_path=CONF_PATH):
        self._username = username
        self._conf_path = conf_path
        self._interface = None
        self._empire = None
        self._conf = None

    @property
    def interface(self):
        if self._interface is None:
            self._interface = Interface(**self.conf)
        return self._interface

    @property
    def conf(self):
        if self._conf is None:
            with open(self._conf_path) as fd:
                self._conf = json.load(fd)[self._username]
        return self._conf

    @property
    def empire(self):
        if self._empire:
            return self._empire

        logger.debug('Loading objects from %r', CACHE_PATH_TEMPLATE)
        self._empire = PlanetCollection({}, capital=self.conf.get('capital'))

        try:
            cache = self.load().get(self._username, None)
            if not cache:
                return self._empire
            self._empire.load(cache)
        except ValueError:
            logger.error('Cache has been corrupted, ignoring it')
            return self._empire
        return self._empire

    @staticmethod
    def load():
        if not os.path.exists(CACHE_PATH_TEMPLATE):
            logger.debug('No cache file found at %r', CACHE_PATH_TEMPLATE)
            return {}
        with open(CACHE_PATH_TEMPLATE, 'r') as fp:
            return json.load(fp)

    def dump(self):
        logger.debug('Dumping objects to %r', CACHE_PATH_TEMPLATE)
        cache = self.load()
        cache[self._username] = self.empire.dump()
        handler = lambda o: o.isoformat() if isinstance(o, datetime) else None
        with open(CACHE_PATH_TEMPLATE, 'w') as fp:
            json.dump(cache, fp, indent=2,
                      separators=(',', ': '), default=handler)
