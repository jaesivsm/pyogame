import logging

from pyogame.empire import empire
from pyogame.routines.common import spy, recycle

logger = logging.getLogger(__name__)


def check_neighborhood(interface, area=[0, 20], mission='both', planet=None):
    if planet is None:
        planet = empire.capital
    galaxy, system_origin, position = planet.coords

    for distance in range(*area):
        for factor in (1, -1):
            system = system_origin + distance * factor
            if not 0 <= system <= 500:
                pass
            for row in interface.browse_galaxy(galaxy, system, planet):
                if mission in ('spy', 'both') and row.inactive \
                        and not (row.vacation or row.noob):
                    spy(interface, planet, row.coords)
                if mission in ('recycle', 'both') \
                        and row.debris_content.total > 20000:
                    recycle(interface, planet, row.coords, row.debris_content)
