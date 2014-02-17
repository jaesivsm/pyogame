#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Outil en ligne de commande pour inscrire des actions
à exécuter ou pour les exécuter directement.
"""
from pyogame import tools, scenarii, routines



if __name__ == "__main__":
    args, logfile, loglevel = tools.parse_args()

    session = tools.load_conf(args.user, logfile, loglevel)

    session.update_empire_overall()
    if args.rapatriate:
        session.crawl(fleet=True)
        routines.civil.rapatriate(session)
    if args.construct:
        routines.civil.plan_construction(session)
    if args.probes:
        session.crawl(fleet=True)
        scenarii.probe_idles(session, args.probes)
    if args.recycle:
        session.crawl(fleet=True)
        scenarii.recycle(session, args.recycle)
    if args.idles:
        scenarii.attack_idles(session)
    if args.build:
        scenarii.specific_construction(session, args.build)
    if not (args.rapatriate or args.construct or args.probes
            or args.recycle or args.idles or args.build):
        session.crawl(building=True, fleet=True, station=True)
        routines.civil.in_place_empire_upgrade(session)
        routines.civil.resources_reception_and_construction(session)
        routines.civil.rapatriate(session)
        routines.civil.plan_construction(session)
    session.dump()

# vim: set et sts=4 sw=4 tw=120:
