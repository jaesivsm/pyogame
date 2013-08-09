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
    args = parser.parse_args()
    if args.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.WARN - args.verbose * 10
    return args.user, LOGFILE if args.log else None, loglevel


def set_logger(logfile=None, level=logging.INFO):
    "Will set a global logging configuration for muleo."
    logger = logging.getLogger('pyogame')
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    if logfile is not None:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
