import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from contextlib import contextmanager

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


@contextmanager
def subplots(*args, **kwargs):
    xlabels = kwargs.pop('xlabels', None)
    ylabels = kwargs.pop('ylabels', None)
    grid = kwargs.pop('grid', None)

    fig, axes = plt.subplots(*args, **kwargs)
    try:
        axes = axes.flatten()
    except AttributeError:
        axes = [axes]
    yield (fig, axes)
    if xlabels is not None:
        for (ax, label) in zip(axes, xlabels):
            ax.set_xlabel(label)

    if ylabels is not None:
        for (ax, label) in zip(axes, ylabels):
            ax.set_ylabel(label)

    fig.tight_layout()
