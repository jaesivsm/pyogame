# -*- coding: utf-8 -*-
import re
import logging
from selenium import selenium

from pyogame.empire import Empire
from pyogame.planet import Planet
from pyogame.const import PAGES, RES_TYPES

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
        logger.info('updating resources on planet %r' % planet)
        try:
            for res_type in RES_TYPES:
                res = self.__split_text("//li[@id='%s_box']" % res_type, '.')
                planet.resources[res_type[:-4]] = int(''.join(res))
        except Exception:
            logger.exception("ERROR: Couldn't update resources")

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
        logger.debug('Going to page %r on %r' % (page, planet))
        if planet is not None and self.current_planet is not planet:
            logger.info('Going to planet %r' % planet)
            self.click("//div[@id='planetList']/div[%d]/a" % (planet.position))
            self.current_planet = planet
            self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        if page is not None and self.current_page != page:
            logger.info('Going to page %r' % page)
            self.click("link=%s" % page)
            self.current_page = page
            self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.update_planet_resources(planet)
        if self.current_page == PAGES['resources']:
            self.update_planet_resources(planet)
        elif self.current_page == PAGES['fleet']:
            self.update_planet_fleet(planet)

    def send_resources(self, src, dst, all_ships=False, **kwargs):
        resources, all_resources = {}, False
        self.go_to(src, PAGES['fleet'])
        for res_type in RES_TYPES:
            if res_type in kwargs:
                resources[res_type] = kwargs[res_type]
        all_resources = not resources

        if not src.fleet.transports:
            logger.warn("No ships on %r, can't move resources" % src)
            return

        if all_ships:
            for ships in src.fleet.transports:
                self.click(ships.xpath)
        else:
            sum_resources = sum(
                    [res for res in (resources or src.resources).values()])
            for ships in src.fleet.transports.for_moving(sum_resources):
                self.type('id=%s' % ships.ship_id, ships.quantity)

        self.click("css=#continue > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.type("id=galaxy", dst.coords[0])
        self.type("id=system", dst.coords[1])
        self.type("id=position", dst.coords[2])
        self.click("id=pbutton")
        self.click("css=#continue > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.click("css=#missionButton3")
        if all_resources:
            self.click("css=#allresources > img")
        else:
            for res_type, quantity in resources.items():
                self.type('id=%s' % res_type, quantity)

        self.click("css=#start > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)
        self.update_planet_fleet(src)

# vim: set et sts=4 sw=4 tw=120:
