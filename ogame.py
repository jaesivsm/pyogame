#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Outil en ligne de commande pour inscrire des actions
à exécuter ou pour les exécuter directement.
"""
import sys
import json

from pyogame import interface, utils

CONF_PATH = 'conf.json'


if __name__ == "__main__":
    with open(CONF_PATH) as conf_file:
        conf = json.load(conf_file)
    user = sys.argv[1]

    utils.set_logger()

    session = interface.Ogame(conf[user]['mother'], conf[user]['planets'])
    session.login(user, conf[user]['password'])
    session.rapatriate()
# vim: set et sts=4 sw=4 tw=120:
