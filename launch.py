#!/usr/bin/python
import json
import ogame

CONF_PATH = 'conf.json'


if __name__ == "__main__":
	with open(CONF_PATH) as conf:
		conf = json.load(conf)

	session = ogame.Ogame(conf['mother'], conf['planets'])
	session.login(conf['username'], conf['password'])
	session.rapatriate(conf['mother'])
