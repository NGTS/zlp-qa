import numpy as np

def find_night_breaks(mjd, gap_size):
    mjd_a = np.array(mjd)
    frames = np.arange(mjd_a.size)
    ind = np.diff(mjd_a) > gap_size
    return frames[ind]

def plot_night_breaks(ax, mjd, gap_size=0.3, ls='--', color='k'):
    breaks = find_night_breaks(mjd, gap_size)
    for b in breaks:
        ax.axvline(b, ls=ls, color=color, zorder=-5)

