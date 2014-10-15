import logging

fmt = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=fmt)

def get_logger(name):
    return logging.getLogger(name)
