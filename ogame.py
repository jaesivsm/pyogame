#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Outil en ligne de commande pour inscrire des actions
à exécuter ou pour les exécuter directement.
"""
import json
import logging

from pyogame import utils, scenarii
from pyogame.interface import Interface

logger = logging.getLogger('pyogame')
CONF_PATH = 'conf.json'


if __name__ == "__main__":
    args, logfile, loglevel = utils.parse_args()
    utils.set_logger(logfile, loglevel)

    with open(CONF_PATH) as conf_file:
        conf = json.load(conf_file)

    if args.user not in conf:
        logger.error('Account %r unknown' % args.user)
        exit(1)
    else:
        session = Interface(conf[args.user])
    if args.rapatriate :
        scenarii.rapatriate(session)
    if args.construct :
        scenarii.plan_construction(session)

# vim: set et sts=4 sw=4 tw=120:
