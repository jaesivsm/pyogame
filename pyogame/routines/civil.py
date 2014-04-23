# -*- coding: utf-8 -*-
import logging

from pyogame.tools.factory import Factory
from pyogame.routines.common import transport

logger = logging.getLogger(__name__)


def in_place_empire_upgrade():
    for planet in Factory().empire.idles:
        if planet.resources > planet.to_construct.cost:
            logger.warn('Resources are available on %s to construct %s (lvl %d)'
                    % (planet, planet.to_construct.name,
                       planet.to_construct.level))
            Factory().interface.construct(planet.to_construct, planet)


def rapatriate(destination=None):
    empire = Factory().empire
    if not destination and empire.capital:
        destination = empire.capital
    assert destination, "Empire has no capital " \
            "and no destination has been provided"
    logger.info('Launching rapatriation to %s' % destination)
    for source in empire:
        if destination is source:
            continue
        if not source.fleet:
            logger.info('no fleet on %s' % source)
            continue
        if float(source.resources.total) / source.fleet.capacity < 2. / 3:
            logger.info('not enough resources on %s to bother repatriating'
                    % source)
            continue
        transport(source, destination, all_ships=True)


def plan_construction():
    empire = Factory().empire
    source = empire.capital
    while True:
        planet = empire.idles.cheapest
        if not planet:
            logger.info("No eligible planet for construction")
            break
        cost = planet.to_construct.cost
        logger.info("Willing to construct %s on %s for %s"
                    % (planet.to_construct, planet, cost.movable))

        if source.resources.movable < cost.movable:
            logger.info("Not enough ressources on %s (having %s)"
                    % (source, source.resources.movable))
            break
        if source.fleet.capacity < cost.movable.total:
            logger.info("Fleet capacity too low on %s (able to move %s)"
                    % (source, source.fleet.capacity))
            break

        logger.warn('Sending resources to construct %s on %s'
                % (planet.to_construct, planet))
        travel_id = transport(source, planet, resources=cost)

        planet.waiting_for[travel_id] = planet.to_construct.name


def resources_reception_and_construction():
    waited_constructs = {}
    empire = Factory().empire

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
        logger.info('A fleet has arrived on %s to construct %s'
                    % (planet, planet.waiting_for[fleet.travel_id]))
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
                logger.warn("All fleet arrived to construct %s on %s, "
                        "launching construction." % (construct, planet))
                Factory().interface.construct(construct, planet)
                for travel_id, c in planet.waiting_for.items():
                    if c == construct:
                        del planet.waiting_for[travel_id]
