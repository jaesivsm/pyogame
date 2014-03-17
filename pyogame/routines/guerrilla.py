import logging

from pyogame.tools.factory import Factory
from pyogame.routines.common import spy, recycle

logger = logging.getLogger(__name__)

SPY = 'SPY'
BOTH = 'BOTH'
RECYCLE = 'RECYCLE'


def check_neighborhood(area=[0, 20], mission=BOTH, planet=None):
    interface = Factory().interface
    if planet is None:
        planet = Factory().empire.capital
    galaxy, system_origin, position = planet.coords

    for distance in range(*area):
        for factor in (1, -1):
            system = system_origin + distance * factor
            if not 0 <= system <= 500:
                pass
            for row in interface.browse_galaxy(galaxy, system, planet):
                if mission in (SPY, BOTH) and row.inactive \
                        and not (row.vacation or row.noob):
                    spy(planet, row.coords)
                if mission in (RECYCLE, BOTH) \
                        and row.debris_content.total > 20000:
                    recycle(planet, row.coords, row.debris_content)
