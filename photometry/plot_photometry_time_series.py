#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fitsio
import argparse

from qa_common import plt

def main(args):
    with fitsio.FITS(args.filename) as infile:
        imagelist_hdu = infile['imagelist']
        mjd = imagelist_hdu['tmid'].read()
        fwhm = imagelist_hdu['fwhm'].read()
        seeing = imagelist_hdu['seeing'].read()
        clouds = imagelist_hdu['clouds'].read()

    mjd0 = int(mjd.min())
    mjd -= mjd0

    fig, axes = plt.subplots(3, 1, sharex=True)
    labels = ['FWHM / pixels', 'Seeing', 'Clouds']
    for ax, data, label in zip(axes, [fwhm, seeing, clouds], labels):
        ax.plot(mjd, data, marker='.', ls='None')
        ax.set_ylabel(label)
        ax.grid(True)

    axes[-1].set_xlabel(r'MJD - {}'.format(mjd0))

    fig.tight_layout()
    fig.savefig(args.output, bbox_inches='tight')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-o', '--output', required=True)
    main(parser.parse_args())

