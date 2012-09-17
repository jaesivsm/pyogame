#!/usr/bin/python
from selenium import selenium


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
        self.wait_for_page_to_load("30000")

    def go_to(self, planet, page):
        self.click("//div[@id='planetList']/div[%d]/a"
                % (self.planets.index(planet)))
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

        self.type("id=galaxy", dst[0])
        self.type("id=system", dst[1])
        self.type("id=position", dst[2])
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
        for src in self.planets:
            if dst != src:
                self.send_ressources(src, dst)

# vim: set et sts=4 sw=4 tw=120:
