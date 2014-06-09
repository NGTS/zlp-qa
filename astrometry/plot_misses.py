#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fitsio
import matplotlib.pyplot as plt
import numpy as np
import argparse
import itertools
from collections import namedtuple
import csv

def missing_from_2mass(args):
    with fitsio.FITS(args.match) as infile:
        hdu = infile[1]

        matched_names = set(hdu['name_2mass'][:])

    with open(args.reference) as infile:
        reader = csv.DictReader(infile)
        data = [row for row in reader]

    for row in data:
        if row['name_2mass'] not in matched_names:
            yield row



def missing_from_casu(args):
    with fitsio.FITS(args.match) as infile:
        hdu = infile[1]

        matched_names = set(hdu['sequence_number'][:].astype(int))

    gain = 2.1
    exptime = 5.
    with fitsio.FITS(args.extracted) as infile:
        extracted_names = infile[1]['sequence_number'][:].astype(int)
        ra = np.degrees(infile[1]['ra'][:])
        dec = np.degrees(infile[1]['dec'][:])
        flux = infile[1]['aper_flux_3'][:] * gain / exptime
        mag = 21.18 - 2.5 * np.log10(flux)

    all_data = zip(extracted_names, ra, dec, flux, mag)

    for name, ra, dec, flux, mag in all_data:
        if int(name) not in matched_names:
            yield (name, ra, dec, flux, mag)

def main(args):
    fig, axes = plt.subplots(2, 1, figsize=(11, 11))
    m_casu = list(missing_from_casu(args))
    _, ra, dec, _, ngts_mag = zip(*m_casu)

    axes[1].plot(ra, dec, 'r.', zorder=10)

    m_2mass = missing_from_2mass(args)
    ra, dec, mag_2mass = [], [], []
    for row in m_2mass:
        ra.append(float(row['ra']))
        dec.append(float(row['dec']))
        mag_2mass.append(float(row['jmag']))

    height, xedges, yedges = np.histogram2d(ra, dec, bins=30)

    mappable = axes[1].pcolormesh(xedges[:-1], yedges[:-1], height.T,
                       cmap=plt.cm.binary, zorder=-10)
    fig.colorbar(mappable, ax=axes[1])

    axes[0].hist([ngts_mag, mag_2mass], bins=15, normed=True, histtype='step',
                 label=['ngts', '2mass'])
    axes[0].legend(loc='best')
    axes[1].set_aspect('equal')

    for ax in axes:
        ax.grid(True)

    axes[0].set_xlabel(r'Magnitude')
    axes[0].set_ylabel(r'Normalised density')
    axes[1].set_xlabel(r'$\alpha$')
    axes[1].set_ylabel(r'$\delta$')


    axes[0].set_title(r'CASU misses: {}, 2MASS misses: {}'.format(
        len(ngts_mag), len(mag_2mass)))

    fig.tight_layout()
    fig.savefig(args.output, bbox_inches='tight')
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', type=str, required=True)
    parser.add_argument('--extracted', type=str, required=True)
    parser.add_argument('--reference', type=str, required=True)
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    main(parser.parse_args())
