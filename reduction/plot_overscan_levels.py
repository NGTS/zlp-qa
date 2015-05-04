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

logger = get_logger(__file__)

def sigma_clipped_mean(values, nsigma=3):
    median_value = np.median(values)
    limit = nsigma * np.std(values)

    ind = (values >= median_value - limit) & (values <= median_value + limit)
    return np.average(values[ind])


def extract_from_file(fname):
    logger.debug('Analysing file %s', fname)
    with fitsio.FITS(fname) as infile:
        header = infile[0].read_header()
        image = infile[0].read()

    mjd = header['mjd']
    left = image[:, 1:20]
    right = image[:, -20:]

    airmass = header['airmass']
    chstemp = header['chstemp']
    ccdtemp = header['ccdtemp']


    return {
            'mjd': mjd,
            'left': sigma_clipped_mean(left).astype(float),
            'right': sigma_clipped_mean(right).astype(float),
            'airmass': airmass,
            'ccdtemp': ccdtemp,
            'chstemp': chstemp,
            }

def compute_limits(data, nsigma=3, precomputed_median=None):
    med = (precomputed_median if precomputed_median is not None
            else np.median(data))

    std = np.std(data)

    ll = med - nsigma * std
    ul = med + nsigma * std

    return ll, ul

def main(args):
    logger.info('Reading data from %s', args.extracted)
    data = qa_common.CSVContainer(args.extracted)

    mjd0 = int(data.mjd.min())
    data['mjd'] = data['mjd'] - mjd0

    frames = np.arange(data.mjd.size)

    logger.info('Plotting')
    fig, axes = plt.subplots(6, 1, figsize=(11, 16), sharex=True)
    ind = data['exposure'] > 0.
    axes[0].semilogy(frames[ind], data['exposure'][ind], 'k.')
    axes[0].set_ylabel(r'Exposure time / s')
    axes[0].yaxis.set_major_formatter(plt.LogFormatter())

    axes[1].plot(frames, data.right - data.left, 'k.')
    axes[1].set_ylabel(r'Left - Right')
    axes[1].set_ylim(*compute_limits(data.right - data.left))

    axes[2].plot(frames, data.left, 'r.', label='left')
    axes[2].plot(frames, data.right, 'g.', label='right')
    axes[2].set_ylabel(r'Overscan level / counts')

    ll_left, ul_left = compute_limits(data.left)
    ll_right, ul_right = compute_limits(data.right)
    axes[2].set_ylim(min(ll_left, ll_right),
                     max(ul_left, ul_right))

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
            help='Extracted data')
    main(parser.parse_args())

