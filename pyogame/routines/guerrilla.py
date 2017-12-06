import logging

from pyogame.routines.common import spy, recycle

logger = logging.getLogger(__name__)

SPY = 'SPY'
BOTH = 'BOTH'
RECYCLE = 'RECYCLE'


def check_neighborhood(interface, empire,
                       area=None, mission=BOTH, planet=None):
    area = area or [0, 20]
    galaxy, system_origin, _ = planet.coords

    for distance in range(*area):
        for factor in (1, -1):
            system = system_origin + distance * factor
            if not 0 <= system <= 500:
                continue
            for row in interface.browse_galaxy(galaxy, system, planet):
                if mission in (SPY, BOTH) and row.inactive \
                        and not (row.vacation or row.noob):
                    spy(interface, empire, planet, row.coords)
                if mission in (RECYCLE, BOTH) \
                        and row.debris_content.total > 20000:
                    recycle(interface, empire,
                            planet, row.coords, row.debris_content)
