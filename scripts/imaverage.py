#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fitsio
import numpy as np
import argparse
import sys
from qa_common import get_logger

def main(logger, args):
    logger.debug(args)
    nfiles = len(args.file)
    logger.info('Averaging {nfiles} files, take that iraf!'.format(
        nfiles=nfiles))

    first_file = args.file[0]
    image = fitsio.read(first_file)
    dimensions = image.shape
    logger.info("Constructing image of size {}x{}".format(*dimensions))

    with fitsio.FITS(args.output, 'rw', clobber=True) as outfile:
        outfile.write(np.zeros(dimensions, dtype=float))

        for fname in args.file:
            logger.debug('Analysing {}'.format(fname))
            data = fitsio.read(fname).astype(float)

            scaled_data = data / float(nfiles)
            logger.debug(scaled_data)

            new_total = outfile[0].read() + scaled_data
            outfile[0].write(new_total)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output file',
            type=str, required=True)
    parser.add_argument('file', nargs='+', type=str, help='Input file')
    args = parser.parse_args()

    logger = get_logger(__file__)
    main(logger, args)
