# -*- coding: utf-8 -*-
import logging
from lxml import html
from selenium import selenium

from pyogame.empire import empire
from pyogame.planet import Planet
from pyogame.constructions import Constructions
from pyogame.const import Resources, PAGES, RES_TYPES

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
        for txt in self.get_text(xpath).split(split_on):
            if txt.strip():
                yield txt.strip()

    def update_planet_resources(self, planet=None):
        planet = planet if planet is not None else self.current_planet
        logger.info('updating resources on planet %r' % planet)
        try:
            for res_type in RES_TYPES:
                res = self.__split_text("//li[@id='%s_box']" % res_type, '.')
                planet.resources[res_type] = int(''.join(res))
        except Exception:
            logger.exception("ERROR: Couldn't update resources")

    def update_planet_buildings(self, planet=None):
        planet, page = self.go_to(planet, PAGES['resources'], update=False)
        logger.info('updating buildings states for %r' % planet)
        buildings = ['metal_mine', 'crystal_mine', 'deuterium_synthetize',
                'solar_plant']
        source = html.fromstring(self.get_html_source())
        for pos, ele in enumerate(source.xpath("//span[@class='level']")):
            try:
                building = getattr(planet, buildings[pos])
            except IndexError:
                continue
            building.level = int(ele.text_content().split()[-1])

    def update_planet_fleet(self, planet=None):
        planet, page = self.go_to(planet, PAGES['fleet'], update=False)
        logger.info('updating fleet states on %r' % planet)
        planet.fleet.clear()
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
        capital = self._conf_dict['capital'] \
                if 'capital' in self._conf_dict else None
        source = html.fromstring(self.get_html_source())
        planets_list = source.xpath( "//div[@id='planetList']")[0]
        for position, elem in enumerate(planets_list):
            name = elem.find_class('planet-name')[0].text.strip()
            coords = elem.find_class('planet-koords')[0].text.strip('[]')
            coords = [int(coord) for coord in coords.split(':')]
            planet = Planet(name, coords, position + 1)
            if not elem.find_class('icon_wrench'):
                planet.add_flag('idle')
            if capital and planet.coords == capital:
                planet.add_flag('capital')
            empire.add(planet)

            if not full:
                continue
            self.update_planet_buildings(planet)
            self.update_planet_fleet(planet)
            self.update_planet_resources(planet)

    def construct(self, construction, planet=None):
        planet = planet if planet is not None else self.current_planet
        if self.current_page != PAGES['resources']:
            self.go_to(planet, PAGES['resources'], update=False)
        if not isinstance(construction, Constructions):
            construction = getattr(planet, construction)
        self.click(construction.css_dom)

    def go_to(self, planet=None, page=None, update=True):
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

        if update:
            self.update_planet_resources(planet)
            if self.current_page == PAGES['resources']:
                self.update_planet_resources(planet)
            elif self.current_page == PAGES['fleet']:
                self.update_planet_fleet(planet)
        return self.current_planet, self.current_page

    def send_resources(self, src, dst, all_ships=False, **kwargs):
        resources, all_resources = Resources(), True
        self.go_to(src, PAGES['fleet'])
        for res_type in RES_TYPES:
            if res_type in kwargs:
                resources[res_type] = kwargs[res_type]
                all_resources = False

        if not src.fleet.transports:
            logger.warn("No ships on %r, can't move resources" % src)
            return

        if all_ships:
            for ships in src.fleet.transports:
                self.click(ships.xpath)
        else:
            for ships in src.fleet.transports.for_moving(resources.total):
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
            for res_type, quantity in resources:
                self.type('id=%s' % res_type, quantity)

        self.click("css=#start > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)
        self.update_planet_fleet(src)

# vim: set et sts=4 sw=4 tw=120:
