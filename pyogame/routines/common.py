# -*- coding: utf-8 -*-
import logging

from pyogame.empire import empire
from pyogame.ships import Probes, Recycler

logger = logging.getLogger(__name__)


def transport(interface, src, dst, all_ships=False, resources=None):
    res_msg = ''
    if not resources:
        resources = src.resources
        res_msg = 'all resources '
    resources = resources.movable
    res_msg += repr(resources)

    if all_ships:
        fleet = src.fleet
    else:
        fleet = src.fleet.transports.for_moving(resources)

    sent_fleet = interface.send_fleet(src, dst, 'transport', fleet, resources)
    logger.warn('Moving %s from %r to %r arriving at %s'
            % (res_msg, src, dst, sent_fleet.arrival_time.isoformat()))
    return empire.missions.add(fleet=sent_fleet)


def spy(interface, src, dst, nb_probe=1):
    fleet = src.fleet.of_type(Probes)
    assert fleet, 'no probes on %r' % src
    assert nb_probe <= fleet.first().quantity, 'not enough probes on %r' % src
    fleet.first().quantity = nb_probe
    sent_fleet = interface.send_fleet(src, dst, 'spy', fleet)
    logging.warn('Spying on %r (arriving at %r)'
            % (dst, sent_fleet.arrival_time))
    return empire.missions.add(fleet=sent_fleet)


def recycle(interface, src, dst, nb_recycler=2):
    fleet = src.fleet.of_type(Recycler)
    assert fleet, 'no recycler on %r' % src
    assert nb_recycler <= fleet.first().quantity, \
            'not enough recyclers on %r' % src
    fleet.first().quantity = nb_recycler
    sent_fleet = interface.send_fleet(src, dst, 'recycler', fleet,
            dtype='debris')
    logging.warn('Going to recycle debris at %r (arriving at %r)'
            % (dst, sent_fleet.arrival_time))
    return empire.missions.add(fleet=sent_fleet)
