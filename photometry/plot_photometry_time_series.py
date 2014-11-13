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
        fwhm = imagelist_hdu['fwhm'].read()
        seeing = imagelist_hdu['seeing'].read()
        clouds = imagelist_hdu['clouds'].read()

    mjd0 = int(mjd.min())
    mjd -= mjd0

    frames = np.arange(mjd.size)

    logger.info('Plotting')
    fig, axes = plt.subplots(3, 1, sharex=True)
    labels = ['FWHM / pixels', 'Seeing', 'Clouds']
    for ax, data, label in zip(axes, [fwhm, seeing, clouds], labels):
        ax.plot(frames, data, marker='.', ls='None')
        ax.set_ylabel(label)
        ax.grid(True, axis='y')
        plot_night_breaks(ax, mjd)

    axes[-1].set_xlabel('Frame')

    logger.info('Rendering to %s', args.output)
    fig.tight_layout()
    fig.savefig(args.output, bbox_inches='tight')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output', required=True)
    main(parser.parse_args())

