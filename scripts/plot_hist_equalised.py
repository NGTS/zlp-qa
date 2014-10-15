#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import fitsio
import argparse
import os

from qa_common import plt, get_logger

logger = get_logger(__file__)


def histogram_equalise(image, nbins=256):
    imhist, bins = np.histogram(image.flatten(), nbins, normed=True)
    cdf = imhist.cumsum()
    cdf = (nbins - 1) * cdf / cdf.max()

    im2 = np.interp(image.flatten(), bins[:-1], cdf).reshape(image.shape)

    return im2


def main(args):
    nbins = 256
    logger.debug('Using %s bins', nbins)
    logger.info('Reading data from %s', args.filename)
    with fitsio.FITS(args.filename) as infile:
        image = infile[0].read()

    logger.info('Normalising data')
    normalised = histogram_equalise(image, nbins=nbins)

    suffixes = ['.{}'.format(args.ext), '_smoothed.{}'.format(args.ext)]
    interpolation_methods = ['none', 'gaussian']

    for (suffix, interpolation_method) in zip(suffixes, interpolation_methods):
        output_filename = '{}{}'.format(args.stub, suffix)
        logger.info('Plotting to %s', output_filename)
        fig, axis = plt.subplots()
        mappable = axis.imshow(normalised, origin='lower', cmap=plt.cm.afmhot,
                               interpolation=interpolation_method)

        for dimension in ['xaxis', 'yaxis']:
            getattr(axis, dimension).set_visible(False)
        axis.set_title(os.path.basename(args.filename))
        fig.tight_layout()
        fig.savefig(output_filename, bbox_inches='tight')
        plt.close(fig)
        logger.debug('Image saved')

if __name__ == '__main__':
    description = '''Plot an histogram equalised frame'''
    epilog = '''The output image is saved as <stub>.<ext> and
 <stub>_smoothed.<ext>'''
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('filename')
    parser.add_argument('-s', '--stub', help='Stub output file', required=True)
    parser.add_argument('-e', '--ext', help='Extension [default: png]',
                        required=False, default='png')
    main(parser.parse_args())
