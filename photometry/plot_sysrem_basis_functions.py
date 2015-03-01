#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import fitsio
import sys
import numpy as np
import argparse

from qa_common.plotting import plt


def main(args):
    with fitsio.FITS(args.filename) as infile:
        imagelist = infile['imagelist']
        coeffs = imagelist['aj'].read()
        mjd = imagelist['tmid'].read()

    n_coeffs = coeffs.shape[1]

    fig, axes = plt.subplots(n_coeffs, 1, sharex=True, figsize=(11, 8))

    frames = np.arange(mjd.size)

    for i, axis in enumerate(axes):
        data = coeffs[:, i]

        axis.plot(frames, data, 'k.', label="{}".format(i + 1))

        # Detect night boundaries
        d_mjd = np.diff(mjd)
        breaks = np.where(np.diff(mjd) > 0.3)[0]
        for b in breaks:
            axis.axvline(b, ls=':', color='k')

        axis.grid(True, axis='y')

        axis.set_ylabel(r'$a_{}$'.format(i))

    axes[-1].set_xlabel(r'Frame')

    fig.tight_layout()

    if args.output is not None:
        fig.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output', help='Output image',
                        required=False, type=argparse.FileType(mode='w'))
    main(parser.parse_args())


