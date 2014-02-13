import logging

from pyogame.empire import empire
from pyogame.routines.common import spy, recycle

logger = logging.getLogger(__name__)
START_GAL = 1
END_GAL = 499


def check_neighborhood(interface, area=1, mission='both', planet=None):
    if planet is None:
        planet = empire.capital
    galaxy, system, place = planet.coords
    start = system - area if system - area >= START_GAL else START_GAL
    end = system + area if system + area <= END_GAL else END_GAL

    for system in range(start, end+1):
        source, rows = interface.browse_galaxy(galaxy, system, planet)
        for pos, row in enumerate(rows):
            if mission in ('spy', 'both'):
                inactive = row.find_class('status_abbr_inactive') \
                        or row.find_class('status_abbr_longinactive')
                ineligible = (row.find_class('status_abbr_vacation')
                        or row.find_class('status_abbr_noob'))
                if inactive and not ineligible:
                    spy(interface, planet, [galaxy, system, pos+1])
            if mission in ('recycle', 'both'):
                css_classes = row.find_class('debris')[0].attrib['class']
                if 'js_no_action' in css_classes:
                    continue
                for css_class in css_classes.strip().split():
                    if not css_class.startswith('js_'):
                        continue
                    elem = source.get_element_by_id(css_class[3:])
                    nb_recycler = elem.find_class('debris-recyclers')[0].text
                    nb_recycler = int(nb_recycler.split()[-1])
                    break

                recycle(interface, planet, [galaxy, system, pos+1],
                        nb_recycler)
