#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from qa_common.plotting import plt
from qa_common import get_logger
import csv
import numpy as np
import itertools
from functools import partial

logger = get_logger(__file__)

psf_indices = list(range(1, 10))
psf_types = ['T', 'A', 'B']
psf_keys = ['psf_{typ}_{i}'.format(typ=typ,
                                   i=i)
            for (typ, i) in itertools.product(psf_types, psf_indices)]

def eccentricity(a, b):
    return np.sqrt(1. - (b / a) ** 2)

def main(args):
    data = np.genfromtxt(args.data, delimiter=',', names=True)

    mjd = data['mjd']
    mjd0 = int(mjd.min())
    mjd -= mjd0

    fig, axes = plt.subplots(3, 1, sharex=True)

    centre_a = data['psf_A_5']
    centre_b = data['psf_B_5']
    centre_e = eccentricity(centre_a, centre_b)

    for corner_index in [1, 3, 7, 9]:
        a = data['psf_A_{}'.format(corner_index)]
        b = data['psf_B_{}'.format(corner_index)]
        ratio_a = a / centre_a
        ratio_b = b / centre_a

        e = eccentricity(a, b)
        ratio_e = e - centre_e

        axes[0].plot(mjd, ratio_a, '.')
        axes[1].plot(mjd, ratio_b, '.')
        axes[2].plot(mjd, ratio_e, '.')

    labels = [r'$A_{\mathrm{edge}} / A_{\mathrm{centre}}$',
            r'$B_{\mathrm{edge}} / B_{\mathrm{centre}}$',
            r'$e_{\mathrm{edge}} - e_{\mathrm{centre}}$']
    for ax, label in zip(axes, labels):
        ax.grid(True)
        ax.set_ylabel(label)

    fig.tight_layout()
    fig.savefig(args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data', type=argparse.FileType(mode='r'), default='-')
    parser.add_argument('-o', '--output',
                        required=False,
                        type=argparse.FileType(mode='w'),
                        default='-')
    main(parser.parse_args())
