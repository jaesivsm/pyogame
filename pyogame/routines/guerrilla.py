import logging

from pyogame.empire import empire
from pyogame.routines.common import spy, recycle

logger = logging.getLogger(__name__)
START_GAL = 1
END_GAL = 499


def check_neighborhood(interface, area=1, mission='both', planet=None):
    if planet is None:
        planet = empire.capital
    interface.crawl(fleet=True)
    galaxy, system, place = planet.coords
    area = int(area)
    start = system - area if system - area >= START_GAL else START_GAL
    end = system + area if system + area <= END_GAL else END_GAL

    for system in range(start, end+1):
        for row in interface.browse_galaxy(galaxy, system, planet):
            if mission in ('spy', 'both') and row.inactive \
                    and not (row.vacation or row.noob):
                spy(interface, planet, [galaxy, system, row.postition])
            if mission in ('recycle', 'both') and row.debris:
                recycle(interface, planet, [galaxy, system, row.postition],
                        row.recyclers)
