#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
import numpy as np
from multiprocessing.pool import ThreadPool as Pool
import csv
import re

from qa_common import get_logger
from qa_common.plotting import plt
from qa_common.util import NullPool
from pipeutils import open_fits_file


logger = get_logger(__file__)

overscan_regex = re.compile(r'\[(\d+):(\d+),(\d+):(\d+)\]')

def parse_overscan_region(region_txt):
    limits = map(int, overscan_regex.search(region_txt).groups())
    xmin, xmax, ymin, ymax = limits
    return (
        slice(xmin, xmax),
        slice(ymin, ymax)
    )

def sigma_clipped_mean(values, nsigma=3):
    median_value = np.median(values)
    limit = nsigma * np.std(values)

    ind = (values >= median_value - limit) & (values <= median_value + limit)
    return np.average(values[ind])


def extract_from_file(fname):
    logger.info('Analysing file %s', fname)
    with open_fits_file(fname) as infile:
        header = infile[0].header
        image = infile[0].data

    # sx, sy = parse_overscan_region(header['biassec'])

    mjd = header['mjd']
    left = image[4:, 1:20]
    right = image[4:, -15:]

    airmass = header.get('airmass', 0)
    chstemp = header.get('chstemp', 0)
    ccdtemp = header.get('ccdtemp', 0)
    image_id = header['image_id']

    return {
            'mjd': mjd,
            'image_id': image_id,
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
    files = [line.strip('\n') for line in args.filelist.readlines()]
    logger.info('Number of files: %s', len(files))

    pool = Pool()
    data = pool.map(extract_from_file, files)

    logger.info('Rendering output file to %s', args.output)
    writer = csv.DictWriter(args.output, fieldnames=data[0].keys())
    writer.writeheader()

    for row in data:
        writer.writerow(row)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output image',
            required=True, type=argparse.FileType(mode='w'))
    parser.add_argument('filelist', type=argparse.FileType(mode='r'),
            help='List of files')
    main(parser.parse_args())

