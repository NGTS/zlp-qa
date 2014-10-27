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
from plot_overscan_levels import sigma_clipped_mean, compute_limits


logger = get_logger(__file__)

def main(args):
    data = qa_common.CSVContainer(args.extracted)

    mjd0 = int(data.mjd.min())
    data['mjd'] = data.mjd - mjd0
    frames = np.arange(data.mjd.size)

    fig, axes = plt.subplots(6, 1, figsize=(11, 20), sharex=True)

    axes[0].plot(frames, data.dark, 'k.')
    axes[0].set_ylabel(r'Dark current / $\mathrm{e}^- s^{-1}$')
    axes[0].set_ylim(1, 7)

    axes[1].plot(frames, data.right - data.left, 'k.')
    axes[1].set_ylabel(r'Left - Right')
    axes[1].set_ylim(*compute_limits(data.right - data.left))

    axes[2].plot(frames, data.left, 'r.', label='left')
    axes[2].plot(frames, data.right, 'g.', label='right')
    axes[2].set_ylabel(r'Overscan level / counts')
    axes[2].set_ylim(*compute_limits(data.right))

    axes[3].plot(frames, data.chstemp, 'r.')
    axes[3].set_ylabel(r'Chassis temp')
    axes[3].set_ylim(*compute_limits(data.chstemp))

    axes[4].plot(frames, data.ccdtemp, 'r.')
    axes[4].set_ylabel(r'CCD temp')

    axes[5].plot(frames, data.airmass, 'r.')
    axes[5].set_ylabel(r'Airmass')

    axes[-1].set_xlabel('Frame')

    for ax in axes:
        ax.grid(True, axis='y')
        plot_night_breaks(ax, data.mjd)

    fig.tight_layout()
    if args.output.strip() == '-':
        fig.savefig(sys.stdout, bbox_inches='tight')
    else:
        fig.savefig(args.output, bbox_inches='tight')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output image',
            required=True, type=str)
    parser.add_argument('extracted', type=str, help='List of files')
    main(parser.parse_args())

