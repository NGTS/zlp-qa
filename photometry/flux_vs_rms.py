#!/usr/bin/env python
# -*- coding: utf-8 -*-


import fitsio
import numpy as np
import matplotlib.pyplot as plt
import argparse
from collections import namedtuple
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

summary = namedtuple('Summary', ['mags', 'frms'])

def extract_flux_data(fname, zp=21.18):
    with fitsio.FITS(fname) as infile:
        flux = infile['flux'].read()

    av_flux = np.average(flux, axis=1)
    std_flux = np.std(flux, axis=1)

    before_size = av_flux.size

    ind = ((av_flux > 0) &
            (std_flux > 0) &
            (av_flux == av_flux) &
            (std_flux == std_flux))
    av_flux, std_flux = [data[ind] for data in [av_flux, std_flux]]

    logger.info("Rejecting {} objects".format(before_size - av_flux.size))

    mags = zp - 2.5 * np.log10(av_flux)

    return summary(mags.astype(float), (std_flux / av_flux).astype(float))

def plot_summary(s, colour, label, ax=None):
    ax = ax if ax else plt.gca()

    ax.plot(s.mags, s.frms, ls='None', marker='.', color=colour,
            label=label)

def main(args):
    if args.pre_sysrem:
        pre = extract_flux_data(args.pre_sysrem)
    if args.post_sysrem:
        post = extract_flux_data(args.post_sysrem)

    fig, ax = plt.subplots(figsize=(11, 8))
    if args.pre_sysrem:
        plot_summary(pre, 'b', 'Pre', ax=ax)
    if args.post_sysrem:
        plot_summary(post, 'r', 'Post', ax=ax)
    ax.legend(loc='best')
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(plt.ScalarFormatter())

    ax.set_xlabel(r'Kepler magnitude')
    ax.set_ylabel(r'FRMS')
    ax.grid(True)
    ax.set_xlim(5, 20)
    ax.set_ylim(1E-3, 10)
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

    main(parser.parse_args())
