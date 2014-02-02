# -*- coding: utf-8 -*-
import logging

from pyogame.empire import empire

logger = logging.getLogger(__name__)


def rapatriate(interface, destination=None):
    logger.info('launching rapatriation to %r' % destination)
    if not destination and empire.capital:
        destination = empire.capital
    assert destination, "Empire has no capital " \
            "and no destination has been provided"
    for source in empire:
        if destination is source:
            continue
        interface.send_resources(source, destination, all_ships=True)
