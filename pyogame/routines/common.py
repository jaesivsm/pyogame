# -*- coding: utf-8 -*-
import logging

from pyogame.empire import empire
from pyogame.ships import Probes, Recycler

logger = logging.getLogger(__name__)


def transport(interface, src, dst, all_ships=False, resources=None):
    res_msg = '%s'
    if not resources:
        resources = src.resources
        res_msg = 'all resources (%s)'
    resources = resources.movable
    res_msg = res_msg % resources

    if all_ships:
        fleet = src.fleet.copy()
    else:
        fleet = src.fleet.transports.for_moving(resources)

    sent_fleet = interface.send_fleet(src, dst, 'transport', fleet, resources)
    logger.warn('Moving %s from %s to %s arriving at %s'
            % (res_msg, src, dst, sent_fleet.arrival_time.isoformat()))
    return empire.missions.add(fleet=sent_fleet)


def spy(interface, src, dst, nb_probe=1):
    fleet = src.fleet.of_type(Probes).copy()
    assert fleet.first and nb_probe <= fleet.first.quantity, \
            'not enough probes on %r' % src
    fleet.first.quantity = nb_probe
    sent_fleet = interface.send_fleet(src, dst, 'spy', fleet)
    logger.warn('Spying on %r (arriving at %r)'
            % (dst, sent_fleet.arrival_time))
    return empire.missions.add(fleet=sent_fleet)


def recycle(interface, src, dst, debris_content):
    fleet = src.fleet.of_type(Recycler).copy()
    assert fleet.first, 'no recyclers on %r' % src
    sent_fleet = interface.send_fleet(src, dst, 'recycle',
            fleet.of_type(Recycler).for_moving(debris_content), dtype='debris')
    logger.warn('Going to recycle debris (%s) at %s (arriving at %s)'
            % (debris_content, dst, sent_fleet.arrival_time.isoformat()))
    return empire.missions.add(fleet=sent_fleet)
