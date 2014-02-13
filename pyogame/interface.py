# -*- coding: utf-8 -*-
import os
import re
import json
import time
import logging
from lxml import html
from selenium import selenium
from datetime import datetime

from pyogame.empire import empire
from pyogame.planet import Planet
from pyogame.fleet import FlyingFleet
from pyogame.constructions import BUILDINGS, STATIONS, Constructions
from pyogame.tools.const import get_cache_path, MISSIONS, MISSIONS_DST
from pyogame.tools.resources import RES_TYPES, Resources
from pyogame.routines.common import spy, recycle

logger = logging.getLogger(__name__)
DEFAULT_WAIT_TIME = 40000


class Interface(selenium):

    def __init__(self, conf_dict={}):
        needed = ['user', 'password', 'univers']
        for key in needed:
            assert key in conf_dict, "configuration dictionnary must at " \
                    "least own the following keys: " + ", ".join(needed)
        empire.capital_coords = conf_dict.get('capital')
        self.user = conf_dict['user']

        url = "http://%s.ogame.gameforge.com/" % conf_dict.get('lang', 'fr')

        selenium.__init__(self, "localhost", 4444, "*chrome", url)
        self.current_planet = None
        self.current_page = None
        self.start()

        logger.info('Logging in with identity %r' % self.user)
        self.open(url)
        self.click("id=loginBtn")
        self.select("id=serverLogin", "label=%s" % conf_dict['univers'])
        self.type("id=usernameLogin", conf_dict['user'])
        self.type("id=passwordLogin", conf_dict['password'])
        self.click("id=loginSubmit")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        time.sleep(1)
        self.server_url = selenium.get_location(self).split('?')[0]
        if not self.load():
            self.discover()
        self.update_empire_overall()

    def __del__(self):
        self.dump()
        self.stop()

    def __split_text(self, xpath, split_on='\n'):
        for txt in self.get_text(xpath).split(split_on):
            if txt.strip():
                yield txt.strip()

    def update_planet_resources(self, planet=None):
        planet, page = self.go_to(planet, update=False)
        logger.debug('updating resources on planet %r' % planet)
        try:
            for res_type in RES_TYPES:
                res = self.__split_text("//li[@id='%s_box']" % res_type, '.')
                planet.resources[res_type] = int(''.join(res))
        except Exception:
            logger.exception("ERROR: Couldn't update resources")

    def _parse_constructions(self, page, planet=None, constructions=[]):
        logger.debug('updating %s states for %r' % (page, planet))
        planet, page = self.go_to(planet, page, update=False)
        source = html.fromstring(self.get_html_source())
        for pos, ele in enumerate(source.xpath("//span[@class='level']")):
            try:
                building = getattr(planet, constructions[pos].name())
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
        planet, page = self.go_to(planet, 'fleet1', update=False)
        logger.debug('updating fleet states on %r' % planet)
        planet.fleet.clear()
        source = html.fromstring(self.get_html_source())
        for fleet_type in ('military', 'civil'):
            fleet = source.xpath("//ul[@id='%s']" % fleet_type)
            if len(fleet) < 1:
                logger.debug('No %s fleet on %r' % (fleet_type, planet))
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
                        quantity=int(ships_str[-1]))
        logger.debug('%s got fleet %s' % (planet, planet.fleet))
        planet.fleet_updated = True

    def update_empire_overall(self):
        logger.debug('updating empire overall')
        source = html.fromstring(self.get_html_source())
        planets_list = source.xpath("//div[@id='planetList']")[0]
        for position, elem in enumerate(planets_list):
            empire.planets[position + 1].idle = False \
                    if elem.find_class('icon_wrench') else True
        empire.missions.clean(empire.waiting_for)

    def discover(self):
        logger.info('Getting list of colonized planets')
        source = html.fromstring(self.get_html_source())
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
            empire.add(Planet(name, coords, position + 1))

    def crawl(self, building=False, station=False, fleet=False, resources=True):
        noc = lambda x: None
        update_funcs = {
                'resources': self.update_planet_buildings if building else noc,
                'fleet1': self.update_planet_fleet if fleet else noc,
                'station': self.update_planet_stations if station else noc,
        }
        for planet in empire:
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
                    '%r has not %r' % (planet, construction)
            construction = getattr(planet, construction)
        if isinstance(construction, tuple(BUILDINGS.values())):
            page = 'resources'
        else:
            page = 'station'
        self.go_to(planet, page, update=False)
        self.click(construction.css_dom)
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)
        self.update_empire_overall()

    def go_to(self, planet=None, page=None, update=True):
        if planet is not None and self.current_planet is not planet:
            logger.info('Going to planet %r' % planet)
            self.click("//div[@id='planetList']/div[%d]/a" % (planet.position))
            self.current_planet = planet
            self.wait_for_page_to_load(DEFAULT_WAIT_TIME)

        if page is not None and self.current_page != page:
            logger.info('Going to page %r' % page)
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
        date =  re.split('[\.: ]', self.get_text("//span[@id='%s']" % css_id))
        day, month, year, hour, minute, second = [int(i) for i in date]
        return datetime(year + 2000, month, day, hour, minute, second)

    def send_fleet(self, src, dst, mission, fleet,
            resources=Resources(), dtype='planet'):
        self.go_to(src, 'fleet1')
        assert mission in MISSIONS, \
                'mission should be among %r' % MISSIONS.keys()

        dst = dst.coords if isinstance(dst, Planet) else dst

        sent_fleet = FlyingFleet(src.coords, dst)
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
        time.sleep(1)
        sent_fleet.arrival_time = self.get_date('arrivalTime')
        sent_fleet.return_time = self.get_date('returnTime')

        self.click("css=#start > span")
        self.wait_for_page_to_load(DEFAULT_WAIT_TIME)
        self.current_page = None
        self.update_planet_resources(src)
        return sent_fleet

    def check_galaxies(self, interface, wideness=0, mission='spy', planet=None):
        if planet is None:
            planet = empire.capital
        self.go_to(planet, 'galaxy')
        time.sleep(2)
        galaxy, syst, place = planet.coords
        wideness = int(wideness)
        deb = syst - wideness
        if deb < 1:
            deb = 1
        fin = syst + wideness
        if fin > 499:
            fin = 499

        for s in range(deb, fin+1):
            self.type("id=galaxy_input", galaxy)
            self.type("id=system_input", s)
            self.click("id=showbutton")
            time.sleep(1)
            if mission=='spy':
                for i in range(1,17):
                    pseudo = self.get_table("galaxytable."+ str(i) +".7")
                    if pseudo.endswith('(i)') or pseudo.endswith('(I)'):
                        spy(self, planet, [galaxy, s, i-1])
                        self.go_to(planet, 'galaxy')
                        self.type("id=galaxy_input", galaxy)
                        self.type("id=system_input", s)
                        self.click("id=showbutton")
                        time.sleep(1)
            elif mission=='recycle':
                tri=0
                source = html.fromstring(self.get_html_source())
                for tr in source.xpath(
                        '//table[@id="galaxytable"]//tr'):
                    tri+=1
                    tdi=0
                    for td in tr:
                        tdi+=1
                        if tri<5:
                            continue
                        if tdi==7 and not td.find_class('js_no_action'):
                            recycle(self, planet, [galaxy, s, tri-4])
            self.go_to(planet, 'galaxy')
            time.sleep(1)

    def load(self):
        cache_path = get_cache_path(self.user)
        if not os.path.exists(cache_path):
            logger.info('No cache file found at %r' % cache_path)
            return False
        logger.debug('Loading objects from %r' % cache_path)
        try:
            with open(cache_path, 'r') as fp:
                empire.load(**json.load(fp))
        except ValueError:
            logger.error('Cache has been corrupted, ignoring it')
            os.remove(cache_path)
            return False
        return True

    def dump(self):
        handler = lambda o: o.isoformat() if isinstance(o, datetime) else None
        with open(get_cache_path(self.user), 'w') as fp:
            json.dump(empire.dump(), fp, default=handler)

# vim: set et sts=4 sw=4 tw=120:
