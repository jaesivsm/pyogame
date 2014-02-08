#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Outil en ligne de commande pour inscrire des actions
à exécuter ou pour les exécuter directement.
"""
import logging

from pyogame import utils, scenarii

logger = logging.getLogger('pyogame')


if __name__ == "__main__":
    args, logfile, loglevel = utils.parse_args()

    session = utils.load_conf(args.user, logfile, loglevel)

    if args.rapatriate:
        scenarii.rapatriate(session)
    elif args.construct:
        scenarii.plan_construction(session)
    elif args.probes:
        scenarii.probe_idles(session)
    elif args.build:
        scenarii.specific_construction(session, args.build)
    else:
        scenarii.default_actions(session)

# vim: set et sts=4 sw=4 tw=120:
