__pages = {
        'fleet': {'fr': 'Flotte'},
        'resources': {'fr': 'Ressources'},
}
RES_TYPES = ['metal', 'crystal', 'deuterium']

class Collection(object):

    def __init__(self, coll, lang='fr'):
        self.coll = coll
        self.lang = lang

    def __getitem__(self, key):
        return self.coll[key][self.lang]


PAGES = Collection(__pages)
