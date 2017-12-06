import os
from enum import Enum


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

class Pages(Enum):
    overview = 'overview'
    resources = 'resources'
    station = 'station'
    research = 'research'
    shipyard = 'shipyard'
    defense = 'defense'
    fleet = 'fleet1'
    movement = 'movement'
    galaxy = 'galaxy'
