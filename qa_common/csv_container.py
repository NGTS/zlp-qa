import csv
import numpy as np

from .qa_logging import get_logger


logger = get_logger(__file__)


class CSVContainer(object):

    def __init__(self, infile, sort_key='mjd'):
        self.infile = infile
        self.sort_key = sort_key
        self.load_data()
        self.data = None

    @classmethod
    def from_filename(cls, filename, *args, **kwargs):
        with open(filename) as infile:
            return cls(infile, *args, **kwargs)

    def load_data(self):
        reader = csv.DictReader(self.infile)
        self.data = [row for row in reader]

        self.sort_data()

        for key in self.data[0]:
            setattr(self, key,
                    np.array([float(row[key]) for row in self.data]))

    def sort_data(self):
        try:
            self.data.sort(key=lambda row: row[self.sort_key])
        except KeyError as err:
            logger.warn('Cannot find key %s in data, no sorting', self.sort_key)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __getitem__(self, name):
        return getattr(self, name)

    def __str__(self):
        return '<{0} fname:{1}>'.format(
            self.__class__.__name__,
            self.fname)
