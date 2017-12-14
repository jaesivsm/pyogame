from itertools import chain
from collections import defaultdict

from pyogame.tools.resources import pretty_number


def pstr(value, is_title=False):
    if isinstance(value, (list, set, tuple)):
        value = value[0]
    if is_title:
        return ' '.join(v for v in value.split())
    if isinstance(value, bool):
        return '+' if value else ''
    if isinstance(value, int):
        return pretty_number(value)
    return str(value)


def print_lines(iterables, *columns):
    lenghts = defaultdict(int)

    def set_max_len(col_title, value, is_title=False):
        lenght = len(pstr(value, is_title))
        if lenght > lenghts[col_title]:
            lenghts[col_title] = lenght

    for title, column_value_getter in columns:
        set_max_len(title, title, is_title=True)
        for element in chain(*iterables):
            set_max_len(title, column_value_getter(element))

    def add_to_line(col_title, value, space=' ', sep='|'):
        return "%s%s%s" % (space, value,
                space * (lenghts[col_title] - len(value) + 1) + sep)
    sep_line = '+'
    line = '|'
    for title, _ in columns:
        value = pstr(title, is_title=True)
        line += add_to_line(title, value)
        sep_line += add_to_line(title, '-' * len(value), '-', '+')
    print(sep_line)
    print(line)
    print(sep_line)

    for element in chain(*iterables):
        line = '|'
        for title, column_value_getter in columns:
            value = pstr(column_value_getter(element))
            line += add_to_line(title, value)
        print(line)
    print(sep_line)


def default_col(ke):
    return ke.split('_')[-1][0:4].capitalize(), lambda x: getattr(x, ke, '--')


def construct_level_col(key, title=None):
    return title or key[0:4].capitalize(), \
            lambda x: x.constructs.cond(name=key).first.level


def join_col_or_ddash(colname):
    def wrapped(obj):
        iterator = getattr(obj, colname, None)
        if iterator is None:
            return '--'
        return ', '.join(['%s %s' % (building, building.cost)
                          for building in iterator])
    return wrapped


def tech_to_col(tech):
    return ''.join(name[0:4].capitalize() for name in tech.name.split('_')), \
            lambda x: tech.level


def print_technologies(empire):
    print_lines([[None]],
                *[tech_to_col(tech) for tech in empire.technologies])


def print_overall_status(empire):
    print_lines((empire,),
                default_col('name'),
                default_col('key'),
                default_col('capital'),
                default_col('is_idle'),
                default_col('is_waiting'),
                ('Resources', lambda x: x.resources),
                ('F M', lambda x: x.is_metal_tank_full),
                ('F C', lambda x: x.is_crystal_tank_full),
                ('F D', lambda x: x.is_deuterium_tank_full),
                ('Transport', lambda x: x.fleet.capacity))


def print_empire_buildings(empire):
    print_lines((empire,),
                default_col('name'),
                default_col('key'),
                construct_level_col('metal_mine'),
                construct_level_col('crystal_mine'),
                construct_level_col('deuterium_synthetizer'),
                construct_level_col('solar_plant'),
                construct_level_col('metal_tank', 'T M'),
                construct_level_col('crystal_tank', 'T C'),
                construct_level_col('deuterium_tank', 'T D'),
                construct_level_col('robot_factory'),
                construct_level_col('shipyard'),
                construct_level_col('laboratory'))

def print_to_construct(empire):
    empire.name = 'Empire'
    print_lines(([empire], empire),
                default_col('name'),
                default_col('key'),
                ('Construct decided by algo',
                    join_col_or_ddash('to_construct')),
                ('Plans registred', join_col_or_ddash('_planner_plans')),
                ('Next construct by plans',
                    join_col_or_ddash('planner_next_plans')),
                )


def unknown_display(display):
    print("Unknown display: %r" % display)
