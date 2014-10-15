import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

matplotlib.rc('patch', edgecolor='None')
matplotlib.rc('image', cmap='afmhot')
matplotlib.rc('figure', figsize=(11, 8))

from .csv_container import CSVContainer
from find_night_breaks import plot_night_breaks
from .qa_logging import get_logger
