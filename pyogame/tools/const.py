import os
__pages = {
        'fleet': {'fr': 'Flotte'},
        'resources': {'fr': 'Ressources'},
}

CACHE_PATH = 'empire.cache'
def get_cache_path(user):
    dirname, filename = os.path.split(os.path.abspath(CACHE_PATH))
    return os.path.join(dirname, '%s.%s' % (user, filename))

CONF_PATH = os.path.abspath('conf.json')


class Collection(object):

    def __init__(self, dictionnary, lang='fr'):
        self.lang = lang
        self.dictionnary = {}
        for key in dictionnary:
            self.dictionnary[key] = dictionnary[key][lang]
            self.dictionnary[dictionnary[key][lang]] = key

    def __getitem__(self, *args, **kwargs):
        return self.dictionnary.__getitem__(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.dictionnary.get(*args, **kwargs)


PAGES = Collection(__pages)
