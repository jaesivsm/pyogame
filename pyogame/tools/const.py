import os

CONF_PATH = os.path.abspath(os.path.expanduser('conf.json'))
LOGFILE = os.path.abspath(os.path.expanduser('~/ogame.log'))

MISSIONS = {
        'attack': '#missionButton1',
        'transport': '#missionButton3',
        'go': '#missionButton4',
        'spy': '#missionButton6',
        'recycle': '#missionButton8',
        'explore': '#missionButton15',
}
MISSIONS_DST = {
        'planet': 'pbutton',
        'moon': 'mbutton',
        'debris': 'dbutton',
}
