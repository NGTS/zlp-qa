#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
import fitsio
import numpy as np
from multiprocessing.pool import ThreadPool as Pool
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import qa_common
from qa_common import plot_night_breaks, get_logger
from qa_common.plotting import plt
from qa_common.util import NullPool
from plot_overscan_levels import sigma_clipped_mean


logger = get_logger(__file__)

def main(args):
    data = qa_common.CSVContainer(args.extracted)

    mjd0 = int(data.mjd.min())
    data['mjd'] = data.mjd - mjd0

    fig, axes = plt.subplots(6, 1, figsize=(11, 20), sharex=True)

    axes[0].plot(data['mjd'], data.dark, 'k.')
    axes[0].set_ylabel(r'Dark current / $\mathrm{e}^- s^{-1}$')
    axes[0].set_ylim(1, 7)

    axes[1].plot(data['mjd'], data.right - data.left, 'k.')
    axes[1].set_ylabel(r'Left - Right')

    axes[2].plot(data['mjd'], data.left, 'r.', label='left')
    axes[2].plot(data['mjd'], data.right, 'g.', label='right')
    axes[2].set_ylabel(r'Overscan level / counts')

    axes[3].plot(data['mjd'], data.chstemp, 'r.')
    axes[3].set_ylabel(r'Chassis temp')

    axes[4].plot(data['mjd'], data.ccdtemp, 'r.')
    axes[4].set_ylabel(r'CCD temp')

    axes[5].plot(data['mjd'], data.airmass, 'r.')
    axes[5].set_ylabel(r'Airmass')

    axes[-1].set_xlabel('MJD - {}'.format(mjd0))

    for ax in axes:
        ax.grid(True, axis='y')
        plot_night_breaks(ax, data.mjd)

    fig.tight_layout()

    if args.output is not None:
        logger.info('Rendering to %s', args.output)
        fig.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output image',
            required=False, type=argparse.FileType(mode='w'))
    parser.add_argument('extracted', type=argparse.FileType(mode='r'),
            help='List of files')
    main(parser.parse_args())

