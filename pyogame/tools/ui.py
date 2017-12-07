from collections import defaultdict

from pyogame.tools.resources import pretty_number


def pstr(value, is_title=False):
    if isinstance(value, (list, set, tuple)):
        value = value[0]
    if is_title:
        return ' '.join(v.capitalize() for v in value.split())
    if isinstance(value, bool):
        return '+' if value else ''
    if isinstance(value, int):
        return pretty_number(value)
    return str(value)


def get_attr(element, attrs):
    if not isinstance(attrs, str):
        attrs = attrs[1]
    for attr in attrs.split('.'):
        element = getattr(element, attr)
    return element


def print_lines(iterable, *columns):
    lenghts = defaultdict(int)

    def set_max_len(column, value, is_title=False):
        lenght = len(pstr(value, is_title))
        if lenght > lenghts[column]:
            lenghts[column] = lenght

    for column in columns:
        set_max_len(column, column, is_title=True)
        for element in iterable:
            set_max_len(column, get_attr(element, column))

    def add_to_line(value, space=' ', sep='|'):
        return "%s%s%s" % (space, value,
                space * (lenghts[column] - len(value) + 1) + sep)
    sep_line = '+'
    line = '|'
    for column in columns:
        value = pstr(column, is_title=True)
        line += add_to_line(value)
        sep_line += add_to_line('-' * len(value), '-', '+')
    print(sep_line)
    print(line)
    print(sep_line)

    for element in iterable:
        line = '|'
        for column in columns:
            value = pstr(get_attr(element, column))
            line += add_to_line(value)
        print(line)
    print(sep_line)

def print_overall_status(empire):
    print_lines(empire, 'name', 'key', ('cap', 'capital'),
                ('idle', 'is_idle'),
                ('wait', 'is_waiting'), 'resources',
                ('f m', 'is_metal_tank_full'),
                ('f c', 'is_crystal_tank_full'),
                ('f d', 'is_deuterium_tank_full'),
                ('transport', 'fleet.capacity'))

def print_to_construct(empire):
    print_lines(empire, 'name',
                ('met', 'metal_mine.level'),
                ('cry', 'crystal_mine.level'),
                ('deut', 'deuterium_synthetizer.level'),
                ('sol', 'solar_plant.level'),
                ('t m', 'metal_tank.level'),
                ('t c', 'crystal_tank.level'),
                ('t d', 'deuterium_tank.level'),
                ('rob', 'robot_factory.level'),
                ('shi', 'shipyard.level'),
                ('lab', 'laboratory.level'),
                ('to construct', 'to_construct.name'),
                ('lvl', 'to_construct.level'),
                ('cost', 'to_construct.cost'))

def unknown_display(display):
    print("Unknown display: %r" % display)
