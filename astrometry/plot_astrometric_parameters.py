#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import argparse
import matplotlib as mpl
mpl.rc('patch', edgecolor='None')
import matplotlib.pyplot as plt
import csv

class Extracted(object):
    def __init__(self, fname):
        with open(fname) as infile:
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



def main(args):
    e = Extracted(args.extracted)

    mjd = e.mjd
    mjd0 = int(mjd.min())
    mjd -= mjd0

    fig, axes = plt.subplots(5, 1, sharex=True, figsize=(11, 11))

    axes[0].plot(mjd, e.cmd_ra, marker='.', ls='None', label='cmd')
    axes[0].plot(mjd, e.tel_ra, marker='.', ls='None', label='tel')
    axes[0].plot(mjd, e.solved_ra, marker='.', ls='None', label='solved')
    axes[0].legend(loc='best')
    axes[0].set_ylabel(r'RA')

    axes[1].plot(mjd, e.cmd_dec, marker='.', ls='None', label='cmd')
    axes[1].plot(mjd, e.tel_dec, marker='.', ls='None', label='tel')
    axes[1].plot(mjd, e.solved_dec, marker='.', ls='None', label='solved')
    axes[1].legend(loc='best')
    axes[1].set_ylabel(r'DEC')

    axes[2].errorbar(mjd, e.skylevel, e.skynoise, ls='None', marker=',',
            color='cyan')
    axes[2].set_ylabel(r'Sky')

    axes[3].plot(mjd, e.numbrms, 'k.')
    axes[3].set_ylabel(r'numbrms')

    axes[4].plot(mjd, e.stdcrms, 'k.')
    axes[4].set_ylabel(r'stdcrms')

    axes[-1].set_xlabel(r'MJD - {}'.format(mjd0))

    for ax in axes:
        ax.grid(True)


    fig.tight_layout()
    fig.savefig(args.output, bbox_inches='tight')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('extracted', help='Input catalogue')
    parser.add_argument('-o', '--output', required=True,
            type=str, help='Output image name')
    main(parser.parse_args())
