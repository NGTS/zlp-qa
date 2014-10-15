#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
import fitsio
import numpy as np
from multiprocessing.pool import ThreadPool as Pool
import csv
import re

from qa_common import plt, get_logger


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
    logger.info('Analysing {0}'.format(fname))
    with fitsio.FITS(fname) as infile:
        header = infile[0].read_header()
        image = infile[0].read()

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
    with open(args.filelist) as infile:
        files = [line.strip('\n') for line in infile.readlines()]
    logger.info("Analysing {0} files".format(len(files)))

    pool = Pool()
    data = pool.map(extract_from_file, files)

    logger.info('Rendering to %s', args.output)
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

