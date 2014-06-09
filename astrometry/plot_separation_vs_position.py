#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import argparse
import fitsio
from astropy import units as u
from astropy.coordinates import ICRS
import matplotlib.pyplot as plt
from scipy import stats

def link_y_limits(ax1, ax2):
    ax1_y = ax1.get_ylim()
    ax2_y = ax2.get_ylim()

    ll = min(ax1_y[0], ax2_y[0])
    ul = max(ax1_y[1], ax2_y[1])

    for ax in [ax1, ax2]:
        ax.set_ylim(ll, ul)

def compute_limits(data, nsigma=3, precomputed_median=None):
    med = (precomputed_median if precomputed_median is not None
            else np.median(data))

    std = np.std(data)

    ll = med - nsigma * std
    ul = med + nsigma * std

    return ll, ul

def compute_binned(x, y, nbins, statistic='median'):
    binned, ledges, _ = stats.binned_statistic(x, y, statistic=statistic,
            bins=nbins)

    binned = np.append(binned, binned[-1])
    return ledges, binned

def compute_binned_errors(x, y, nbins):
    std, ledges, _ = stats.binned_statistic(x, y, statistic='std',
            bins=nbins)
    count, _, _ = stats.binned_statistic(x, y, statistic='count',
            bins=ledges)

    error = std / np.sqrt(count)
    error = np.append(error, error[-1])

    return ledges, error

def compute_bin_centres(ledges):
    return ledges + np.diff(ledges)[0] / 2.

def main(args):
    with fitsio.FITS(args.catalogue) as infile:
        hdu = infile[1]
        ra1 = hdu['RA_1'][:]
        dec1 = hdu['DEC_1'][:]

        ra2 = hdu['ra_2'][:]
        dec2 = hdu['dec_2'][:]

        x = hdu['X_coordinate'][:]
        y = hdu['Y_coordinate'][:]


    coords1 = ICRS(ra=ra1, dec=dec1, unit=(u.radian, u.radian))
    coords2 = ICRS(ra=ra2, dec=dec2, unit=(u.degree, u.degree))

    separations = coords1.separation(coords2).degree * 3600.

    fig, axes = plt.subplots(2, 2, sharex=True, figsize=(11, 8))
    [(x_axis, y_axis), (x_zoomed, y_zoomed)] = axes

    nsigma = 5
    nbins = 2048 / 128
    print('Using {} bins'.format(nbins))
    x_axis.plot(x, separations, 'k.', color='0.4')
    x_axis.set_ylabel(r'X')

    ledges, x_binned = compute_binned(x, separations, nbins)
    _, x_binned_error = compute_binned_errors(x, separations, ledges)
    bin_centres = compute_bin_centres(ledges)

    for ax in [x_axis, x_zoomed]:
        ax.errorbar(bin_centres[:-1], x_binned[:-1], x_binned_error[:-1],
                color='r', ls='None')
        ax.plot(ledges, x_binned, color='r', drawstyle='steps-post')

    x_zoomed.set_ylim(*compute_limits(x_binned, nsigma=nsigma))
    x_zoomed.set_ylabel(r'X zoomed')


    y_axis.plot(y, separations, 'k.', color='0.4')
    y_axis.set_ylabel(r'y')

    ledges, y_binned = compute_binned(y, separations, nbins)
    _, y_binned_error = compute_binned_errors(y, separations, ledges)

    for ax in [y_axis, y_zoomed]:
        ax.errorbar(bin_centres[:-1], y_binned[:-1], x_binned_error[:-1],
                color='r', ls='None')
        ax.plot(ledges, y_binned, color='r', drawstyle='steps-post')

    y_zoomed.set_ylim(*compute_limits(y_binned, nsigma=nsigma))
    y_zoomed.set_ylabel(r'y zoomed')

    link_y_limits(x_zoomed, y_zoomed)

    for ax in axes.flatten():
        ax.grid(True)

    fig.tight_layout()
    fig.savefig(args.output, bbox_inches='tight')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('catalogue', help='Input catalogue')
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    main(parser.parse_args())

