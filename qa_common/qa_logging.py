import logging
import sys

fmt = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=fmt, stream=sys.stdout)

def get_logger(name):
    return logging.getLogger(name)
