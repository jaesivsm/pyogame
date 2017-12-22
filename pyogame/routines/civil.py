# -*- coding: utf-8 -*-
import logging

from pyogame.routines.common import transport

logger = logging.getLogger(__name__)


def in_place_empire_upgrade(interface, empire):
    logger.debug('### In place empire upgrade')
    tech_plans = list(empire.planner_next_plans)
    construct_on_capital = len(empire) > 1
    if not empire.is_researching and tech_plans:
        for plan in tech_plans:
            if plan.cost <= empire.capital.resources:
                logger.warning("Resources are available on %s to construct %s "
                               "(lvl %d)", empire.capital, plan.name,
                               plan.level + 1)
                interface.construct(plan, empire.capital)
                break
    for planet in empire.idles:
        if planet.capital and not construct_on_capital:
            continue
        launched, have_plans = False, False
        for plan in planet.planner_next_plans:
            have_plans = True
            logger.debug('%r > %r = %r', planet.resources, plan.cost,
                         planet.resources >= plan.cost)
            if plan.cost <= planet.resources:
                logger.warning("Resources are available on %s to realise "
                               "plan %s (lvl %d)", planet, plan.name,
                                plan.level)

                launched = True
                interface.construct(plan, planet)
                break
        if launched:
            continue
        if have_plans:
            logger.info("Won't construct on %r, planet have plans", planet)
            continue

        for construct in planet.to_construct:
            logger.debug('%r > %r = %r', planet.resources,
                        construct.cost, planet.resources >= construct.cost)
            if planet.resources >= construct.cost:
                logger.warning("Resources are available on %s to construct %s "
                               "(lvl %d)", planet, construct.name,
                               construct.level)
                interface.construct(construct, planet)
                break


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


def plan_construction(interface, empire):
    logger.debug('### plan construction')
    source = empire.capital
    construct_on_capital = len(empire) > 1
    while True:
        planet, construct = empire.idles.cheapest(construct_on_capital)
        if not planet:
            logger.info("No eligible planet for construction")
            break

        cost = construct.cost
        logger.info("Willing to construct %s on %s for %s",
                    construct, planet, cost.movable)

        if source.resources.movable < cost.movable:
            logger.info("Not enough resources on %s (having %s)",
                        source, source.resources.movable)
            break
        if source.fleet.capacity < cost.movable.total:
            logger.info("Fleet capacity too low on %s (able to move %s)",
                        source, source.fleet.capacity)
            break

        logger.warning('Sending resources to construct %s on %s',
                    construct, planet)
        travel_id = transport(interface, empire,
                            source, planet, resources=cost)

        planet.waiting_for[travel_id] = construct.name


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
            waited_travel = list(planet.waiting_for.values()).count(construct)
            if waited_constr == waited_travel:
                logger.warning("All fleet arrived to construct %s on %s, "
                               "launching construction.", construct, planet)
                interface.construct(
                        planet.constructs.cond(name=construct).first,
                        planet)
                for travel_id in [travel_id
                                  for travel_id in planet.waiting_for
                                  if construct == planet.waiting_for[travel_id]
                                  ]:
                    planet.waiting_for.pop(travel_id, None)
