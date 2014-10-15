#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy as np
import fitsio
from qa_common import plt
from qa_common import get_logger


def main(args):
    if not args.width % 2 == 0:
        raise RuntimeError("Width must be a multiple of 2")

    logger = get_logger('total_flat_adu')

    logger.debug('Reading data')
    with fitsio.FITS(args.filename) as infile:
        image_data = infile[0].read()

    logger.debug('Choosing region at %s,%s of width %s',
                 args.x, args.y, args.width)
    region = image_data[
        args.y - args.width / 2: args.y + args.width / 2,
        args.x - args.width / 2: args.x + args.width / 2
    ]

    med_region = np.median(region)
    std_region = np.std(region)
    logger.info('Region values - median: %s, std: %s',
                med_region, std_region)

    logger.info('Plotting')
    fig, axis = plt.subplots()
    colour_cycle = axis._get_lines.color_cycle
    axis.hist(region.flatten(), bins=args.nbins, histtype='step', normed=True)
    axis.axvline(med_region, color=next(colour_cycle))

    axis.set_xlabel(r'Total counts / ADU')
    axis.set_ylabel(r'Probability density')
    axis.set_title('Median: {:.1f}, std: {:.3f}'.format(
        med_region, std_region))

    fig.tight_layout()
    logger.debug('Saving image')
    fig.savefig(args.output)


if __name__ == '__main__':
    default_width = 256
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('--width',
                        help='Region width [default: {}]'.format(default_width),
                        default=default_width, required=False, type=int)
    parser.add_argument('--x', help='Region centre x [default: 1024]',
                        default=1024, required=False, type=int)
    parser.add_argument('--y', help='Region centre y [default: 1024]',
                        default=1024, required=False, type=int)
    parser.add_argument('--nbins', help='Number of histogram bins [default: 64]',
                        default=64, required=False, type=int)
    main(parser.parse_args())
