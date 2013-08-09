#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Outil en ligne de commande pour inscrire des actions
à exécuter ou pour les exécuter directement.
"""
import sys
import json
import logging

from pyogame import interface, utils

logger = logging.getLogger('pyogame')
CONF_PATH = 'conf.json'


if __name__ == "__main__":
    user, logfile, loglevel = utils.parse_args()
    utils.set_logger(logfile, loglevel)

    with open(CONF_PATH) as conf_file:
        conf = json.load(conf_file)

    if user not in conf:
        logger.error('Account %r unknown' % user)
        exit(1)
    else:
        session = interface.Ogame(conf[user])
        session.rapatriate()

# vim: set et sts=4 sw=4 tw=120:
