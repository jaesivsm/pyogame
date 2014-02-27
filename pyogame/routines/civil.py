# -*- coding: utf-8 -*-
import logging

from pyogame.empire import empire
from pyogame.routines.common import transport

logger = logging.getLogger(__name__)


def in_place_empire_upgrade(interface):
    for planet in empire.idles:
        if planet.resources > planet.to_construct.cost:
            logger.warn('Resources are available on %r to construct %r'
                    % (planet, planet.to_construct))
            interface.construct(planet.to_construct, planet)


def rapatriate(interface, destination=None):
    if not destination and empire.capital:
        destination = empire.capital
    assert destination, "Empire has no capital " \
            "and no destination has been provided"
    logger.info('Launching rapatriation to %r' % destination)
    for source in empire:
        if destination is source:
            continue
        if not source.fleet:
            logger.debug('no fleet on %r' % source)
            continue
        if float(source.resources.total) / source.fleet.capacity < 2. / 3:
            logger.debug('not enough resources on %r to bother repatriating'
                    % source)
            continue
        transport(interface, source, destination, all_ships=True)


def plan_construction(interface):
    source = empire.capital
    while True:
        planet = empire.idles.cheapest
        if not planet:
            logger.debug("No eligible planet for construction")
            break
        cost = planet.to_construct.cost
        if source.resources.movable < cost.movable:
            logger.debug("Not enough ressources on %r (%r, %r needed)"
                    % (source, source.resources.movable, cost.movable))
            break
        if source.fleet.capacity < cost.movable.total:
            logger.debug("Fleet capacity too low on %r (%r, %r needed)"
                    % (source, source.fleet.capacity, cost.movable.total))
            break

        logger.warn('Sending resources to construct %r on %r'
                % (planet.to_construct, planet))
        travel_id = transport(interface, source, planet, resources=cost)

        planet.waiting_for[travel_id] = planet.to_construct.name()


def resources_reception_and_construction(interface):
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
        logger.info('A fleet has arrived on %r to construct %r'
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
                logger.warn("All fleet arrived to construct %r on %r, "
                        "launching construction." % (construct, planet))
                interface.construct(construct, planet)
                for travel_id, c in planet.waiting_for.items():
                    if c == construct:
                        del planet.waiting_for[travel_id]
