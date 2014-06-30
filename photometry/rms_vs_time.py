#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import fitsio
import numpy as np
import matplotlib.pyplot as plt
import argparse
from collections import namedtuple
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

summary = namedtuple('Summary', ['frames', 'flux', 'breaks'])

def extract_flux_data(fname, chosen_exptime=None):
    logger.info("Extracting from {}".format(fname))
    with fitsio.FITS(fname) as infile:
        mjd = infile['hjd'][0:1, :][0]
        flux = infile['flux'].read()
        imagelist = infile['imagelist']
        exptime = imagelist['exposure'].read()

    if chosen_exptime is not None:
        ind = exptime == chosen_exptime
        mjd = mjd[ind]
        flux = flux[:, ind]

    per_ap_median = np.median(flux, axis=1)
    ind = (per_ap_median > 0)
    normalise_flux = ((flux[ind].T / per_ap_median[ind]) - 1.0).T
    assert normalise_flux.shape[1] == flux.shape[1], (normalise_flux.shape,
            flux.shape)

    med_flux = np.median(normalise_flux, axis=0)
    assert med_flux.size == mjd.size, (med_flux.size, mjd.size)

    frames = np.arange(mjd.size)
    breaks = np.where(np.diff(mjd) > 0.5)[0]

    return summary(frames, med_flux, breaks)


def plot_summary(s, colour, label, ax=None):
    ax = ax if ax else plt.gca()

    ax.plot(s.frames, s.flux, ls='None', marker='.', color=colour,
            label=label)


def plot_breaks(s, ax=None):
    ax = ax if ax else plt.gca()
    for b in s.breaks:
        ax.axvline(b, ls='--', color='k',
                zorder=-10)

def compute_limits(data, nsigma=3, precomputed_median=None):
    med = (precomputed_median if precomputed_median is not None
            else np.median(data))

    std = np.std(data)

    ll = med - nsigma * std
    ul = med + nsigma * std

    return ll, ul

def main(args):
    fig, ax = plt.subplots(figsize=(11, 8))

    if args.pre_sysrem:
        pre = extract_flux_data(args.pre_sysrem)
        plot_summary(pre, 'b', 'Pre', ax=ax)

    if args.post_sysrem:
        post = extract_flux_data(args.post_sysrem)
        plot_summary(post, 'r', 'Post', ax=ax)
        plot_breaks(post)

    ax.legend(loc='best')

    ax.set_xlabel(r'MJD')
    ax.set_ylabel(r'FRMS')
    ax.grid(True)

    if args.pre_sysrem:
        ax.set_ylim(*compute_limits(pre.flux, nsigma=5))
    elif args.post_sysrem:
        ax.set_ylim(*compute_limits(post.flux, nsigma=5))

    fig.tight_layout()

    if args.output.strip() == '-':
        fig.savefig(sys.stdout, bbox_inches='tight')
    else:
        fig.savefig(args.output, bbox_inches='tight')
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    parser.add_argument('--pre-sysrem', help='Input filename',
            type=str)
    parser.add_argument('--post-sysrem', help='Input filename',
            type=str)
    parser.add_argument('--exptime', help='Exposure time to filter out',
                        required=False, default=None, type=float)

    main(parser.parse_args())
