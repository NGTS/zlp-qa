#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import argparse
import csv
import sys

from qa_common.plotting import plt
from qa_common import plot_night_breaks, get_logger

logger = get_logger(__file__)

class Extracted(object):
    def __init__(self, infile):
        self.infile = infile
        reader = csv.DictReader(infile)
        self.data = [row for row in reader]
        keys = self.data[0].keys()

        for key in keys:
            try:
                setattr(self, key, np.array([float(row[key])
                    for row in self.data]))
            except ValueError:
                setattr(self, key, np.array([row[key]
                    for row in self.data]))

    @classmethod
    def from_file(cls, filename):
        with open(filename) as infile:
            return cls(filename)


def main(args):
    logger.info('Reading data from %s', args.extracted)
    e = Extracted(args.extracted)

    mjd = e.mjd
    mjd0 = int(mjd.min())
    mjd -= mjd0

    frames = np.arange(mjd.size)

    logger.info('Plotting')
    fig, axes = plt.subplots(5, 1, sharex=True, figsize=(11, 11))

    axes[0].plot(frames, e.cmd_ra, marker='.', ls='None', label='cmd')
    axes[0].plot(frames, e.tel_ra, marker='.', ls='None', label='tel')
    axes[0].plot(frames, e.solved_ra, marker='.', ls='None', label='solved')
    axes[0].legend(loc='best')
    axes[0].set_ylabel(r'RA')

    axes[1].plot(frames, e.cmd_dec, marker='.', ls='None', label='cmd')
    axes[1].plot(frames, e.tel_dec, marker='.', ls='None', label='tel')
    axes[1].plot(frames, e.solved_dec, marker='.', ls='None', label='solved')
    axes[1].legend(loc='best')
    axes[1].set_ylabel(r'DEC')

    axes[2].errorbar(frames, e.skylevel, e.skynoise, ls='None', marker=',',
            color='cyan')
    axes[2].set_ylabel(r'Sky')

    axes[3].plot(frames, e.numbrms, 'k.')
    axes[3].set_ylabel(r'numbrms')

    axes[4].plot(frames, e.stdcrms, 'k.')
    axes[4].set_ylabel(r'stdcrms')

    axes[-1].set_xlabel('Frame')

    for ax in axes:
        ax.grid(True, axis='y')
        plot_night_breaks(ax, mjd)


    fig.tight_layout()

    if args.output is not None:
        logger.info('Saving to %s', args.output)
        fig.savefig(args.output, bbox_inches='tight')
    else:
        plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('extracted', help='Input catalogue',
            type=argparse.FileType(mode='r'))
    parser.add_argument('-o', '--output', required=False,
            type=argparse.FileType(mode='w'), help='Output image name')
    main(parser.parse_args())

