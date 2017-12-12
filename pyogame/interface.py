# -*- coding: utf-8 -*-
import re
import time
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from lxml import html
from selenium import webdriver
from selenium.webdriver.support.ui import Select


from pyogame.planet import Planet
from pyogame.fleet import FlyingFleet
from pyogame.tools.const import MISSIONS, MISSIONS_DST, Pages
from pyogame.tools.resources import RES_TYPES, Resources
from pyogame.tools.common import GalaxyRow

logger = logging.getLogger(__name__)
DEFAULT_WAIT_TIME = 10  # seconds
DEFAULT_JS_SLEEP = 1


class Interface:

    def __init__(self, user, password, univers, lang='fr', **kwargs):
        self._driver = None
        self.url = "http://%s.ogame.gameforge.com/" % lang

        self.current_planet = None
        self.user, self.password, self.univers = user, password, univers

    @property
    def driver(self):
        if self._driver is None:
            self._driver = webdriver.Firefox()
            self._driver.implicitly_wait(DEFAULT_WAIT_TIME)
        return self._driver

    @property
    def server_url(self):
        return self.driver.current_url.split('?')[0]

    @property
    def current_page(self):
        query = urlparse(self.driver.current_url).query
        page = parse_qs(query).get('page')
        if page:
            return Pages(page[0])

    def __split_text(self, xpath, split_on='\n'):
        for txt in self.driver.find_element_by_xpath(xpath)\
                .text.split(split_on):
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
        self.click(id_='loginSubmit')

        time.sleep(DEFAULT_JS_SLEEP)

    def logout(self):
        self.click(css="a[href=\"%s?page=logout\"]" % self.server_url)
        self.driver.close()

    def click(self, id_=None, name=None, xpath=None, css=None):
        if id_ is not None:
            elem = self.driver.find_element_by_id(id_)
        elif name is not None:
            elem = self.driver.find_element_by_name(name)
        elif xpath is not None:
            elem = self.driver.find_element_by_xpath(xpath)
        elif css is not None:
            elem = self.driver.find_element_by_css_selector(css)
        else:
            raise ValueError('Interface.click must be provided at least one')
        elem.click()
        return elem

    def update_planet_resources(self, planet):
        resources = Resources()
        try:
            for res_type in RES_TYPES:
                res = self.__split_text("//li[@id='%s_box']" % res_type, '.')
                resources[res_type] = int(''.join(res))
            logger.debug('found %r on %s:%s',
                    resources, self.current_planet, self.current_page)
            planet.resources = resources
        except Exception:
            logger.exception("ERROR: Couldn't update resources")
        return resources

    def update_buildings(self, page, planet):
        logger.debug('### updating %s states for %s', page, planet)
        source = html.fromstring(self.driver.page_source)
        for pos, ele in enumerate(source.xpath("//span[@class='level']")):
            # page resources and station don't start at the same level
            offset = 0 if page is Pages.station else 1
            builds = planet.constructs.cond(page=page, position=pos + offset)
            if builds.first is None:
                continue  # building is not supported yet
            builds.first.level = int(ele.text_content().split()[-1])

    def update_technologies(self, empire):
        logger.debug('### updating tech states')
        source = html.fromstring(self.driver.page_source)
        for pos, ele in enumerate(source.xpath("//span[@class='level']")):
            tech = empire.technologies.cond(position=pos).first
            try:
                tech.level = int(ele.text_content().split()[-1])
            except ValueError:  # supporting temp upgrade, shifting real level
                tech.level = int(ele.text_content().split()[-2])

    def update_planet_fleet(self, planet):
        planet = planet if planet else self.current_planet
        logger.info('updating fleet states on %s', planet)
        planet.fleet.clear()
        source = html.fromstring(self.driver.page_source)
        for fleet_type in 'military', 'civil':
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

    def update_empire_state(self, empire):
        logger.debug('Getting list of colonized planets')
        source = html.fromstring(self.driver.page_source)
        planets_list_elem = source.xpath("//div[@id='planetList']")[0]
        existing = {}
        for position, elem in enumerate(planets_list_elem):
            name = elem.find_class('planet-name')[0].text.strip()
            coords = elem.find_class('planet-koords')[0].text.strip('[]')
            coords = [int(coord) for coord in coords.split(':')]
            planet = Planet(name, coords, position + 1)
            existing[planet.key] = planet

        for planet in existing.values():
            if empire.cond(key=planet.key).first is None:
                logger.warning('Adding %r to empire', planet)
                empire.add(planet)

        to_remove = []
        for planet in empire:
            if planet.key not in existing:
                to_remove.append(planet)
        for planet in to_remove:
            logger.warning('Removing %r of empire', planet)
            empire.remove(planet.key)

        logger.debug('updating empire overall')
        source = html.fromstring(self.driver.page_source)
        planets_list = source.xpath("//div[@id='planetList']")[0]
        for position, elem in enumerate(planets_list):
            empire.cond(position=position + 1).first.idle = not bool(
                    elem.find_class('icon_wrench'))
        empire.missions.clean(empire.waiting_for)

    def crawl(self, planets, **kwargs):
        for planet in planets:
            for page in Pages.resources, Pages.station, Pages.fleet:
                self.go_to(planet=planet, page=page)
            if planet.capital:
                self.go_to(planet=planet, page=Pages.research)
                self.update_technologies(planets)

    def construct(self, construct, planet=None):
        planet = planet if planet is not None else self.current_planet
        self.go_to(planet, construct.page, update=False)
        self.click(css=construct.css_dom)
        self.update_planet_resources(planet)
        planet.idle = False
        planet.remove_old_plans()

    def go_to(self, planet=None, page=None, update=True):
        if planet is not None and self.current_planet is not planet:
            logger.debug('Going to planet %s', planet)
            self.click(xpath="//div[@id='planetList']/div[%d]/a"
                       % (planet.position))
            self.current_planet = planet

        if page is not None and self.current_page is not page:
            logger.debug('Going to page %s', page)
            self.click(css="a[href=\"%s?page=%s\"]"
                       % (self.server_url, page.value))

        if self.current_planet:
            self.update_planet_resources(self.current_planet)
            if self.current_page in {Pages.resources, Pages.station}:
                self.update_buildings(self.current_page, self.current_planet)
            elif self.current_page is Pages.fleet:
                self.update_planet_fleet(self.current_planet)
        return self.current_planet, self.current_page

    def get_date(self, css_id):
        date = re.split(r'[\.: ]',
                self.driver.find_element_by_xpath(
                    "//span[@id='%s']" % css_id).text)
        day, month, year, hour, minute, second = [int(i) for i in date]
        return datetime(year + 2000, month, day, hour, minute, second)

    def send_fleet(self, src, dst, mission, fleet,
            resources=Resources(), dtype='planet'):
        self.go_to(src, Pages.fleet)
        assert mission in MISSIONS, \
                'mission should be among %r' % MISSIONS.keys()

        dst = dst.coords if isinstance(dst, Planet) else dst

        sent_fleet = FlyingFleet(src.coords, dst, mission)
        for ships in fleet:
            self.driver.find_element_by_id('ship_%d' % ships.ships_id)\
                    .send_keys(ships.quantity)
            sent_fleet.add(ships=ships)
            src.fleet.remove(ships=ships)

        self.click(css="#continue > span")

        self.driver.find_element_by_id("galaxy").send_keys(dst[0])
        self.driver.find_element_by_id("system").send_keys(dst[1])
        self.driver.find_element_by_id("position").send_keys(dst[2])
        self.click(id_=MISSIONS_DST[dtype])
        self.click(css="#continue > span")

        self.click(css=MISSIONS[mission])
        for res_type, quantity in resources.movable:
            self.driver.find_element_by_id(res_type).send_keys(quantity)
        sent_fleet.arrival_time = self.get_date('arrivalTime')
        sent_fleet.return_time = self.get_date('returnTime')

        self.click(css="#start > span")
        self.update_planet_resources(src)
        return sent_fleet

    def browse_galaxy(self, galaxy, system, planet=None):
        self.go_to(planet, Pages.galaxy)
        logger.debug('Browsing system %r on galaxy %r', system, galaxy)
        self.driver.find_element_by_id('galaxy_input').send_keys(galaxy)
        self.driver.find_element_by_id("system_input").send_keys(system)
        self.click(id_="showbutton")
        time.sleep(DEFAULT_JS_SLEEP)
        source = html.fromstring(self.driver.page_source)
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
