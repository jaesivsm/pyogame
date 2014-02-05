# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from pyogame.empire import empire

logger = logging.getLogger(__name__)


def rapatriate(interface, destination=None):
    if not destination and empire.capital:
        destination = empire.capital
    assert destination, "Empire has no capital " \
            "and no destination has been provided"
    logger.info('Launching rapatriation to %r' % destination)
    for source in empire:
        if destination is source:
            logger.info('Destination is Source')
            continue
        interface.go_to(source, 'fleet1')
        if not source.fleet:
            continue
        interface.send_resources(source, destination, all_ships=True)


def plan_construction(interface):
    planet = empire.idles.cheapest
    if planet is None :
        logger.info('All planets are constructing')
        exit(1)
    logger.warn('Will try to construct %r on %r'
            % (planet.to_construct, planet))
    assert planet.to_construct.cost.movable < empire.capital.resources, \
            "Not enough ressources on capital"
    assert planet.to_construct.cost.movable.total < \
            empire.capital.fleet.capacity, "Fleet capacity too low on capital"
    travel_id = interface.send_resources(empire.capital, planet,
            resources=empire.cheapest.to_construct.cost)

    planet.waiting_for[travel_id] = empire.cheapest.to_construct.building_attr


def resources_reception_and_construction(interface):
    now = datetime.now()
    to_dels, to_construct = [], {}

    for travel_id, flying_fleet in empire.flying_fleets.items():
        if flying_fleet['arrival_time'] < now:
            continue
        to_dels.append(travel_id)
        planet = empire.planets[flying_fleet.to_pl]
        to_construct[flying_fleet.to_pl] = planet.waiting_for[travel_id]
        del planet.waiting_for[travel_id]

    for to_del in to_dels:
        del empire.flying_fleets[to_del]

    for position, construct in to_construct.items():
        planet = empire.planets[position]
        if construct in planet.waiting_for.values():
            continue  # waiting for other fleet
        interface.construct(construct, planet)


def probe_inactives(interface) :
    interface.go_to(empire.capital, 'fleet1')
    pass

def specific_construction(interface, to_build) :
    what, where = to_build.split('/')
    notFound = True
    for planet in empire:
        if planet.name == where:
            notFound = False
            if what == 'M' :
                construction = planet.metal_mine
            elif what == 'C' :
                construction = planet.crystal_mine
            elif what == 'D' :
                construction = planet.deuterium_synthetize
            elif what == 'S' :
                construction = planet.solar_plant
            else:
                logger.info('Please enter M, C, D or S to build')
            interface.construct(construction, planet)
    if notFound:
        logger.info('Planet not found')
    pass
