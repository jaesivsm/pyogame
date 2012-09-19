#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Outil en ligne de commande pour inscrire des actions
à exécuter ou pour les exécuter directement.
"""
import json
import lib_ogame

CONF_PATH = 'conf.json'


if __name__ == "__main__":
    with open(CONF_PATH) as conf_file:
        conf = json.load(conf_file)

    session = lib_ogame.Ogame(conf['mother'], conf['planets'])
    session.login(conf['username'], conf['password'])
    session.rapatriate(conf['mother'])
# vim: set et sts=4 sw=4 tw=120:
