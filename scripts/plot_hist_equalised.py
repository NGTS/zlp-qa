#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import fitsio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse
import os


def histogram_equalise(image, nbins=256):
    imhist, bins = np.histogram(image.flatten(), nbins, normed=True)
    cdf = imhist.cumsum()
    cdf = (nbins - 1) * cdf / cdf.max()

    im2 = np.interp(image.flatten(), bins[:-1], cdf).reshape(image.shape)

    return im2


def main(args):
    nbins = 256
    with fitsio.FITS(args.filename) as infile:
        image = infile[0].read()

    normalised = histogram_equalise(image, nbins=nbins)

    suffixes = ['.png', '_smoothed.png']
    interpolation_methods = ['none', 'gaussian']

    for (suffix, interpolation_method) in zip(suffixes, interpolation_methods):
        fig, axis = plt.subplots()
        mappable = axis.imshow(normalised, origin='lower', cmap=plt.cm.afmhot,
                               interpolation=interpolation_method)

        for dimension in ['xaxis', 'yaxis']:
            getattr(axis, dimension).set_visible(False)
        axis.set_title(os.path.basename(args.filename))
        fig.tight_layout()
        fig.savefig('{}{}'.format(args.stub, suffix), bbox_inches='tight')
        plt.close(fig)

if __name__ == '__main__':
    description = '''Plot an histogram equalised frame'''
    epilog = 'The output image is saved as <stub>.png and <stub>_smoothed.png'
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('filename')
    parser.add_argument('-s', '--stub', help='Stub output file', required=True)
    main(parser.parse_args())
