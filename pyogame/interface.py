# -*- coding: utf-8 -*-
import re
import logging
from selenium import selenium

from pyogame.planets import Empire, Planet
from pyogame.const import PAGES

logger = logging.getLogger(__name__)
DEFAULT_WAIT_TIME = 40000


class Interface(selenium):

    def __init__(self, conf_dict={}):
        needed = ['user', 'password', 'univers']
        self._conf_dict =  conf_dict
        for key in needed:
            assert key in conf_dict, "configuration dictionnary must at " \
                    "least own the following keys: " + ", ".join(needed)
            setattr(self, key, conf_dict[key])

        selenium.__init__(self,
                "localhost", 4444, "*chrome", "http://ogame.fr/")
        self.current_planet = None
        self.current_page = None
        self.start()

        logger.info('Logging in with identity %r' % self.user)
        self.open("http://ogame.fr/")
        self.click("id=loginBtn")
        self.select("id=serverLogin", "label=%s" % self.univers)
        self.type("id=usernameLogin", self.user)
        self.type("id=passwordLogin", self.password)
        self.click("id=loginSubmit")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.discover()

    def __del__(self):
        self.stop()

    def __split_text(self, xpath, split_on='\n'):
        return self.get_text(xpath).split(split_on)

    def update_planet_resources(self, planet=None):
        planet = planet if planet is not None else self.current_planet
        logger.info('updating ressources on planet %r' % planet)
        try:
            for res_type in ['metal_box', 'crystal_box',
                    'deuterium_box', 'energy_box']:
                res = self.__split_text("//li[@id='%s']" % res_type, '.')
                planet.ressources[res_type[:-4]] = int(''.join(res))
        except Exception:
            logger.exception("ERROR: Couldn't update ressources")

    def update_planet_buildings(self, planet=None):
        planet = planet if planet is not None else self.current_planet
        if self.current_page != PAGES['resources']:
            self.go_to(planet, PAGES['resources'])
        logger.info('updating buildings states for %r' % planet)
        planet.constructs = {}
        try:
            for ctype in ('building', 'storage'):
                for const in self.__split_text("//ul[@id='%s']" % ctype):
                    if not const.strip():
                        continue
                    planet.constructs[ctype] = {}
                    name, level = const.strip().rsplit(' ', 1)
                    planet.constructs[ctype][name] \
                            = int(''.join(level.split('.')))
        except Exception:
            logger.exception("ERROR: Couldn't update building states")

    def update_planet_fleet(self, planet=None):
        planet = planet if planet is not None else self.current_planet
        if self.current_page != PAGES['fleet']:
            self.go_to(planet, PAGES['fleet'])
        logger.info('updating fleet states on %r' % planet)
        for fleet_type in ('military', 'civil'):
            try:
                for fleet in self.__split_text("//ul[@id='%s']" % fleet_type):
                    name, quantity = fleet.strip().rsplit(' ', 1)
                    planet.fleet.add(name.encode('utf8'), int(quantity))
            except Exception, error:
                if "//ul[@id='" in str(error) and "not found" in str(error):
                    logger.debug('No %s fleet on %r' % (fleet_type, planet))
                    continue
                logger.error("ERROR: Couldn't update fleet states")
                raise error
        logger.debug('%s got fleet %s' % (planet, planet.fleet))

    def discover(self, full=False):
        logger.info('Getting list of colonized planets')
        xpath = "//div[@id='planetList']"
        capital = self._conf_dict['capital'] \
                if 'capital' in self._conf_dict else None
        for position, planet in enumerate(self.__split_text(xpath)):
            name, coords = re.split('\[?\]?', planet.split('\n')[0])[:2]
            planet = Planet(name.strip(), coords, position + 1)
            if capital and planet.coords == capital:
                planet.is_capital = True
            Empire.add(planet)

            if not full:
                continue
            self.go_to(planet)
            self.update_planet_fleet()

    def go_to(self, planet=None, page=None):
        logger.info('Going to page %r on %r' % (page, planet))
        if planet is not None and self.current_planet is not planet:
            self.click("//div[@id='planetList']/div[%d]/a" % (planet.position))
            self.current_planet = planet
            self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        if page is not None and self.current_page != page:
            self.click("link=%s" % page)
            self.current_page = page
            self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.update_planet_resources(planet)
        if page == PAGES['resources']:
            self.update_planet_resources(planet)
        elif page == PAGES['fleet']:
            self.update_planet_fleet(planet)

    def send_ressources(self, src, dst, content={}):
        #metal = content.get('metal', 'all')
        #cristal = content.get('cristal', 'all')
        #deut = content.get('deut', 'all')
        logger.info('sending all possible ressources from %r to %r'
                % (src, dst))

        self.go_to(src, PAGES['fleet'])
        if not src.fleet:
            logger.warn("No ships on %r, can't move ressources" % src)
            return
        self.click("//ul[@id='civil']/li[2]/div/a")
        self.click("css=#continue > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.type("id=galaxy", dst.coords[0])
        self.type("id=system", dst.coords[1])
        self.type("id=position", dst.coords[2])
        self.click("id=pbutton")
        self.click("css=#continue > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.click("css=#missionButton3")
        #if metal == 'all' and cristal == 'all' and deut == 'all':
        self.click("css=#allresources > img")
        self.click("css=#start > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)
        self.update_planet_fleet(src)

# vim: set et sts=4 sw=4 tw=120:
