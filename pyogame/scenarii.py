# -*- coding: utf-8 -*-
import logging

from pyogame.tools.factory import Factory

logger = logging.getLogger(__name__)


def attack_idles(interface) :
    pass


def display_messages(interface) :
    pass


def specific_construction(to_build) :
    position, construction = to_build.split('/')
    factory = Factory()
    try:
        for planet in factory.empire:
            if planet.position == int(position):
                factory.interface.construct(construction, planet)
                return True
        logger.critical('No planet at position %r' % position)
    except AssertionError, error:
        logger.critical(str(error))
    return False


def specific_research(interface, to_build) :
    return False
