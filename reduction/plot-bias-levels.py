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
    left = image[:, :20]
    right = image[:, -20:]

    return {
            'mjd': mjd,
            'left': sigma_clipped_mean(left).astype(float),
            'right': sigma_clipped_mean(right).astype(float),
            }

def main(args):
    with open(args.filelist) as infile:
        files = [line.strip('\n') for line in infile.readlines()]
    logger.info("Analysing {0} files".format(len(files)))

    pool = Pool()
    data = pd.DataFrame(pool.map(extract_from_file, files)).sort('mjd')

    mjd0 = int(data.mjd.min())
    data['mjd'] = data['mjd'] - mjd0

    fig, axes = plt.subplots(figsize=(11, 8))
    axes.plot(data.mjd, data.left, 'r.', label='left')
    axes.plot(data.mjd, data.right, 'g.', label='right')

    axes.set_xlabel(r'MJD - {}'.format(mjd0))
    axes.set_ylabel(r'Overscan level / counts')

    fig.tight_layout()
    fig.savefig(args.output, bbox_inches='tight')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output image',
            required=True, type=str)
    parser.add_argument('filelist', type=str, help='List of files')
    main(parser.parse_args())

