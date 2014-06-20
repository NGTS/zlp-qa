#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
import logging
import fitsio
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing.pool import ThreadPool as Pool
import sys


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def sigma_clipped_mean(values, nsigma=3):
    median_value = np.median(values)
    limit = nsigma * np.std(values)

    ind = (values >= median_value - limit) & (values <= median_value + limit)
    return np.average(values[ind])


def extract_from_file(fname):
    logger.debug('Analysing {0}'.format(fname))
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

class NullPool(object):
    def __init__(self, *args, **kwargs):
        pass

    def map(self, fn, objects):
        return map(fn, objects)

def compute_limits(data, nsigma=3, precomputed_median=None):
    med = (precomputed_median if precomputed_median is not None
            else np.median(data))

    std = np.std(data)

    ll = med - nsigma * std
    ul = med + nsigma * std

    return ll, ul

def main(args):
    data = pd.read_table(args.extracted, sep=',')

    mjd0 = int(data.mjd.min())
    data['mjd'] = data['mjd'] - mjd0

    fig, axes = plt.subplots(5, 1, figsize=(11, 8), sharex=True)
    axes[0].plot(data.mjd, data.right - data.left, 'k.')
    axes[0].set_ylabel(r'Left - Right')
    axes[0].set_ylim(*compute_limits(data.right - data.left))

    axes[1].plot(data.mjd, data.left, 'r.', label='left')
    axes[1].plot(data.mjd, data.right, 'g.', label='right')
    axes[1].set_ylabel(r'Overscan level / counts')

    ll_left, ul_left = compute_limits(data.left)
    ll_right, ul_right = compute_limits(data.right)
    axes[1].set_ylim(min(ll_left, ll_right),
                     max(ul_left, ul_right))

    axes[2].plot(data.mjd, data.chstemp, 'r.')
    axes[2].set_ylabel(r'Chassis temp')
    axes[2].set_ylim(*compute_limits(data.chstemp))

    axes[3].plot(data.mjd, data.ccdtemp, 'r.')
    axes[3].set_ylabel(r'CCD temp')

    axes[4].plot(data.mjd, data.airmass, 'r.')
    axes[4].set_ylabel(r'Airmass')

    axes[-1].set_xlabel(r'MJD - {}'.format(mjd0))

    for ax in axes:
        ax.grid(True)

    fig.tight_layout()
    if args.output.strip() == '-':
        fig.savefig(sys.stdout, bbox_inches='tight')
    else:
        fig.savefig(args.output, bbox_inches='tight')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output image',
            required=True, type=str)
    parser.add_argument('extracted', type=str, help='Extracted data')
    main(parser.parse_args())

