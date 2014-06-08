#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import argparse
import fitsio
from astropy import units as u
from astropy.coordinates import ICRS
import matplotlib.pyplot as plt
from scipy import stats

def compute_limits(data, nsigma=3, precomputed_median=None):
    med = (precomputed_median if precomputed_median is not None
            else np.median(data))

    std = np.std(data)

    ll = med - nsigma * std
    ul = med + nsigma * std

    return ll, ul

def compute_binned(x, y, nbins):
    binned, ledges, _ = stats.binned_statistic(x, y, statistic='median',
            bins=nbins)

    binned = np.append(binned, binned[-1])
    return ledges, binned

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

    for ax in [x_axis, x_zoomed]:
        ax.plot(ledges, x_binned, color='r', drawstyle='steps-post')

    x_zoomed.set_ylim(*compute_limits(x_binned, nsigma=nsigma))
    x_zoomed.set_ylabel(r'X zoomed')


    y_axis.plot(y, separations, 'k.', color='0.4')
    y_axis.set_ylabel(r'y')

    ledges, y_binned = compute_binned(y, separations, nbins)
    for ax in [y_axis, y_zoomed]:
        ax.plot(ledges, y_binned, color='r', drawstyle='steps-post')
    y_zoomed.set_ylim(*compute_limits(y_binned, nsigma=nsigma))
    y_zoomed.set_ylabel(r'y zoomed')

    fig.tight_layout()
    fig.savefig(args.output, bbox_inches='tight')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('catalogue', help='Input catalogue')
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    main(parser.parse_args())

