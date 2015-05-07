import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

matplotlib.rc('patch', edgecolor='None')
matplotlib.rc('image', cmap='afmhot')
matplotlib.rc('figure', figsize=(11, 8))


def compute_limits(data, nsigma=3, precomputed_median=None):
    med = (precomputed_median if precomputed_median is not None else
           np.median(data))

    std = np.std(data)

    ll = med - nsigma * std
    ul = med + nsigma * std

    return ll, ul
