#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import argparse
import sys
import fitsio
from astropy import units as u
from astropy.coordinates import ICRS
from scipy import stats

from qa_common.plotting import plt

def compute_limits(data, nsigma=3, precomputed_median=None):
    med = (precomputed_median if precomputed_median is not None
            else np.median(data))

    std = np.std(data)

    ll = med - nsigma * std
    ul = med + nsigma * std

    return ll, ul


def main(args):
    with fitsio.FITS(args.catalogue) as infile:
        hdu = infile[1]
        ra1 = hdu['RA_1'][:]
        dec1 = hdu['DEC_1'][:]

        ra2 = hdu['ra_2'][:]
        dec2 = hdu['dec_2'][:]

        jmag = hdu['jmag'][:]


    coords1 = ICRS(ra=ra1, dec=dec1, unit=(u.radian, u.radian))
    coords2 = ICRS(ra=ra2, dec=dec2, unit=(u.degree, u.degree))

    separations = coords1.separation(coords2).degree * 3600.

    nbins = 30
    height, xedges, yedges = np.histogram2d(jmag, separations, nbins)

    fig, axis = plt.subplots(figsize=(11, 8))

    mappable = axis.pcolormesh(xedges[:-1], yedges[:-1], np.log10(height.T + 1), 
            cmap=plt.cm.binary)
    axis.plot(jmag, separations, 'k.', alpha=0.2)

    stat, ledges, _ = stats.binned_statistic(jmag, separations, statistic='median',
            bins=nbins)
    axis.plot(ledges[:-1], stat, drawstyle='steps-post', color='r')

    _, ul = compute_limits(separations, nsigma=7)
    axis.set_ylim(ymax=ul)

    axis.set_xlabel(r'2MASS J Magnitude')
    axis.set_ylabel(r'Separation / arcseconds')
    axis.grid(True)

    fig.tight_layout()
    if args.output.strip() == '-':
        fig.savefig(sys.stdout, bbox_inches='tight')
    else:
        fig.savefig(args.output, bbox_inches='tight')




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('catalogue', help='Input catalogue')
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    main(parser.parse_args())

