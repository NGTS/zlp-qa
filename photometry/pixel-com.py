#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Compute the pixel centre of mass
'''

import fitsio
import argparse
import numpy as np

from qa_common import plt, plot_night_breaks, get_logger

logger = get_logger(__file__)

def main(args):
    logger.info('Reading data', filename=args.fname)
    with fitsio.FITS(args.fname) as infile:
        ccdx = infile['ccdx'].read()
        ccdy = infile['ccdy'].read()
        mjd = infile['imagelist']['tmid'].read()

    frames = np.arange(mjd.size)

    fn = np.median

    logger.info('Plotting')
    fig, axis = plt.subplots()
    mappable_x = axis.plot(frames, fn(ccdx, axis=0), 'b.')[0]
    axis2 = axis.twinx()
    mappable_y = axis2.plot(frames, fn(ccdy, axis=0), 'g.')[0]

    axis2.legend([mappable_x, mappable_y], ['X', 'Y'], loc='best')
    axis.set_ylabel(r'X')
    axis2.set_ylabel(r'Y')
    axis.set_xlabel('Frame')

    plot_night_breaks(axis, mjd)

    logger.info('Rendering', filename=args.output)
    fig.tight_layout()
    fig.savefig(args.output, bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    parser.add_argument('-o', '--output', required=True, type=str)
    main(parser.parse_args())
