# -*- coding: utf-8 -*-
import logging

from pyogame.planets import Empire

logger = logging.getLogger(__name__)


def rapatriate(interface, destination=None):
    logger.info('launching rapatriation to %r' % destination)
    if not destination:
        assert Empire.capital
        destination = Empire.capital
    for colony in Empire.colonies:
        if destination is colony:
            continue
        try:
            interface.send_resources(colony, destination, all_ships=True)
        except Exception:
            logger.exception('An error occured during rapatriation:')
