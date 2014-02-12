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

    if args.rapatriate:
        routines.civil.rapatriate(session)
    elif args.construct:
        routines.civil.plan_construction(session)
    elif args.probes:
        scenarii.probe_idles(session, args.probes)
    elif args.recycle:
        scenarii.recycle(session, args.recycle)
    elif args.idles :
        scenarii.attack_idles(session)
    elif args.build:
        scenarii.specific_construction(session, args.build)
    else:
        session.crawl(building=True, fleet=True, station=True)
        session.update_empire_overall()
        routines.civil.in_place_empire_upgrade(session)
        routines.civil.resources_reception_and_construction(session)
        routines.civil.rapatriate(session)
        routines.civil.plan_construction(session)
    session.dump()

# vim: set et sts=4 sw=4 tw=120:
