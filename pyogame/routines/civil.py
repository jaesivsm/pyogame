# -*- coding: utf-8 -*-
import logging

from pyogame.routines.common import transport

logger = logging.getLogger(__name__)


def in_place_empire_upgrade(interface, empire, construct_on_capital=True):
    logger.debug('### In place empire upgrade')
    for planet in empire.idles:
        if planet.capital and not construct_on_capital:
            continue
        logger.debug('%r > %r = %r', planet.resources, planet.to_construct.cost,
                     planet.resources >= planet.to_construct.cost)
        if planet.resources >= planet.to_construct.cost:
            logger.warning("Resources are available on %s to construct %s "
                           "(lvl %d)", planet, planet.to_construct.name,
                           planet.to_construct.level + 1)
            interface.construct(planet.to_construct, planet)


def rapatriate(interface, empire, destination=None):
    logger.debug('### rapatriate')
    if not destination and empire.capital:
        destination = empire.capital
    assert destination, "Empire has no capital " \
            "and no destination has been provided"
    logger.info('Launching rapatriation to %s', destination)
    for source in empire:
        if destination is source:
            continue
        if not source.fleet:
            logger.info('no fleet on %s', source)
            continue
        if float(source.resources.total) / source.fleet.capacity < 2. / 3 \
                and not source.is_metal_tank_full \
                and not source.is_crystal_tank_full \
                and not source.is_deuterium_tank_full:
            logger.info('not enough resources on %s to bother repatriating',
                        source)
            continue
        transport(interface, empire, source, destination, all_ships=True)


def plan_construction(interface, empire, construct_on_capital=True):
    logger.debug('### plan construction')
    source = empire.capital
    while True:
        planet = empire.idles.cheapest(construct_on_capital)
        if not planet:
            logger.info("No eligible planet for construction")
            break
        cost = planet.to_construct.cost
        logger.info("Willing to construct %s on %s for %s",
                    planet.to_construct, planet, cost.movable)

        if source.resources.movable < cost.movable:
            logger.info("Not enough resources on %s (having %s)",
                        source, source.resources.movable)
            break
        if source.fleet.capacity < cost.movable.total:
            logger.info("Fleet capacity too low on %s (able to move %s)",
                        source, source.fleet.capacity)
            break

        logger.warning('Sending resources to construct %s on %s',
                       planet.to_construct, planet)
        travel_id = transport(interface, empire,
                              source, planet, resources=cost)

        planet.waiting_for[travel_id] = planet.to_construct.name


def resources_reception_and_construction(interface, empire):
    logger.debug('### Resources reception and construction')
    waited_constructs = {}

    for fleet in empire.missions.arrived:
        if not fleet.travel_id in empire.waiting_for:
            continue  # no one cares about this fleet
        planet = empire.cond(key=fleet.dst).first
        assert planet, "no planet at %s" % fleet.dst
        if not planet.idle:  # construction has began
            continue
        if not fleet.dst in waited_constructs:
            waited_constructs[fleet.dst] = []
        # we list the constructions fleets have delivered resources for
        logger.info('A fleet has arrived on %s to construct %s',
                    planet, planet.waiting_for[fleet.travel_id])
        waited_constructs[planet.key].append(
                planet.waiting_for[fleet.travel_id])

    for planet in empire:
        if not planet.key in waited_constructs:
            continue
        for construct in set(waited_constructs[planet.key]):
            # we count how many constructions resources
            # have been delivered for on this planet
            waited_constr = waited_constructs[planet.key].count(construct)
            # we count how many of this construction are waiting on this planet
            waited_travel = planet.waiting_for.values().count(construct)
            if waited_constr == waited_travel:
                logger.warning("All fleet arrived to construct %s on %s, "
                               "launching construction.", construct, planet)
                interface.construct(construct, planet)
                for travel_id, c in planet.waiting_for.items():
                    if c == construct:
                        del planet.waiting_for[travel_id]
