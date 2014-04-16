import os

CONF_PATH = os.path.abspath(os.path.expanduser('conf.json'))
LOGFILE = os.path.abspath(os.path.expanduser('~/ogame.log'))

MISSIONS = {
        'attack': 'css=#missionButton1',
        'transport': 'css=#missionButton3',
        'go': 'css=#missionButton4',
        'spy': 'css=#missionButton6',
        'recycle': 'css=#missionButton8',
        'explore': 'css=#missionButton15',
}
MISSIONS_DST = {
        'planet': 'id=pbutton',
        'moon': 'id=mbutton',
        'debris': 'id=dbutton',
}
