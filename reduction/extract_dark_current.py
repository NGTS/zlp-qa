#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
import numpy as np
from multiprocessing.pool import ThreadPool as Pool
import csv

from qa_common import get_logger
from plot_overscan_levels import sigma_clipped_mean
from qa_common.util import NullPool
from pipeutils import open_fits_file


logger = get_logger(__file__)

def compute_bias_signal(image, left, right):
    x = np.arange(2048)
    gradient = (right - left) / 2048.

    y = gradient * x + left
    return y

def extract_from_file(fname):
    with open_fits_file(fname) as infile:
        header = infile[0].header
        image = infile[0].data

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

    logger.debug('Analysing file %s, gain: %s, exptime: %s, ccdtemp: %s',
                 fname, gain, exptime, ccdtemp)

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
    logger.info('Number of files: %s', len(files))

    pool = Pool()
    data = filter(None, pool.map(extract_from_file, files))

    writer = csv.DictWriter(args.output, fieldnames=data[0].keys())
    writer.writeheader()

    for row in data:
        writer.writerow(row)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output image',
            required=True, type=argparse.FileType(mode='w'))
    parser.add_argument('filelist', type=str, help='List of files')
    main(parser.parse_args())

