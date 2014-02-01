# -*- coding: utf-8 -*-
import logging

from pyogame.empire import empire

logger = logging.getLogger(__name__)


def rapatriate(interface, destination=None):
    logger.info('launching rapatriation to %r' % destination)
    if not destination:
        assert empire.capital, "Empire has no capital " \
                "and no destination has been provided"
        destination = empire.capital
    for colony in empire.colonies:
        if destination is colony:
            continue
        try:
            interface.send_resources(colony, destination, all_ships=True)
        except Exception:
            logger.exception('An error occured during rapatriation:')
