#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import argparse
import fitsio
from astropy import units as u
from astropy.coordinates import ICRS
import matplotlib.pyplot as plt



def main(args):
    with fitsio.FITS(args.catalogue) as infile:
        data = infile[1]['RA', 'ra_1', 'DEC', 'dec_1'][:]
        hdu = infile[1]
        ra1 = hdu['RA'][:]
        dec1 = hdu['DEC'][:]

        ra2 = hdu['ra_1'][:]
        dec2 = hdu['dec_1'][:]
        

    coords1 = ICRS(ra=ra1, dec=dec1, unit=(u.radian, u.radian))
    coords2 = ICRS(ra=ra2, dec=dec2, unit=(u.degree, u.degree))

    separations = coords1.separation(coords2).degree * 3600.

    fig, axes = plt.subplots(figsize=(11, 8))

    axes.hist(separations, 30, histtype='step')
    axes.set_xlabel(r'Separation / arcseconds')
    axes.grid(True)

    fig.tight_layout()
    fig.savefig(args.output, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('catalogue', help='Input catalogue')
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    main(parser.parse_args())

