#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import fitsio
import numpy as np
import argparse
from collections import namedtuple
from scipy.stats import scoreatpercentile

from qa_common.filter_objects import good_measurement_indices
from qa_common.plotting import plt
from qa_common import get_logger

logger = get_logger(__file__)

summary = namedtuple('Summary', ['mjd', 'flux', 'breaks', 'lq', 'uq', 'std'])

def extract_flux_data(fname, chosen_exptime=None):
    logger.info("Extracting from %s", fname)
    with fitsio.FITS(fname) as infile:
        flux = infile['flux'].read()
        imagelist = infile['imagelist']
        airmass = imagelist['airmass'].read()
        exptime = imagelist['exposure'].read()
        mjd = imagelist['tmid'].read()

        ccdx = infile['ccdx'][:, :1].flatten()
        ccdy = infile['ccdy'][:, :1].flatten()

    logger.info('Normalising by exposure time')
    flux /= exptime

    per_ap_median = np.median(flux, axis=1)
    ind = (per_ap_median > 0)
    normalise_flux = ((flux[ind].T / per_ap_median[ind]) - 1.0).T
    assert normalise_flux.shape[1] == flux.shape[1], (normalise_flux.shape,
            flux.shape)

    med_flux = np.median(normalise_flux, axis=0)
    assert med_flux.size == mjd.size, (med_flux.size, mjd.size)

    breaks = np.where(np.diff(mjd) > 0.5)[0]

    lq, uq = scoreatpercentile(normalise_flux, [25, 75], axis=0)
    std = np.std(normalise_flux, axis=0) / np.sqrt(normalise_flux.shape[0])

    return summary(mjd, med_flux, breaks, lq, uq, std)


def plot_summary(s, colour, label, ax=None):
    ax = ax if ax else plt.gca()

    mjd0 = int(s.mjd.min())
    mjd = s.mjd - mjd0
    ax.plot(mjd, s.flux, ls='None', marker='.', color='k',
            label=label, zorder=2)
    lims = (ax.get_xlim(), ax.get_ylim())
    ax.errorbar(mjd, s.flux, s.std, ls='None', color=colour, alpha=0.5,
                zorder=1)
    ax.set_xlim(*lims[0])
    ax.set_ylim(*lims[1])


def plot_breaks(s, ax=None):
    ax = ax if ax else plt.gca()
    for b in s.breaks:
        ax.axvline(b, ls='--', color='k',
                zorder=-10)


def main(args):
    fig, ax = plt.subplots(figsize=(11, 8))

    if args.pre_sysrem:
        pre = extract_flux_data(args.pre_sysrem, args.exptime)
        plot_summary(pre, 'b', 'Pre', ax=ax)

    if args.post_sysrem:
        post = extract_flux_data(args.post_sysrem, args.exptime)
        plot_summary(post, 'r', 'Post', ax=ax)
        plot_breaks(post)

    ax.legend(loc='best')

    ax.axhline(0, ls='--', color='k')
    ax.axhline(-1E-3, ls=':', color='k')
    ax.axhline(1E-3, ls=':', color='k')

    ax.set_xlabel(r'$\Delta \mathrm{mjd}$')
    ax.set_ylabel(r'FRMS')

    fig.tight_layout()

    if args.output is not None:
        logger.info('Rendering to %s', args.output)
        fig.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=False,
            type=argparse.FileType(mode='w'), help='Output image name')
    parser.add_argument('--pre-sysrem', help='Input filename',
            type=str)
    parser.add_argument('--post-sysrem', help='Input filename',
            type=str)
    parser.add_argument('--exptime', help='Exposure time to filter out',
                        required=False, default=None, type=float)
    parser.add_argument('-n', '--nsigma', help='Sigma clip the output',
                        required=False, default=None, type=float)

    main(parser.parse_args())
