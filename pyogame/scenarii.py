# -*- coding: utf-8 -*-
import logging

from pyogame.empire import empire
from pyogame.routines import guerrilla

logger = logging.getLogger(__name__)


def probe_idles(interface, wideness) :
    guerrilla.check_neighborhood(interface, wideness, 'spy')


def recycle(interface, wideness) :
    guerrilla.check_neighborhood(interface, wideness, 'recycle')


def attack_idles(interface) :
    pass


def display_messages(interface) :
    pass


def specific_construction(interface, to_build) :
    position, construction = to_build.split('/')
    try:
        for planet in empire:
            if planet.position == int(position):
                interface.construct(construction, planet)
                return True
        logger.critical('No planet at position %r' % position)
    except AssertionError, error:
        logger.critical(str(error))
    return False


def specific_research(interface, to_build) :
    return False
