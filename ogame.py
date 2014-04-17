#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Outil en ligne de commande pour inscrire des actions
à exécuter ou pour les exécuter directement.
"""
from pyogame import tools, scenarii, routines


if __name__ == "__main__":
    args, logfile, loglevel = tools.parse_args()
    factory = tools.Factory(args.user)
    logger = tools.set_logger(logfile, args.user, loglevel)

    if args.ui:
        if args.ui == 'overall':
            tools.ui.print_overall_status()
        elif args.ui == 'toconstruct':
            tools.ui.print_to_construct()
        else:
            tools.ui.unknown_display(args.ui)

    factory.interface.login()
    factory.interface.update_empire_overall()
    if args.rapatriate:
        factory.interface.crawl(fleet=True)
        routines.civil.rapatriate()
    if args.construct:
        routines.civil.plan_construction()
    if args.probes:
        factory.interface.crawl(fleet=True)
        routines.guerrilla.check_neighborhood(
                [args.area_start, args.area_end],
                routines.guerrilla.SPY)
    if args.recycle:
        factory.interface.crawl(fleet=True)
        routines.guerrilla.check_neighborhood(
                [args.area_start, args.area_end],
                routines.guerrilla.RECYCLE)
    if args.idles:
        scenarii.attack_idles()
    if args.build:
        scenarii.specific_construction(args.build)
    if not (args.rapatriate or args.construct or args.probes
            or args.recycle or args.idles or args.build):
        factory.interface.crawl(building=True, fleet=True, station=True)
        routines.civil.in_place_empire_upgrade()
        routines.civil.resources_reception_and_construction()
        routines.civil.rapatriate()
        routines.civil.plan_construction()
    factory.interface.stop()
    factory.dump()

# vim: set et sts=4 sw=4 tw=120:
