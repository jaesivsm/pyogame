import os

CACHE_PATH = 'empire.cache'
def get_cache_path(user):
    dirname, filename = os.path.split(os.path.abspath(CACHE_PATH))
    return os.path.join(dirname, '%s.%s' % (user, filename))

CONF_PATH = os.path.abspath(os.path.expanduser('conf.json'))
LOGFILE = os.path.abspath(os.path.expanduser('~/ogame.log'))

MISSIONS = {
        'transport': 'css=#missionButton3',
        'spy': 'css=#missionButton6',
        'recycle': 'css=#missionButton8',
}
MISSIONS_DST = {
        'planet': 'id=pbutton',
        'debris': 'id=dbutton',
}
