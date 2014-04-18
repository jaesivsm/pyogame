from collections import defaultdict

from pyogame.tools.resources import pretty_number
from pyogame.tools.factory import Factory


def pstr(value, is_title=False):
    if isinstance(value, (list, set, tuple)):
        value = value[0]
    if is_title:
        return value.capitalize()
    if isinstance(value, bool):
        return '+' if value else ''
    if isinstance(value, int):
        return pretty_number(value)
    return unicode(value)


def get_attr(element, attrs):
    if not type(attrs) is str:
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
        return space + value + space * (lenghts[column] - len(value) + 1) + sep
    sep_line = '+'
    line = '|'
    for column in columns:
        value = pstr(column, is_title=True)
        line += add_to_line(value)
        sep_line += add_to_line('-' * len(value), '-', '+')
    print sep_line
    print line
    print sep_line

    for element in iterable:
        line = '|'
        for column in columns:
            value = pstr(get_attr(element, column))
            line += add_to_line(value)
        print line
    print sep_line

def _try_exit(exit_status):
    try:
        exit(exit_status)
    except NameError:
        pass  # not in a shell

def print_overall_status():
    print_lines(Factory().empire, 'name', 'key', ('cap', 'capital'),
                ('idle', 'is_idle'),
                ('wait', 'is_waiting'), 'resources',
                ('met', 'metal_mine.level'),
                ('cry', 'crystal_mine.level'),
                ('deut', 'deuterium_synthetizer.level'),
                ('sol', 'solar_plant.level'),
                ('transport', 'fleet.capacity'))
    _try_exit(0)

def print_to_construct():
    print_lines(Factory().empire, 'name', ('construct', 'to_construct.name'),
            ('lvl', 'to_construct.level'), ('cost', 'to_construct.cost'))
    _try_exit(0)

def unknown_display(display):
    print "Unknown display: %r" % display
    _try_exit(1)
