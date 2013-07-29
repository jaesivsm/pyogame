#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from selenium import selenium

DEFAULT_WAIT_TIME = 40000

class Ogame(selenium):

    def __init__(self, mother=None, planets=[]):
        selenium.__init__(self,
                "localhost", 4444, "*chrome", "http://ogame.fr/")
        self.mother, self.planets = mother, planets
        self.start()

    def __del__(self):
        self.stop()

    def login(self, login, passwd):
        self.open("http://ogame.fr/")
        self.click("id=loginBtn")
        self.select("id=serverLogin", "label=Pegasus")
        self.type("id=usernameLogin", login)
        self.type("id=passwordLogin", passwd)
        self.click("id=loginSubmit")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)
        if not self.planets:
            self.get_planets()

    def update_planet_resources(self, planet):
        planet['resources'] = {}
        for res_type in ['metal_box', 'crystal_box',
                'deuterium_box', 'energy_box']:
            res = self.get_text("//li[@id='%s']" % res_type).split('.')
            planet['resources'][res_type[:-4]] = int(''.join(res))

    def get_planets(self, full=False):
        self.planets, xpath = {}, "//div[@id='planetList']"
        for position, planet in enumerate(self.get_text(xpath).split('\n')):
            name, coords = re.split('\[?\]?', planet.split('\n')[0])[:2]
            self.planets[position + 1] = planet = {'name': name.strip()}
            planet['coords'] = [int(coord) for coord in coords.split(':')]
            planet['position'] = position + 1

            if not full:
                continue

            self.go_to(planet, 'Ressources')

            for const_list in ('building', 'storage'):
                xpath = "//ul[@id='%s']" % const_list
                for const in self.get_text(xpath).split('\n'):
                    if not const.strip():
                        continue
                    planet[const_list] = {}
                    name, level = const.strip().rsplit(' ', 1)
                    planet[const_list][name] = int(''.join(level.split('.')))

    def go_to(self, planet, page):
        self.click("//div[@id='planetList']/div[%d]/a" % (planet['position']))
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)
        self.update_planet_resources(planet)
        self.click("link=%s" % page)
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

    def send_ressources(self, src, dst, content={}):
        #metal = content.get('metal', 'all')
        #cristal = content.get('cristal', 'all')
        #deut = content.get('deut', 'all')

        self.go_to(src, 'Flotte')
        self.click("//ul[@id='civil']/li[2]/div/a")
        self.click("css=#continue > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.type("id=galaxy", dst[0])
        self.type("id=system", dst[1])
        self.type("id=position", dst[2])
        self.click("id=pbutton")
        self.click("css=#continue > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.click("css=#missionButton3")
        #if metal == 'all' and cristal == 'all' and deut == 'all':
        self.click("css=#allresources > img")
        self.click("css=#start > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

    def rapatriate(self, dst=None):
        if not self.planets:
            self.get_planets()
        dst = dst if dst is not None else self.mother
        for src in self.planets.values():
            if dst != src:
                try:
                    self.send_ressources(src, dst)
                except Exception:
                    pass

# vim: set et sts=4 sw=4 tw=120:
