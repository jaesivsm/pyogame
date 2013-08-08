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
    utils.set_logger()


    with open(CONF_PATH) as conf_file:
        conf = json.load(conf_file)

    if len(sys.argv) < 2:
        logger.error('You must precise an account name')
        exit(1)
    elif sys.argv[1] not in conf:
        logger.error('Account %r unknown' % sys.argv[1])
        exit(2)
    else:
        session = interface.Ogame(conf[sys.argv[1]])
        session.rapatriate()
# vim: set et sts=4 sw=4 tw=120:
