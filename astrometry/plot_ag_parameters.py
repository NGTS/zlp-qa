#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import
import argparse
from itertools import product, cycle
import logging
from astropy.io import fits
import numpy as np
from qa_common.plotting import plt, subplots

logging.basicConfig(
    level='INFO', format='%(levelname)7s %(message)s')
logger = logging.getLogger(__name__)


def main(args):
    if args.verbose:
        logger.setLevel('DEBUG')
    logger.debug(args)

    imagelist = fits.getdata(args.filename)

    colours = ['#d95f02', '#1b9e77']
    mjd = imagelist['tmid']
    mjd0 = int(mjd.min())
    mjd -= mjd0
    keys = ['ag_err', 'ag_corr', 'ag_delt']
    axes_labels = ['x', 'y']
    full_keys = (a + b for (a, b) in product(keys, axes_labels))
    with subplots(6, 1, sharex=True, figsize=(11, 11)) as (fig, axes):
        for (key, ax, colour) in zip(full_keys, axes, cycle(colours)):
            ax.plot(mjd, imagelist[key], '.', color=colour)
            ax.set_ylabel(key)
        axes[-1].set_xlabel(r'MJD - {}'.format(mjd0))

    fig.savefig(args.output, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output',
                        required=False,
                        type=argparse.FileType(mode='w'),
                        default='-')
    parser.add_argument('-v', '--verbose', action='store_true')
    main(parser.parse_args())
