#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from qa_common import get_logger
import csv
from collections import namedtuple
from multiprocessing import Pool
import os
from astropy.io import fits
import itertools

logger = get_logger(__file__)

psf_indices = list(range(1, 10))
psf_types = ['T', 'A', 'B']
psf_keys = ['psf_{typ}_{i}'.format(typ=typ,
                                   i=i)
            for (typ, i) in itertools.product(psf_types, psf_indices)]
all_keys = ['mjd'] + psf_keys
Extraction = namedtuple('Extraction', all_keys)


def extract(filename):
    with fits.open(filename) as infile:
        header = infile[1].header
        return Extraction(*[header[key] for key in all_keys])


def main(args):
    logger.info('Extracting psf data')
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
