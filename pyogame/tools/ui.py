from pyogame.tools.factory import Factory


def stat_lines():
    empire = Factory().empire
    lines = []
    for planet in empire:
        yield planet.name, planet.key, planet.capital, planet.is_idle, \
                planet.is_waiting, planet.resources.movable, \
                planet.metal_mine, planet.crystal_mine, \
                planet.deuterium_synthetizer, planet.solar_plant


def print_stats():
    for line in stat_lines():
        print line
