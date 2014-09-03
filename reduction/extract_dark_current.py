#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
import logging
import fitsio
import numpy as np
from multiprocessing.pool import ThreadPool as Pool
import csv

from plot_overscan_levels import sigma_clipped_mean, NullPool, compute_limits


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def compute_bias_signal(image, left, right):
    x = np.arange(2048)
    gradient = (right - left) / 2048.

    y = gradient * x + left
    return y

def extract_from_file(fname):
    logger.info('Analysing {0}'.format(fname))
    with fitsio.FITS(fname) as infile:
        header = infile[0].read_header()
        image = infile[0].read()

    if not header['imgtype'].strip() == 'DARK':
        return None

    mjd = header['mjd']
    left = image[:, 1:20]
    right = image[:, -20:]

    gain = header['gainfact']
    exptime = header['exposure']

    left_overscan = sigma_clipped_mean(left)
    right_overscan = sigma_clipped_mean(right)

    airmass = header['airmass']
    chstemp = header['chstemp']
    ccdtemp = header['ccdtemp']

    logger.debug('Gain: {}'.format(gain))
    logger.debug('Exposure time: {}'.format(exptime))
    logger.debug('CCD temp: {}'.format(ccdtemp))

    central = image[:, 20:-20]
    bias_signal = compute_bias_signal(central, left_overscan, right_overscan)
    dark_current = central - bias_signal
    dark_current_electrons_per_second = dark_current * gain / exptime

    return {
            'mjd': mjd,
            'left': left_overscan.astype(float),
            'right': right_overscan.astype(float),
            'airmass': airmass,
            'ccdtemp': ccdtemp,
            'chstemp': chstemp,
            'dark': sigma_clipped_mean(dark_current).astype(float),
            }

def main(args):
    with open(args.filelist) as infile:
        files = [line.strip('\n') for line in infile.readlines()]
    logger.info("Analysing {0} files".format(len(files)))

    pool = NullPool()
    data = filter(None, pool.map(extract_from_file, files))

    with open(args.output, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=data[0].keys())
        writer.writeheader()

        for row in data:
            writer.writerow(row)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output image',
            required=True, type=str)
    parser.add_argument('filelist', type=str, help='List of files')
    main(parser.parse_args())

