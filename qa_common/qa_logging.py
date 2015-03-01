import logging
import sys
import datetime

fmt = '%(asctime)s|%(name)s|%(levelname)7s|%(message)s'
logging.basicConfig(level=logging.DEBUG, format=fmt, stream=sys.stderr)


def get_logger(filename):
    return logging.getLogger(filename)
