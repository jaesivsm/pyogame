# -*- coding: utf-8 -*-
import logging

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
            resources=planet.to_construct.cost)

    planet.waiting_for[travel_id] = planet.to_construct.building_attr


def upgrade_empire(interface):
    interface.crawl(building=True, fleet=True)
    interface.update_empire_overall()
    while True:
        try:
            plan_construction(interface)
        except AssertionError:
            break


def resources_reception_and_construction(interface):
    waited_constructs = {}

    for fleet in empire.missions.arrived:
        if not fleet.travel_id in empire.waiting_for:
            continue  # no one cares about this fleet
        planet = empire.planets[fleet.to_pl]
        if not planet.idle:  # construction has began
            continue
        if not fleet.to_pl in waited_constructs:
            waited_constructs[fleet.to_pl] = []
        # we list the constructions fleets have delivered resources for
        waited_constructs[fleet.to_pl].append(
                planet.waiting_for[fleet.travel_id])

    for planet in empire:
        if not planet.position in waited_constructs:
            continue
        for construct in set(waited_constructs[planet.position]):
            # we count how many constructions resources
            # have been delivered for on this planet
            waited_constr = waited_constructs[planet.position].count(construct)
            # we count how many of this construction are waiting on this planet
            waited_travel = planet.waiting_for.values().count(construct)
            if waited_constr == waited_travel:
                interface.construct(construct, planet)
                for travel_id, c in planet.waiting_for.items():
                    if c == construct:
                        del planet.waiting_for[travel_id]

    interface.update_empire_overall()


def default_actions(interface):
    resources_reception_and_construction(interface)
    rapatriate(interface)
    upgrade_empire(interface)


def probe_idles(interface) :
    interface.go_to(empire.capital, 'galaxy')
    interface.go_to(empire.capital, 'fleet1')
    pass

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
