#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fitsio
import numpy as np
import argparse
import itertools
import sys

from qa_common.plotting import plt


def hide_labels(axis):
    axis.get_xaxis().set_visible(False)
    axis.get_yaxis().set_visible(False)

def main(args):
    with fitsio.FITS(args.catalogue) as infile:
        hdu = infile[1]

        ra1 = np.degrees(hdu['RA_1'][:])
        dec1 = np.degrees(hdu['DEC_1'][:])

        ra2 = hdu['ra_2'][:]
        dec2 = hdu['dec_2'][:]

        x = hdu['X_Coordinate'][:]
        y = hdu['Y_Coordinate'][:]


    centres = [2048 / 4, 2048 / 2, 3 * 2048 / 4]
    fig, axes = plt.subplots(3, 3, figsize=(11, 8))

    # Get the axes in the correct order
    axes = axes[::-1].T
    zipped = itertools.izip(
        itertools.product(centres, centres),
        axes.flatten())

    margin = 128
    for (x_centre, y_centre), axis in zipped:
        ind = ((x >= x_centre - margin) & (x <= x_centre + margin) &
               (y >= y_centre - margin) & (y <= y_centre + margin))

        axis.scatter(ra2[ind], dec2[ind], marker='o', edgecolor='b', color='None',
                    label='2MASS')
        axis.scatter(ra1[ind], dec1[ind], marker='s', edgecolor='r', color='None',
                    label='CASU')

        hide_labels(axis)

    padding = 0.5
    fig.tight_layout(h_pad=padding, w_pad=padding)
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
