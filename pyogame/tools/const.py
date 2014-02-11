import os

CACHE_PATH = 'empire.cache'
def get_cache_path(user):
    dirname, filename = os.path.split(os.path.abspath(CACHE_PATH))
    return os.path.join(dirname, '%s.%s' % (user, filename))

CONF_PATH = os.path.abspath('conf.json')
