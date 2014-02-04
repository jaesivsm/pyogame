# -*- coding: utf-8 -*-
import os
import re
import time
import logging
from lxml import html
from uuid import uuid4
from selenium import selenium
from datetime import timedelta, datetime

from pyogame.empire import empire
from pyogame.planet import Planet
from pyogame.constructions import Constructions
from pyogame.const import PAGES, RES_TYPES, FLEET_ARRIVAL, \
        CACHE_PATH, IDLE, CAPITAL, WAITING_RES

logger = logging.getLogger(__name__)
DEFAULT_WAIT_TIME = 40000


class Interface(selenium):

    def __init__(self, conf_dict={}):
        needed = ['user', 'password', 'univers']
        for key in needed:
            assert key in conf_dict, "configuration dictionnary must at " \
                    "least own the following keys: " + ", ".join(needed)
        self.__capital_crds = conf_dict.get('capital')

        selenium.__init__(self,
                "localhost", 4444, "*chrome", "http://ogame.fr/")
        self.current_planet = None
        self.current_page = None
        self.crawled = False
        self.start()

        logger.info('Logging in with identity %r' % conf_dict['user'])
        self.open(conf_dict['login_page'])
        self.click("id=loginBtn")
        self.select("id=serverLogin", "label=%s" % conf_dict['univers'])
        self.type("id=usernameLogin", conf_dict['user'])
        self.type("id=passwordLogin", conf_dict['password'])
        self.click("id=loginSubmit")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        time.sleep(1)
        self.discover()
        self.update_flags()

    def __del__(self):
        self.clean()
        self.stop()

    def __split_text(self, xpath, split_on='\n'):
        for txt in self.get_text(xpath).split(split_on):
            if txt.strip():
                yield txt.strip()

    def update_planet_resources(self, planet=None):
        planet = planet if planet is not None else self.current_planet
        logger.debug('updating resources on planet %r' % planet)
        try:
            for res_type in RES_TYPES:
                res = self.__split_text("//li[@id='%s_box']" % res_type, '.')
                planet.resources[res_type] = int(''.join(res))
        except Exception:
            logger.exception("ERROR: Couldn't update resources")

    def update_planet_buildings(self, planet=None):
        planet, page = self.go_to(planet, PAGES['resources'], update=False)
        logger.debug('updating buildings states for %r' % planet)
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
        logger.debug('updating fleet states on %r' % planet)
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

    def update_flags(self):
        logger.debug('updating flags')
        now = datetime.now()
        empire.del_flags(IDLE)
        source = html.fromstring(self.get_html_source())
        planets_list = source.xpath("//div[@id='planetList']")[0]
        for position, elem in enumerate(planets_list):
            if not elem.find_class('icon_wrench'):
                empire.planets[position + 1].add_flag(IDLE)
        for planet in empire:
            if not planet.has_flag(WAITING_RES):
                planet.del_flag(FLEET_ARRIVAL)
            construct = None
            if planet.has_flag(FLEET_ARRIVAL):
                to_dels = []
                for travel_id, date \
                        in planet.get_flag(FLEET_ARRIVAL).items():
                    if date < now:
                        if travel_id in planet.get_flag(WAITING_RES):
                            construct = planet.get_flag(WAITING_RES)[travel_id]
                        to_dels.append(travel_id)
                import ipdb
                ipdb.set_trace()
                for to_del in to_dels:
                    planet.del_flag_key(FLEET_ARRIVAL, to_del)
                    planet.del_flag_key(WAITING_RES, to_del)
                if construct and not planet.get_flag(WAITING_RES):
                    self.construct(getattr(planet, construct), planet)

    def discover(self):
        logger.info('Getting list of colonized planets')
        source = html.fromstring(self.get_html_source())
        try:
            planets_list = source.xpath("//div[@id='planetList']")[0]
        except IndexError:
            logger.error("Couldn't get the planet list. Is your login page the right one? See configuration")
            exit(1)
        for position, elem in enumerate(planets_list):
            name = elem.find_class('planet-name')[0].text.strip()
            coords = elem.find_class('planet-koords')[0].text.strip('[]')
            coords = [int(coord) for coord in coords.split(':')]
            planet = Planet(name, coords, position + 1)
            if self.__capital_crds and planet.coords == self.__capital_crds:
                planet.add_flag(CAPITAL)
            empire.add(planet)

        if not os.path.exists(CACHE_PATH):
            logger.info('No cache file found at %r' % CACHE_PATH)
            return
        try:
            with open(CACHE_PATH, 'r') as fp:
                empire.loads_flags(fp.read())
        except ValueError:
            logger.error('Cache has been corrupted, ignoring it')
        os.remove(CACHE_PATH)

    def crawl(self, building=False, fleet=False):
        for planet in empire:
            if self.current_page == PAGES['fleet']:
                if fleet:
                    self.update_planet_fleet(planet)
                if building:
                    self.update_planet_buildings(planet)
            else:
                if building:
                    self.update_planet_buildings(planet)
                if fleet:
                    self.update_planet_fleet(planet)
            self.update_planet_resources(planet)
        self.crawled = True

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

    def send_resources(self, src, dst, all_ships=False, resources=None):
        logger.warn('Moving %r from %r to %r'
                % (resources if resources else 'all resources', src, dst))
        self.go_to(src, PAGES['fleet'])
        travel_id = str(uuid4())
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
        if not resources:
            self.click("css=#allresources > img")
        else:
            for res_type, quantity in resources.movable:
                self.type('id=%s' % res_type, quantity)
        time.sleep(1)
        day, month, year, hour, minute, second = [int(i) for i in
                re.split('[\.: ]', self.get_text("//span[@id='arrivalTime']"))]
        arrival = datetime(year + 2000, month, day, hour, minute, second)
        arrival = arrival + timedelta(seconds=60)
        logger.info('Resources will be arriving at %s' % arrival)
        dst.add_flag(FLEET_ARRIVAL, {travel_id: arrival})

        self.click("css=#start > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)
        self.current_page = None
        self.update_planet_fleet(src)
        return travel_id

    def clean(self):
        with open(CACHE_PATH, 'w') as fp:
            fp.write(empire.dumps_flags())

# vim: set et sts=4 sw=4 tw=120:
