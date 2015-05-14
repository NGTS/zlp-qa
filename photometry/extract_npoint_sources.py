#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
from multiprocessing import Pool
from collections import namedtuple
from astropy.io import fits
from qa_common import get_logger
import csv

Extraction = namedtuple('Extraction', ['mjd', 'nsources'])

logger = get_logger(__file__)


def extract(filename):
    with fits.open(filename) as infile:
        header = infile[0].header
        cat = infile[1].data

    nsources = len(cat)
    logger.debug('%s => %d', filename, nsources)
    return Extraction(header['mjd'], len(cat))


def main(args):
    logger.info('Extracting number of point sources')
    filenames = (os.path.realpath(line.strip()) for line in args.filelist)
    pool = Pool()
    results = pool.map(extract, filenames)
    results.sort(key=lambda row: row.mjd)

    logger.info('Rendering point source info to %s', args.output)
    writer = csv.DictWriter(args.output, fieldnames=Extraction._fields)
    writer.writeheader()
    for row in results:
        writer.writerow(dict(zip(Extraction._fields, row)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filelist', type=argparse.FileType(mode='r'))
    parser.add_argument('-o', '--output',
                        required=False,
                        type=argparse.FileType(mode='w'),
                        default='-')
    main(parser.parse_args())
