__pages = {
        'fleet': {'fr': 'Flotte'},
        'resources': {'fr': 'Ressources'},
}
BUILDINGS = {
        u'Mine de m\xe9tal': 'metal_mine',
        u'Mine de cristal': 'crystal_mine',
        u'Synth\xe9tiseur de deut\xe9rium': 'deuterium_synthetize',
        u'Centrale \xe9lectrique solaire': 'solar_plant',
}
RES_TYPES = ['deuterium', 'crystal', 'metal', 'energy']


class Collection(object):

    def __init__(self, coll, lang='fr'):
        self.coll = coll
        self.lang = lang

    def __getitem__(self, key):
        return self.coll[key][self.lang]

    def get(self, key, default=None):
        item = self.coll.get(key)
        return item[self.lang] if item else None


PAGES = Collection(__pages)
