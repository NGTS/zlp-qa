import csv
import numpy as np

from .qa_logging import get_logger


logger = get_logger(__file__)


class CSVContainer(object):

    def __init__(self, fname, sort_key='mjd'):
        self.fname = fname
        self.sort_key = sort_key
        self.load_data()
        self.data = None

    def load_data(self):
        with open(self.fname) as infile:
            reader = csv.DictReader(infile)
            self.data = [row for row in reader]

        self.sort_data()

        for key in self.data[0]:
            setattr(self, key,
                    np.array([float(row[key]) for row in self.data]))

    def sort_data(self):
        try:
            self.data.sort(key=lambda row: row[self.sort_key])
        except KeyError as err:
            logger.warn('Cannot find key in data, no sorting',
                        key=self.sort_key)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __getitem__(self, name):
        return getattr(self, name)

    def __str__(self):
        return '<{0} fname:{1}>'.format(
            self.__class__.__name__,
            self.fname)
