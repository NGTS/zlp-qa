#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fitsio
import argparse
import numpy as np

from qa_common.plotting import plt
from qa_common import plot_night_breaks, get_logger

logger = get_logger(__file__)

def main(args):
    logger.info('Reading data')
    with fitsio.FITS(args.filename) as infile:
        imagelist_hdu = infile['imagelist']
        mjd = imagelist_hdu['tmid'].read()
        seeing = imagelist_hdu['seeing'].read()
        frame_sn = imagelist_hdu['frame_sn'].read()

    mjd0 = int(mjd.min())
    mjd -= mjd0


    logger.info('Plotting')
    fig, axes = plt.subplots(2, 1, sharex=True)
    labels = ['"Seeing"', 'Frame S/N']
    for ax, data, label in zip(axes, [seeing, frame_sn], labels):
        ax.plot(mjd, data, marker='.', ls='None')
        ax.set_ylabel(label)
        ax.grid(True, axis='y')
        plot_night_breaks(ax, mjd)

    axes[-1].set_xlabel('MJD - {}'.format(mjd0))

    fig.tight_layout()
    if args.output is not None:
        logger.info('Rendering to %s', args.output)
        fig.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output', required=False,
            type=argparse.FileType(mode='w'))
    main(parser.parse_args())

