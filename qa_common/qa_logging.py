import logging

fmt = '%(asctime)s|%(levelname)8s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=fmt)

def get_logger(name):
    return logging.getLogger(name)
