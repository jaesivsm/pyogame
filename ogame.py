#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Outil en ligne de commande pour inscrire des actions
à exécuter ou pour les exécuter directement.
"""
from pyogame import tools, routines


def main(factory, args):
    factory.interface.login()
    factory.interface.update_empire_overall()
    factory.interface.crawl(building=True, fleet=True, station=True)
    if args.rapatriate:
        routines.civil.rapatriate()
    if args.construct:
        routines.civil.in_place_empire_upgrade()
        routines.civil.resources_reception_and_construction()
        routines.civil.plan_construction()
    if args.probes:
        routines.guerrilla.check_neighborhood(
                [args.area_start, args.area_end],
                routines.guerrilla.SPY)
    if args.recycle:
        routines.guerrilla.check_neighborhood(
                [args.area_start, args.area_end],
                routines.guerrilla.RECYCLE)
    if not (args.rapatriate or args.construct or args.probes
            or args.recycle or args.idles or args.build):
        routines.civil.in_place_empire_upgrade()
        routines.civil.resources_reception_and_construction()
        routines.civil.rapatriate()
        routines.civil.plan_construction()


if __name__ == "__main__":
    args, logfile, loglevel = tools.parse_args()
    logger = tools.set_logger(logfile, args.user, loglevel)

    factory = tools.Factory(args.user)

    if args.ui:
        if args.ui == 'overall':
            tools.ui.print_overall_status()
        elif args.ui == 'toconstruct':
            tools.ui.print_to_construct()
        else:
            tools.ui.unknown_display(args.ui)

    if args.build:
        plan = args.build.split('-')
        construct_name, level, planet_key = None, None, None
        if len(plan) == 2:
            construct_name, level = plan
        elif len(plan) == 3:
            construct_name, level, planet_key = plan
        level = int(level) if level else None
        if planet_key is not None:
            for planet in factory.empire:
                if planet.key == planet_key:
                    planet.add_construction_plan(construct_name, level)
        elif construct_name is not None and level is not None:
            factory.empire.capital.add_construction_plan(construct_name, level)

    if not args.do_nothing:
        try:
            factory.interface.start()
            main(factory, args)
        finally:
            factory.interface.stop()
    factory.dump()

# vim: set et sts=4 sw=4 tw=120:
