#!/usr/bin/python
from selenium import selenium
PLANETS = {
        2: {'galaxy': 5, 'system': 57, 'position': 5},
        3: {'galaxy': 5, 'system': 57, 'position': 6},
        4: {'galaxy': 5, 'system': 57, 'position': 7},
        5: {'galaxy': 5, 'system': 58, 'position': 7},
        6: {'galaxy': 5, 'system': 58, 'position': 10},
        7: {'galaxy': 5, 'system': 58, 'position': 11}}

class Ogame(selenium):

    def __init__(self, login, password, mother=None):
        selenium.__init__(self,
				"localhost", 4444, "*chrome", "http://ogame.fr/")
        self.start()
        self.login(login, password)
        self.mother = mother

    def __del__(self):
        self.stop()

    def login(self, login, passwd):
        self.open("http://ogame.fr/")
        self.click("id=loginBtn")
        self.select("id=serverLogin", "label=Pegasus")
        self.type("id=usernameLogin", login)
        self.type("id=passwordLogin", passwd)
        self.click("id=loginSubmit")
        self.wait_for_page_to_load("30000")

    def go_to(self, planet, page):
        self.click("//div[@id='myPlanets']/div[%d]/a" % planet)
        self.wait_for_page_to_load("30000")
        self.click("link=%s" % page)
        self.wait_for_page_to_load("30000")

    def send_ressources(self, src, dst, content={}):
        #metal = content.get('metal', 'all')
        #cristal = content.get('cristal', 'all')
        #deut = content.get('deut', 'all')

        self.go_to(src, 'Flotte')
        self.click("link=Grand transporteur 4")
        self.click("css=#continue > span")
        self.wait_for_page_to_load("30000")

        self.type("id=galaxy", PLANETS[dst]["galaxy"])
        self.type("id=system", PLANETS[dst]["system"])
        self.type("id=position", PLANETS[dst]["position"])
        self.click("id=pbutton")
        self.click("css=#continue > span")
        self.wait_for_page_to_load("30000")

        self.click("css=#missionButton3")
        #if metal == 'all' and cristal == 'all' and deut == 'all':
        self.click("css=#allresources > img")
        self.click("css=#start > span")
        self.wait_for_page_to_load("30000")

    def rapatriate(self, dst=None):
        dst = dst if dst is not None else self.mother
        for planet in PLANETS:
            if PLANETS[dst] == PLANETS[planet]:
                continue
            self.send_ressources(planet, dst)

# vim: set et sts=4 sw=4 tw=120:
