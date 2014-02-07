import json
import logging
from argparse import ArgumentParser


LOGFILE = '~/ogame.log'

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(dest='user', action='store', default=None)
    parser.add_argument('-d', '--debug', dest='debug',
            action='store_true', default=False)
    parser.add_argument('-q', '--quiet', dest='quiet',
            action='store_true', default=False)
    parser.add_argument('-v', '--verbose', dest='verbose',
            action='count', default=0)
    parser.add_argument('-l', '--log', dest='log',
            action='store_true', default=False)
    parser.add_argument('-r', '--rapatriate', dest='rapatriate',
            action='store_true', default=False)
    parser.add_argument('-c', '--construct', dest='construct',
            action='store_true', default=False)
    parser.add_argument('-p', '--probes', dest='probes',
            action='store_true', default=False)
    parser.add_argument('-b', '--build', dest='build',
            action='store', default=False)
    args = parser.parse_args()
    if args.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.WARN - args.verbose * 10
    return args, LOGFILE if args.log else None, loglevel


def set_logger(logfile=None, loglevel=None):
    "Will set a global logging configuration for muleo."
    logger = logging.getLogger('pyogame')
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    if loglevel is None:
        loglevel = logging.INFO
    if logfile is not None:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(loglevel)
    return logger


def load_conf(username, logfile=None, loglevel=None):
    from pyogame.interface import Interface
    from pyogame.tools.const import CONF_PATH

    with open(CONF_PATH) as conf_file:
        conf = json.load(conf_file)

    if loglevel is None:
        loglevel = conf.get('loglevel', logging.INFO)
    logger = set_logger(logfile, loglevel)

    if username not in conf:
        logger.error('Account %r unknown' % username)
        return None
    return Interface(conf[username])
