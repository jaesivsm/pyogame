import os
import json
import logging
from argparse import ArgumentParser

from .const import LOGFILE


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
    # rapatriate the ressources to the capital
    parser.add_argument('-r', '--rapatriate', dest='rapatriate',
            action='store_true', default=False)
    parser.add_argument('-c', '--construct', dest='construct',
            action='store_true', default=False)
    # send probs around
    parser.add_argument('-p', '--probes', dest='probes',
            action='store', type=int, default=0)
    # build a specific building on a specific planet
    parser.add_argument('-b', '--build', dest='build',
            action='store', default=False)
    parser.add_argument('-i', '--idles', dest='idles',
            action='store_true', default=False)
    # send recyclers if fields exist
    parser.add_argument('-y', '--recycle', dest='recycle',
            action='store', type=int, default=0)
    args = parser.parse_args()
    if args.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.WARN - args.verbose * 10
        if loglevel <= 0:
            loglevel = logging.DEBUG
    return args, LOGFILE if args.log else None, loglevel


def set_logger(logfile=None, loglevel=None):
    "Will set a global logging configuration for muleo."
    logger = logging.getLogger('pyogame')
    log_format = '%(levelname)-8s - %(message)s'
    if loglevel is None:
        loglevel = logging.INFO
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(loglevel)
    if logfile is not None:
        stream_handler.setLevel(logging.ERROR)
        log_format = '%(asctime)s - ' + log_format
        file_handler = logging.FileHandler(os.path.expanduser(logfile))
        file_handler.setFormatter(logging.Formatter(log_format))
        file_handler.setLevel(loglevel)
        logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
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
