import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

matplotlib.rc('patch', edgecolor='None')
matplotlib.rc('image', cmap='afmhot')

from .csv_container import CSVContainer
from find_night_breaks import find_night_breaks
