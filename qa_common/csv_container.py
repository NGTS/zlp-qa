import csv
import numpy as np

class CSVContainer(object):
    def __init__(self, fname):
        self.fname = fname
        self.load_data()
        self.data = None

    def load_data(self):
        with open(self.fname) as infile:
            reader = csv.DictReader(infile)
            self.data = [row for row in reader]

        for key in self.data[0]:
            setattr(self, key,
                    np.array([float(row[key]) for row in self.data]))

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __getitem__(self, name):
        return getattr(self, name)

    def __str__(self):
        return '<{0} fname:{1}>'.format(
            self.__class__.__name__,
            self.fname)



