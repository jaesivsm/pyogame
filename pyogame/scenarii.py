# -*- coding: utf-8 -*-
import logging

from pyogame import const
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
        interface.go_to(source, const.PAGES['fleet'])
        if not source.fleet:
            continue
        interface.send_resources(source, destination, all_ships=True)


def plan_construction(interface):
    planet = empire.idles.cheapest
    logger.warn('Will try to construct %r on %r'
            % (planet.to_construct, planet))
    assert planet.to_construct.cost.movable < empire.capital.resources, \
            "Not enough ressources on capital"
    assert planet.to_construct.cost.movable.total < \
            empire.capital.fleet.capacity, "Fleet capacity too low on capital"
    travel_id = interface.send_resources(empire.capital, planet,
            resources=empire.cheapest.to_construct.cost)

    planet.add_flag(const.WAITING_RES,
            {travel_id: empire.cheapest.to_construct.building_attr})


def resources_reception_and_construction(interface):
    pass

