#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Outil en ligne de commande pour inscrire des actions
à exécuter ou pour les exécuter directement.
"""
from pyogame import utils, scenarii


if __name__ == "__main__":
    args, logfile, loglevel = utils.parse_args()

    session = utils.load_conf(args.user, logfile, loglevel)

    if args.rapatriate:
        scenarii.rapatriate(session)
    elif args.construct:
        scenarii.plan_construction(session)
    elif args.probes:
        scenarii.probe_idles(session, args.probes)
    elif args.idles :
        scenarii.attack_idles(session)
    elif args.build:
        scenarii.specific_construction(session, args.build)
    else:
        session.crawl(building=True, fleet=True, station=True)
        session.update_empire_overall()
        scenarii.resources_reception_and_construction(session)
        scenarii.rapatriate(session)
        scenarii.upgrade_empire(session)
    session.dump()

# vim: set et sts=4 sw=4 tw=120:
