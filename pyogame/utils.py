import logging

def set_logger(logfile=False):
    "Will set a global logging configuration for muleo."
    logger = logging.getLogger('pyogame')
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
