# -*- coding: utf-8 -*-
import re
import time
import logging
from datetime import datetime

from lxml import html
from selenium import webdriver
from selenium.webdriver.support.ui import Select


from pyogame.planet import Planet
from pyogame.fleet import FlyingFleet
from pyogame.constructions import BUILDINGS, STATIONS, Constructions
from pyogame.tools.const import MISSIONS, MISSIONS_DST
from pyogame.tools.resources import RES_TYPES, Resources
from pyogame.tools.common import GalaxyRow

logger = logging.getLogger(__name__)
DEFAULT_WAIT_TIME = 60000
DEFAULT_JS_SLEEP = 1


class Interface:

    def __init__(self, user, password, univers, lang='fr', **kwargs):
        self.driver = webdriver.Firefox()
        self.url = "http://%s.ogame.gameforge.com/" % lang

        self.current_planet = None
        self.current_page = None
        self.user, self.password, self.univers = user, password, univers
        from pyogame.tools.factory import Factory
        self.empire = Factory().empire

    def __split_text(self, xpath, split_on='\n'):
        for txt in self.driver.get_text(xpath).split(split_on):
            if txt.strip():
                yield txt.strip()

    def login(self):
        logger.debug('### Logging in with identity %r', self.user)
        self.driver.get(self.url)
        self.driver.find_element_by_id("loginBtn").click()
        Select(self.driver.find_element_by_id('serverLogin'))\
                .select_by_visible_text(self.univers)
        self.driver.find_element_by_id("usernameLogin").send_keys(self.user)
        self.driver.find_element_by_id("passwordLogin")\
                .send_keys(self.password)
        self.driver.find_element_by_id("loginSubmit").click()

        time.sleep(DEFAULT_JS_SLEEP)
        self.server_url = self.driver.get_location(self).split('?')[0]
        self.discover()
        self.update_empire_overall()

    def update_planet_resources(self, planet=None):
        planet, page = self.go_to(planet, update=False)
        try:
            for res_type in RES_TYPES:
                res = self.__split_text("//li[@id='%s_box']" % res_type, '.')
                planet.resources[res_type] = int(''.join(res))
            logger.info('updating resources on planet %s (%s)',
                        planet, planet.resources)
        except Exception:
            logger.exception("ERROR: Couldn't update resources")

    def _parse_constructions(self, page, planet=None, constructions=[]):
        logger.debug('### updating %s states for %s', page, planet)
        planet, page = self.go_to(planet, page, update=False)
        source = html.fromstring(self.get_html_source())
        for pos, ele in enumerate(source.xpath("//span[@class='level']")):
            try:
                building = getattr(planet, constructions[pos + 1].name)
            except KeyError:
                continue
            building.level = int(ele.text_content().split()[-1])

    def update_planet_buildings(self, planet=None, force=False):
        planet = planet if planet else self.current_planet
        if force or not planet.building_updated:
            self._parse_constructions('resources', planet, BUILDINGS)
            planet.building_updated = True

    def update_planet_stations(self, planet=None, force=False):
        planet = planet if planet else self.current_planet
        if force or not planet.station_updated:
            self._parse_constructions('station', planet, STATIONS)
            planet.station_updated = True

    def update_planet_fleet(self, planet=None, force=False):
        planet = planet if planet else self.current_planet
        if not force and planet.fleet_updated:
            return
        planet, page = self.driver.go_to(planet, 'fleet1', update=False)
        logger.info('updating fleet states on %s', planet)
        planet.fleet.clear()
        source = html.fromstring(self.get_html_source())
        for fleet_type in ('military', 'civil'):
            fleet = source.xpath("//ul[@id='%s']" % fleet_type)
            if len(fleet) < 1:
                logger.debug('No %s fleet on %s', fleet_type, planet)
                continue
            for ships in fleet[0]:
                ships_id = ships.get('id')
                if 'button' in ships_id:
                    ships_id = int(ships_id[-3:])
                cls = ships.find_class('level')
                if len(cls) < 1:
                    continue
                ships_str = cls[0].text_content().split()
                planet.fleet.add(ships_id,
                        name=' '.join(ships_str[:-1]),
                        quantity=int(ships_str[-1].replace('.', '')))
        logger.debug('%s got fleet %s', planet, planet.fleet)
        planet.fleet_updated = True

    def update_empire_overall(self):
        logger.info('updating empire overall')
        source = html.fromstring(self.driver.get_html_source())
        planets_list = source.xpath("//div[@id='planetList']")[0]
        for position, elem in enumerate(planets_list):
            self.empire.planets[position + 1].idle = False \
                    if elem.find_class('icon_wrench') else True
        self.empire.missions.clean(self.empire.waiting_for)

    def discover(self):
        if self.empire.loaded:
            return
        logger.debug('Getting list of colonized planets')
        source = html.fromstring(self.driver.get_html_source())
        try:
            planets_list = source.xpath("//div[@id='planetList']")[0]
        except IndexError:  # FIXME ugly, shouldn't be here, invoking exit bad
            logger.error("Couldn't get the planet list. "
                         "Is your login page the right one? See configuration")
            exit(1)
        for position, elem in enumerate(planets_list):
            name = elem.find_class('planet-name')[0].text.strip()
            coords = elem.find_class('planet-koords')[0].text.strip('[]')
            coords = [int(coord) for coord in coords.split(':')]
            self.empire.add(Planet(name, coords, position + 1))
        self.empire.loaded = True

    def crawl(self, resources=True, **kwargs):
        logger.info("Will crawl all empire for %s",
                    ', '.join([key for key in kwargs if kwargs[key] is True]))
        noc = lambda x: None
        update_funcs = {
                'resources': self.update_planet_buildings \
                             if kwargs.get('building') else noc,
                'fleet1': self.update_planet_fleet \
                          if kwargs.get('fleet') else noc,
                'station': self.update_planet_stations \
                           if kwargs.get('station') else noc,
        }
        for planet in self.empire:
            if self.current_page in update_funcs:
                update_funcs[self.current_page](planet)
            for func in update_funcs.values():
                func(planet)
            if resources:
                self.update_planet_resources(planet)

    def construct(self, construction, planet=None):
        planet = planet if planet is not None else self.current_planet
        if not isinstance(construction, Constructions):
            assert hasattr(planet, construction), \
                    '%s has not %r' % (planet, construction)
            construction = getattr(planet, construction)
        if isinstance(construction, tuple(building.__class__
                                          for building in BUILDINGS.values())):
            page = 'resources'
        else:
            page = 'station'
        self.go_to(planet, page, update=False)
        self.click(construction.css_dom)
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)
        self.update_empire_overall()
        self.update_planet_resources(planet)

    def go_to(self, planet=None, page=None, update=True):
        if planet is not None and self.current_planet is not planet:
            logger.debug('Going to planet %s', planet)
            self.click("//div[@id='planetList']/div[%d]/a" % (planet.position))
            self.current_planet = planet
            self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        if page is not None and self.current_page != page:
            logger.debug('Going to page %s', page)
            self.click("css=a[href=\"%s?page=%s\"]" % (self.server_url, page))
            self.current_page = page
            self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        if update:
            self.update_planet_resources(planet)
            if self.current_page == 'resources':
                self.update_planet_resources(planet)
            elif self.current_page == 'fleet1':
                self.update_planet_fleet(planet)
        return self.current_planet, self.current_page

    def get_date(self, css_id):
        date = re.split('[\.: ]', self.get_text("//span[@id='%s']" % css_id))
        day, month, year, hour, minute, second = [int(i) for i in date]
        return datetime(year + 2000, month, day, hour, minute, second)

    def send_fleet(self, src, dst, mission, fleet,
            resources=Resources(), dtype='planet'):
        self.go_to(src, 'fleet1')
        assert mission in MISSIONS, \
                'mission should be among %r' % MISSIONS.keys()

        dst = dst.coords if isinstance(dst, Planet) else dst

        sent_fleet = FlyingFleet(src.coords, dst, mission)
        for ships in fleet:
            self.type('id=ship_%d' % ships.ships_id, ships.quantity)
            sent_fleet.add(ships=ships)
            src.fleet.remove(ships=ships)

        self.click("css=#continue > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.type("id=galaxy", dst[0])
        self.type("id=system", dst[1])
        self.type("id=position", dst[2])
        self.click(MISSIONS_DST[dtype])
        self.click("css=#continue > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        self.click(MISSIONS[mission])
        for res_type, quantity in resources.movable:
            self.type('id=%s' % res_type, quantity)
        time.sleep(DEFAULT_JS_SLEEP)
        sent_fleet.arrival_time = self.get_date('arrivalTime')
        sent_fleet.return_time = self.get_date('returnTime')

        self.click("css=#start > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)
        self.current_page = None
        self.update_planet_resources(src)
        return sent_fleet

    def browse_galaxy(self, galaxy, system, planet=None):
        self.go_to(planet, 'galaxy')
        logger.debug('Browsing system %r on galaxy %r', system, galaxy)
        self.type("id=galaxy_input", galaxy)
        self.type("id=system_input", system)
        self.click("id=showbutton")
        time.sleep(DEFAULT_JS_SLEEP)
        source = html.fromstring(self.get_html_source())
        for position, row in enumerate(
                source.xpath('//table[@id="galaxytable"]//tbody//tr')):
            if row.find_class('planetEmpty'):
                continue
            inactive = row.find_class('inactive') \
                    or row.find_class('longinactive')
            vacation = bool(row.find_class('vacation'))
            noob = bool(row.find_class('noob'))
            debris_class = row.find_class('debris')[0].attrib['class'].strip()
            debris = False if 'js_no_action' in debris_class else True
            debris_content = Resources()
            if debris:
                for css_class in debris_class.split():
                    if not css_class.startswith('js_debris'):
                        continue
                    elem = source.get_element_by_id(css_class[3:])
                    content = elem.find_class('debris-content')
                    metal = ''.join(content[0].text.split()[-1].split('.'))
                    crystal = ''.join(content[1].text.split()[-1].split('.'))
                    debris_content = Resources(metal=metal, crystal=crystal)
                    break
            yield GalaxyRow([galaxy, system, position+1],
                    inactive, vacation, noob, debris, debris_content)
