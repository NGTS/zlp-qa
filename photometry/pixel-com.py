#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Compute the pixel centre of mass
'''

import fitsio
import argparse
import numpy as np

from qa_common.plotting import plt
from qa_common import plot_night_breaks, get_logger

logger = get_logger(__file__)

def main(args):
    logger.info('Reading data from %s', args.fname)
    with fitsio.FITS(args.fname) as infile:
        ccdx = infile['ccdx'].read()
        ccdy = infile['ccdy'].read()
        mjd = infile['imagelist']['tmid'].read()

    mjd0 = int(mjd.min())
    mjd -= mjd0
    fn = np.median

    logger.info('Plotting')
    fig, axis = plt.subplots()
    mappable_x = axis.plot(mjd, fn(ccdx, axis=0), 'b.')[0]
    axis2 = axis.twinx()
    mappable_y = axis2.plot(mjd, fn(ccdy, axis=0), 'g.')[0]

    axis2.legend([mappable_x, mappable_y], ['X', 'Y'], loc='best')
    axis.set_ylabel(r'X')
    axis2.set_ylabel(r'Y')
    axis.set_xlabel('MJD - {}'.format(mjd0))

    plot_night_breaks(axis, mjd)

    fig.tight_layout()
    if args.output is not None:
        logger.info('Rendering to %s', args.output)
        fig.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    parser.add_argument('-o', '--output', required=False,
            type=argparse.FileType(mode='w'))
    main(parser.parse_args())
