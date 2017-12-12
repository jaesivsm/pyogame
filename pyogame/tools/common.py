from collections import namedtuple

GalaxyRow = namedtuple("GalaxyRow",
        ['coords', 'inactive', 'vacation', 'noob', 'debris', 'debris_content'])


def coords_to_key(coords):
    if isinstance(coords, (list, tuple, set)):
        return ':'.join([str(coord) for coord in coords])
    return coords
